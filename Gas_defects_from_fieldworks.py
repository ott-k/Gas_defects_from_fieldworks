# -*- coding: utf-8 -*-
#
# Author:
#
# Description: 


import arcpy
import os
import sys
import datetime
import shutil
import logging.config  # Has to be imported before agtools
logging.config.fileConfig('logging.conf',  # Has to be set before agtools
                          defaults={'date': datetime.datetime.now().strftime(
                              '%Y%m%d_%H%M%S')})  # For single run log file
log = logging.getLogger(__name__)  # Has to be set before agtools
import Gas_defects_from_fieldworks_config


cfg = Gas_defects_from_fieldworks_config.conf
arcpy.env.overwriteOutput = True
work_dir = cfg['work_dir']
gdb_sde = cfg['gdb_sde']
temp_fgdb_dir = os.path.join(work_dir, 'temp_fgdbs')
temp_fgdb = f'temp_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.gdb'
protection_zones = os.path.join(gdb_sde, cfg['protection_zones'])
defect_areas = cfg['defect_areas']
defect_areas_path = os.path.join(gdb_sde, cfg['defect_areas_path'])
defect_areas_protection_zones_clipped = os.path.join(
    temp_fgdb_dir,
    temp_fgdb,
    defect_areas + '_protection_zones_clipped')
cadastres = os.path.join(gdb_sde, cfg['kataster_elering'])
defect_areas_cadastres_split_temp = os.path.join(
    temp_fgdb_dir,
    temp_fgdb,
    defect_areas + '_cadastres_split')
defect_areas_cadastres_split = os.path.join(
    gdb_sde,
    cfg['defect_areas_cadastres_split'])


log.info('#' * 40 + ' Start of main ' + (39 - len(' Start main ')) * '#')
main_start_time = datetime.datetime.now()

log.info(f'Delete FGDBs from temporary folder {temp_fgdb_dir}')
deleted_count = 0
for folder in os.listdir(temp_fgdb_dir):
    try:
        log.info(f'Deleting FGDB {folder}')
        shutil.rmtree(os.path.join(temp_fgdb_dir, folder))
        deleted_count += 1
    except:
        log.info(f'Could not delete {folder}')
log.info(f'Deleted {deleted_count} FGDBs')

log.info(f'Create temporary FGDB {temp_fgdb}')
arcpy.management.CreateFileGDB(temp_fgdb_dir, temp_fgdb)

log.info(f'Clip {defect_areas_path} with {protection_zones}')
arcpy.analysis.PairwiseClip(
    defect_areas_path,
    protection_zones,
    defect_areas_protection_zones_clipped)

log.info(f'Split {defect_areas_protection_zones_clipped} with {cadastres}')
arcpy.analysis.PairwiseIntersect(
    in_features=f"{defect_areas_protection_zones_clipped};{cadastres}",
    out_feature_class=defect_areas_cadastres_split_temp,
    join_attributes="ALL",
    cluster_tolerance=None,
    output_type="INPUT"
)

if arcpy.Exists(defect_areas_cadastres_split):
    log.info(f'Truncating {defect_areas_cadastres_split}')
    arcpy.TruncateTable_management(defect_areas_cadastres_split)
    log.info(f'Appending {defect_areas_cadastres_split_temp} to {defect_areas_cadastres_split}')
    arcpy.Append_management(
        defect_areas_cadastres_split_temp,
        defect_areas_cadastres_split,
        'NO_TEST')
else:
    log.info(f'{defect_areas_cadastres_split} does not exist, coping to destination')
    arcpy.management.CopyFeatures(
        defect_areas_cadastres_split_temp,
        defect_areas_cadastres_split)

log.info(f'TEST')

log.info(f'Main run time {datetime.datetime.now() - main_start_time}')
log.info('#' * 40 + ' End of main ' + (39 - len(' End of main ')) * '#')
