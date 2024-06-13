#!/bin/bash


for i in `ls -d 9?????`;do
    cd $i
    echo "Working in $i"
    ldr=`ls *.02 | awk '{print substr(($1),6,length($1)-8)}'`
    img=`ls *.03 | awk '{print substr(($1),6,length($1)-8)}'`
    cp *.02 SARLEADER$ldr
    cp *.03 IMAGERY$img

    make_raw_jers.pl s SARLEADER$ldr $i
    cd ../
done
