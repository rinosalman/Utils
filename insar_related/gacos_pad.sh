#!/bin/bash

gacos_fold=../../gacos
cDir=`pwd`

#compute bounds
bounds=`gmt grdinfo -C intf/*/unwrap_mask_ll.grd |cut -f 2-5 |gmt gmtinfo -C | cut -f 1,4,5,8 |awk '{printf("-R%.12f/%.12f/%.12f/%.12f",$1,$2,$3,$4)}'`
inc=`gmt grdinfo intf/*/unwrap_mask_ll.grd -I | head -1`
echo "computed maximum exterior bounds for all files: $bounds"

#convert .ztd to .grd
cd $gacos_fold
for i in `ls *.ztd`;do
     
    #convert
    echo "Convert $i to $i.grd"
    M_LON_MIN=`cat $i.rsc | grep X_FIRST | awk '{print $2}'`
    M_LAT_MAX=`cat $i.rsc | grep Y_FIRST | awk '{print $2}'`
    M_WIDTH=`cat $i.rsc | grep WIDTH | awk '{print $2}'`
    M_LENGTH=`cat $i.rsc | grep FILE_LENGTH | awk '{print $2}'`
    M_X_STEP=`cat $i.rsc | grep X_STEP | awk '{print $2}'`
    M_Y_STEP=`cat $i.rsc | grep X_STEP | awk '{print $2}'`
    gmt xyz2grd $i -G$i.grd -RLT$M_LON_MIN/$M_LAT_MAX/$M_WIDTH/$M_LENGTH -I$M_X_STEP/$M_Y_STEP -di0 -ZTLf

    #padding
    echo "Padding $i.grd"
    gmt grd2xyz $i.grd -bo | gmt xyz2grd -bi $bounds $inc -r -Gtemp_$i
    nccopy -k classic temp_$i $i"_pad.grd"
    rm temp_$i

done
cd $cDir
