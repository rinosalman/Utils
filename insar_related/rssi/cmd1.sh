#!/bin/bash
# July 2023, Rino Salman, EOS-NTU

# necessary parameters
cDir=`pwd`
ref_date=220905
sec_date=230220
idir=../../../../dates_resampled/
look_code=/home/share/miniconda3/envs/isce2_v2.6.1_MP/share/isce2/alosStack/look_coherence.py
filt_code=/home/share/miniconda3/envs/isce2_v2.6.1_MP/share/isce2/alosStack/filt.py
unwrap_code=/home/share/miniconda3/envs/isce2_v2.6.1_MP/share/isce2/alosStack/unwrap_snaphu.py

# multilook, filter and unwrap interferograms
cd ../lower
$look_code -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 
$filt_code -idir $idir -ref_date_stack ${ref_date} -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 -alpha 0.75 -win 64 -step 4
cp ../../${ref_date}.track.xml .
$unwrap_code -idir $idir -ref_date_stack ${ref_date} -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 -wbd_msk

cd ../upper
$look_code -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 
$filt_code -idir $idir -ref_date_stack ${ref_date} -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 -alpha 0.75 -win 64 -step 4
cp ../../${ref_date}.track.xml .
$unwrap_code -idir $idir -ref_date_stack ${ref_date} -ref_date ${ref_date} -sec_date ${sec_date} -nrlks1 1 -nalks1 14 -nrlks2 5 -nalks2 2 -wbd_msk

cd $cDir
