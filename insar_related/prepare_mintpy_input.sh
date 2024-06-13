#!/bin/bash

#make directory
mkdir -p pairs dates_resampled

#copying baseline file
#cp -r ../../baseline .

#copying metafile and interferogram datasets
refdate=150401
cd pairs
for i in `ls -d ../../../pairs/*`;do
    dir=`echo $i | awk -F/ '{print $5}'`
    mkdir $dir
    cp $i/$refdate'.track.xml' $dir/
    mkdir -p $dir/insar
    cp $i/insar/filt*_5rlks_28alks.unw $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.rsc $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.vrt $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.xml $dir/insar/
    cp $i/insar/*_5rlks_28alks.cor $dir/insar/
    cp $i/insar/*_5rlks_28alks.cor.vrt $dir/insar/
    cp $i/insar/*_5rlks_28alks.cor.xml $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.conncomp $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.conncomp.vrt $dir/insar/
    cp $i/insar/filt*_5rlks_28alks.unw.conncomp.xml $dir/insar/
done
cd ../


#copying geometry datasets
cd dates_resampled
mkdir -p $refdate/insar
cp ../../../dates_resampled/$refdate/insar/*_5rlks_28alks.hgt* $refdate/insar
cp ../../../dates_resampled/$refdate/insar/*_5rlks_28alks.lat* $refdate/insar
cp ../../../dates_resampled/$refdate/insar/*_5rlks_28alks.lon* $refdate/insar
cp ../../../dates_resampled/$refdate/insar/*_5rlks_28alks.los* $refdate/insar
cp ../../../dates_resampled/$refdate/insar/*_5rlks_28alks.wbd* $refdate/insar
cd ../
