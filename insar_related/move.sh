#!/bin/bash

cd bad_intfs
for i in `ls -d 20*/imag.grd`;do
   folder=`echo $i | awk '{print substr($1,1,15)}'`
   echo $folder >> moved_folder
   mv $folder ../intf
done
cd ../
