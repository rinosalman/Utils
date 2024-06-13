#cut areas affected by Mw 6.5 earthquake
R="-R95.6111111111/96.3555555556/4.12222222222/5.07666666667"
cd intf
for i in `ls -d *`;do
	cd $i
	gmt grdcut unwrap_mask_ll_pad.grd $R -Gunwrap_mask_ll_pad_cut.grd
	cd ../
done
cd ../
