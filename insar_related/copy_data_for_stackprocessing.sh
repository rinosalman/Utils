#!/bin/bash


dataFolder='/home/data/INSAR/ALOS2/P035/F3650'
cDir=`pwd`
for i in `ls $dataFolder/LED*`;do
    date=`echo $i | awk -F/ '{print $8}' | awk -F- '{print $3}'`
    mkdir -p data/$date
    cd data/$date
    ln -s $i .
    ln -s $dataFolder/IMG-HH*$date* .
    cd $cDir
done
