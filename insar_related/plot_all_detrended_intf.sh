# fault segments
segmentpath=/home/data/INSAR_processing/ALOS-2/sumatran_fault/fault_segments
tripa=$segmentpath/tripe_segment.kml.gmt
aceh=$segmentpath/aceh_segment.kml.gmt
seulimum=$segmentpath/seulimum_segment.kml.gmt
batee=$segmentpath/batee_segment.kml.gmt

grd=los_ll.grd
trend=los_trend.grd
grddetrended=los_ll_detrended.grd
cpt=gmtcpt.cpt
psFile=los_ll_detrended.ps
pdfFile=los_ll_detrended.pdf

cd intf
for i in `ls -d *`;do

	cd $i

	# estimate trend
	gmt grdtrend $grd -N3r -T$trend -R$grd

	# subtract the trend
	gmt grdmath $grd $trend SUB = $grddetrended

	# make a cpt file
	gmt makecpt -Crainbow -T-200/200/10 -D -Z > $cpt

	# plot
	gmt grdimage $grddetrended -C$cpt -JM5i -R$grddetrended -K -P -Xc -Yc > $psFile

	# plot fault segments
	gmt psxy $tripa -R -J -W4,yellow -O -K >> $psFile
	gmt psxy $aceh -R -J -W4,black -O -K >> $psFile
	gmt psxy $batee -R -J -W4,purple -O -K >> $psFile
	gmt psxy $seulimum -R -J -W4,orange -O -K >> $psFile

	# plot scale
	gmt psscale -D2.3i/-0.32i/2.0i/0.08ih -C$cpt -Ba100/f50:"mm/yr": -K -O >> $psFile

	# convert to pdf
	ps2pdf $psFile $pdfFile

	cd ../

done
cd ../
