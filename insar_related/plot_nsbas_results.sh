#!/bin/bash
# fault segments
segmentpath=/home/data/INSAR_processing/ALOS-2/sumatran_fault/fault_segments
tripa=$segmentpath/tripe_segment.kml.gmt
aceh=$segmentpath/aceh_segment.kml.gmt
seulimum=$segmentpath/seulimum_segment.kml.gmt
batee=$segmentpath/batee_segment.kml.gmt

# input files/parameters
#grd=rate_detrended.grd
grd=rate.grd

# transect points
t1lon1=95.473
t1lat1=5.046
t1lon2=95.781
t1lat2=5.492
t2lon1=95.291
t2lat1=5.249
t2lon2=95.503
t2lat2=5.567
t3lon1=95.941
t3lat1=4.410
t3lon2=96.254
t3lat2=4.942
xo=96.592
yo=4.417

# output files
psFile=rate.ps
transect1dat=transect1.dat
transect2dat=transect2.dat
transect3dat=transect3.dat
transect1ps=transect1.ps
transect2ps=transect2.ps
transect3ps=transect3.ps
cpt=cptFile.cpt

# GMT variables
wleft=-2
wright=2
ytop=40
ybottom=-40
xleft=-60
xright=60
proj=M4i
border=a0.5f0.25/a0.5f0.25WseN

# GMT defaults
gmt gmtset FONT_LABEL 15
gmt gmtset FONT_TITLE 15
gmt gmtset MAP_FRAME_WIDTH 1.06
gmt gmtset MAP_FRAME_PEN 1.50p
gmt gmtset FONT_LABEL Helvetica
gmt gmtset MAP_ORIGIN_X 1i
gmt gmtset MAP_ORIGIN_Y 1i
gmt gmtset MAP_FRAME_TYPE plain
gmt gmtset MAP_TICK_LENGTH_PRIMARY 0.15c
gmt gmtset MAP_TICK_LENGTH_SECONDARY 0.15c
gmt gmtset MAP_ANNOT_OFFSET_PRIMARY 0.15i
gmt gmtset MAP_TITLE_OFFSET 0.1i
gmt gmtset FORMAT_GEO_MAP D
gmt gmtset FONT_ANNOT_PRIMARY 15

# make a cpt file
gmt makecpt -Crainbow -T-20/20/0.1 -D -Z > $cpt

# plot coastlines
gmt pscoast -Df -R$grd -J$proj -Swhite -B$border -Wthinnest -Xc -Yc -P -K > $psFile

# plot rate.grd
gmt grdimage rate.grd -C$cpt -J -R -O -K >> $psFile

# plot fault segments
gmt psxy $tripa -R -J -W4,yellow -O -K >> $psFile
gmt psxy $aceh -R -J -W4,black -O -K >> $psFile
gmt psxy $batee -R -J -W4,purple -O -K >> $psFile
gmt psxy $seulimum -R -J -W4,orange -O -K >> $psFile

# plot coastlines
gmt pscoast -Df -R$grd -J$proj -Swhite -B$border -Wthinnest -K -O >> $psFile

# plot transect line
echo -e $t1lon1 $t1lat1\\n$t1lon2 $t1lat2 | gmt psxy -R -J -W2 -Wblack -K -O >> $psFile
echo -e $t2lon1 $t2lat1\\n$t2lon2 $t2lat2 | gmt psxy -R -J -W2 -Wblack -K -O >> $psFile
#echo -e $t3lon1 $t3lat1\\n$t3lon2 $t3lat2 | gmt psxy -R -J -W2 -Wblack -K -O >> $psFile

# plot scale
gmt psscale -D2.1i/-0.39i/2.0i/0.08ih -C$cpt -Ba10/f5:"mm/yr": -K -O >> $psFile

# plot legend for distance
gmt pscoast -Df -R -J -Swhite -Lf95.30/4.65/0/20+l+jt -Wthinnest -K -O >> $psFile

# plot text
echo $t1lon1 $t1lat1 14 0 1 LT A > text
echo $t1lon2 $t1lat2 14 0 1 LT B >> text
gmt pstext text -J -R -O -K >> $psFile


# plot text
echo $t2lon1 $t2lat1 14 0 1 LT C > text
echo $t2lon2 $t2lat2 14 0 1 LT D >> text
gmt pstext text -J -R -O -K >> $psFile

# grab points for cross section
gmt grd2xyz $grd -s | gmt project -C$t1lon1/$t1lat1 -E$t1lon2/$t1lat2 -Q -W$wleft/$wright -Fpz > $transect1dat
gmt grd2xyz $grd -s | gmt project -C$t2lon1/$t2lat1 -E$t2lon2/$t2lat2 -Q -W$wleft/$wright -Fpz > $transect2dat
#gmt grd2xyz $grd -s | gmt project -C$t3lon1/$t3lat1 -E$t3lon2/$t3lat2 -Q -W$wleft/$wright -Fpz > $transect3dat

# plot cross section 1
cat $transect1dat | awk '{print $1-26,$2}' | gmt psxy -JX6i/3i -R$xleft/$xright/$ybottom/$ytop -P -Sc0.1c -Gblack -Ba50f10:"Distance from fault (km)":/:"Fault-parallel velocity (mm/yr)":20WSne -Xc -Y3 -K > $transect1ps

# draw fault line
echo -e -0 -50\\n0 50 | gmt psxy -R -J -Wfat,black,-. -O -K >> $transect1ps
echo -e 16 -50\\n16 50 | gmt psxy -R -J -Wfat,orange,-. -O -K >> $transect1ps

# plot text
echo -62 46 14 0 1 LT A > text
echo 58 46 14 0 1 LT B >> text
gmt pstext text -J -R -O -K -N >> $transect1ps

# plot cross section 2
cat $transect2dat | awk '{print $1-23,$2}' | gmt psxy -JX6i/3i -R$xleft/$xright/$ybottom/$ytop -P -Sc0.1c -Gblack -Ba50f10:"Distance from fault (km)":/:"Fault-parallel velocity (mm/yr)":20WSne -Xc -Y11 -O -K >> $transect1ps

# draw fault line
echo -e 0 -50\\n0 50 | gmt psxy -R -J -W3,black,-. -O -K >> $transect1ps

# plot text
echo -62 46 14 0 1 LT C > text
echo 58 46 14 0 1 LT D >> text
gmt pstext text -J -R -O -K -N >> $transect1ps

#cat $transect3dat | awk '{print $1,$2}' | gmt psxy -JX6i/3i -R$xleft/$xright/$ybottom/$ytop -P -Sc0.1c -Gblack -Ba50f10:"Distance from fault (km)":/:"Fault-parallel velocity (mm/yr)":20WSne -Xc -Yc > $transect3ps


# open
#gs rate.ps &
#gs rate_transect.ps &
