#!/bin/bash

#resample to common grid
#qsub -v sec_date=150226 pbs_1b.pbs

#mosaic
/home/share/miniconda3/envs/isce2_v2.6.3/share/isce2/alosStack/mosaic_parameter.py -idir dates_resampled -ref_date 150226 -sec_date 150226 -nrlks1 1 -nalks1 14

# compute latitude, longtitude and height
dem1=/home/data/INSAR_processing/indo_sub/p32/dem1/demLat_S08_S05_Lon_E105_E109.dem.wgs84
wbd1=/home/data/INSAR_processing/indo_sub/p32/wbd1/swbdLat_S08_S05_Lon_E105_E109.wbd
cd dates_resampled/150226
/home/share/miniconda3/envs/isce2_v2.6.3/share/isce2/alosStack/rdr2geo.py -date 150226 -dem $dem1 -wbd $wbd1 -nrlks1 1 -nalks1 14
cd ../../

# estimate residual offsets between radar and DEM
code=/home/share/miniconda3/envs/isce2_v2.6.3/share/isce2/alosStack/radar_dem_offset.py
track=150226.track.xml
wbd=insar/150226_1rlks_14alks.wbd
hgt=insar/150226_1rlks_14alks.hgt
amp=../../pairs/150226-150407/insar/150226-150407_1rlks_14alks.amp
numberRangeLooks1=1
numberAzimuthLooks1=14
cd dates_resampled/150226
$code -track $track -dem $dem -wbd $wbd -hgt $hgt -amp $amp -output affine_transform.txt -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1
cd ../../

# look geom
code=/home/share/miniconda3/envs/isce2_v2.6.3/share/isce2/alosStack/look_geom.py
ref_date_stack=150226
numberRangeLooks1=1
numberAzimuthLooks1=14
numberRangeLooks2=10
numberAzimuthLooks2=4
cd dates_resampled/$ref_date_stack
$code -date $ref_date_stack -wbd $wbd1 -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 -nrlks2 $numberRangeLooks2 -nalks2 $numberAzimuthLooks2
cd ../../
