#!/bin/bash

for i in `ls LED*`;do
    id=`echo $i | awk -F- '{print $2}'`
    path=`grep -a Sci_ObservationPathNo $i | grep -oP '"\K.*(?=")'`
    frame=`grep -a Sci_FrameCenterNo $i | grep -oP '"\K.*(?=")'`
    date=`grep -a Img_SceneCenterDateTime $i | grep -oP '"\K.*(?=")' | awk '{print $1}'`
    mkdir -p P$path/F$frame/$date/$id
    mv *$id* P$path/F$frame/$date/$id/
done
