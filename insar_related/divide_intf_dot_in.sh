#!/bin/bash
#divide number of interferograms to be processed into maximum processors number
  
proc=32
n=0

for i in {1..26};do

    #intf.in?
    bef=`echo $proc | awk -v ii=$n '{print ($1*ii)+1}'`
    aft=`echo $proc | awk -v ii=$i '{print $1*ii}'`
    sed -n "$bef,$aft p" intf.in > intf.in$i
    #echo $bef,$aft,$i
    let n=n+1

    #batch.config?
    #edit intf_file
    sed "43s/intf_file =/intf_file = intf.in$i/" batch.config > temp
    #edit treshold value for unwrapping
    sed "189s/threshold_snaphu =/threshold_snaphu = 0.10/" temp > temp2
    #edit treshold value for geocode
    sed "216s/threshold_geocode =/threshold_snaphu = 0.10/" temp2 > batch.config$i
    
done





