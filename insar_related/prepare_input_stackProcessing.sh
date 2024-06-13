#!/bin/bash

#1. Copy data
dataFolder='/home/data/INSAR/ALOS2/P036/F3650'
cDir=`pwd`
for i in `ls $dataFolder/LED*`;do
    date=`echo $i | awk -F/ '{print $8}' | awk -F- '{print $3}'`
    mkdir -p data/$date
    cd data/$date
    ln -s $i .
    ln -s $dataFolder/IMG-HH*$date* .
    cd $cDir
done


#2. Copy alosStack.xml
#cp /home/data/INSAR_processing/sumatra/ALOS2/P034/F3700/stack/alosStack.xml .
#cp /home/data/INSAR_processing/sumatra/ALOS2/P035/F3650/stack/*.py .


#3. Create command files for processing data
#${PATH_ALOSSTACK}/create_cmds.py -stack_par alosStack.xml
