#!/bin/bash

path=/home/data/INSAR/JERS1/ORD2023030531930

for i in `ls $path/J1*.zip`;do
    date=`echo $i | awk -F/ '{print $7}' | awk '{print substr(($1),6,length($1)-33)}'`
    echo $i
    file=$(basename "$i" .zip)
    echo $date
    mkdir $date
    rsync -avz $path/$file.?? $date/ &
done
