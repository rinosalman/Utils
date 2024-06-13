#!/bin/bash
# July 2023, Rino Salman, EOS-NTU

# necessary parameters
cDir=`pwd`
ref_date=220905
sec_date=230220
idir=/home/data/INSAR_processing/turkey/P184/F0700-F7050/alosstack/dates_resampled
unwrap_code=/home/share/miniconda3/envs/isce2_v2.6.1_MP/share/isce2/alosStack/unwrap_snaphu.py
geocode_code=/home/share/miniconda3/envs/isce2_v2.6.1_MP/share/isce2/alosStack/geocode.py
dem=/home/data/INSAR_processing/turkey/P184/F0700-F7050/dem_3_arcsec/demLat_N33_N40_Lon_E034_E040.dem.wgs84
mskunw=filt_${ref_date}-${sec_date}_5rlks_28alks_msk.unw

