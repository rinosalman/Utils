#!/bin/bash

for wdir in `ls -d 20*`;do
#wdir=psize16_2017094_2017178

	cd $wdir
	losgrdin=los_ll.grd
	lostrend=los_ll_trend.grd
	losgrdout=los_ll_det.grd
	losdetcpt=los_ll_det.cpt

	# estimate trend
	grdtrend $losgrdin -N3r -T$lostrend -R$losgrdin
	grdmath $losgrdin $lostrend SUB = $losgrdout

	# make cpt
	tmp=`gmt grdinfo -C -L2 $losgrdout`
	limitU=`echo $tmp | awk '{printf("%5.1f", $12+$13*2)}'`
	limitL=`echo $tmp | awk '{printf("%5.1f", $12-$13*2)}'`
	makecpt -Cpolar -Z -T"$limitL"/"$limitU"/1 -D > $losdetcpt

	# geocode
	grd2kml.csh los_ll_det $losdetcpt

	cd ../

done
