#!/bin/bash
#plot baselines based on 20* folders inside intf

echo "#masterID masterYDOY masterX masterBSL slaveID slaveYDOY slaveX slaveBSL" > baseline_intf.txt
for i in `ls -d intf/20*`;do

	#master
	mst_clock=`grep SC_clock_start $i/*.PRM | head -1 | awk '{print $3}'`
	mst_id=`grep $mst_clock raw/baseline_table.dat | awk '{print substr($1,13,length($1)-34)}'`
	mst_ydoy=`grep $mst_clock raw/baseline_table.dat | awk '{printf ("%d",int($2))}'`
	mst_x=`grep $mst_clock raw/baseline_table.dat | awk '{print ($3/365.25)+2014.5}'`
	mst_bsl=`grep $mst_clock raw/baseline_table.dat | awk '{print $5}'`

	#slave
	slv_clock=`grep SC_clock_start $i/*.PRM | tail -1 | awk '{print $3}'`
	slv_id=`grep $slv_clock raw/baseline_table.dat | awk '{print substr($1,13,length($1)-34)}'`
	slv_ydoy=`grep $slv_clock raw/baseline_table.dat | awk '{printf ("%d",int($2))}'`
	slv_x=`grep $slv_clock raw/baseline_table.dat | awk '{print ($3/365.25)+2014.5}'`
	slv_bsl=`grep $slv_clock raw/baseline_table.dat | awk '{print $5}'`

	#save
        echo "$mst_id $mst_ydoy $mst_x $mst_bsl $slv_id $slv_ydoy $slv_x $slv_bsl" >> baseline_intf.txt
done

#grab location and texts
grep -v "#" baseline_intf.txt | awk '{print $3,$4,$1}' > text
grep -v "#" baseline_intf.txt | awk '{print $7,$8,$5}' >> text
awk '!seen[$0]++' text > text2

#plot
psFile=baseline_intf.ps
grep -v "#" baseline_intf.txt | awk '{print $3,$4}' > point
grep -v "#" baseline_intf.txt | awk '{print $7,$8}' >> point
awk '!seen[$0]++' point > point2
#gmt pstext text2 -JX8.8i/6.8i -R2015/2021.5/-350/450 -D0.2/0.2 -Xc -Yc -K -F+f10,Helvetica+j5 > $psFile
#gmt psxy -JX8.8i/6.8i -R2015/2021.5/-350/450 -Xc -Yc -K > $psFile
gmt psxy point2 -JX8.8i/6.8i -R2015/2021.5/-350/450 -Sp0.2c -G0 -Ba1.0g0.5:"year":/a100g100f100:"baseline (m)":WSen -K -Xc -Yc > $psFile
while IFS= read -r line;do
	echo "$line" | awk '{print $3,$4}' >> tmp
	echo "$line" | awk '{print $7,$8}' >> tmp
	gmt psxy tmp -R -J -Wthinnest,darkgreen -K -O >> $psFile
	rm tmp
done < "baseline_intf.txt"
gmt psxy point2 -J -R -Sp0.2c -G0 -O -K >> $psFile
gmt pstext text2 -J -R -K -O -D0.2/0.2 -F+f10,Helvetica+j5 >> $psFile
rm text text2 point point2


#grab location and texts
grep -v "#" baseline_intf.txt | awk '{print $3,$4,$2}' > text
grep -v "#" baseline_intf.txt | awk '{print $7,$8,$6}' >> text
awk '!seen[$0]++' text > text2

psFile2=baseline_intf2.ps
grep -v "#" baseline_intf.txt | awk '{print $3,$4}' > point
grep -v "#" baseline_intf.txt | awk '{print $7,$8}' >> point
awk '!seen[$0]++' point > point2
gmt psxy point2 -JX8.8i/6.8i -R2015/2021.5/-350/450 -Sp0.2c -G0 -Ba1.0g0.5:"year":/a100g100f100:"baseline (m)":WSen -Xc -Yc -K > $psFile2
while IFS= read -r line;do
	echo "$line" | awk '{print $3,$4}' >> tmp
	echo "$line" | awk '{print $7,$8}' >> tmp
	gmt psxy tmp -R -J -Wthinnest,darkgreen -K -O >> $psFile2
	rm tmp
done < "baseline_intf.txt"
gmt psxy point2 -J -R -Sp0.2c -G0 -O -K >> $psFile2
gmt pstext text2 -J -R -K -O -D0.2/0.2 -F+f10,Helvetica+j5 >> $psFile2
rm text text2 point point2
