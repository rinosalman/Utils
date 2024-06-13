#!/bin/bash
#used to isolate pairs that show error in stackStripMap processing with run01-run08

for i in {1..9};do
    inp=`cat errorpairs | awk -v row=$i 'NR==row{print $0}'` 
    ref=`cat $inp | awk 'NR==2{print $4}' | awk -F/ '{print $10}'`
    rep=`cat $inp | awk 'NR==1{print $4}' | awk -F/ '{print $10}'`
    echo $ref"_"$rep
done
