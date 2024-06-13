#!/bin/csh -f
#
# create LOS vector grid files: look_e.grd look_n.grd look_u.grd
# also create lltenud ascii file at full resolution, or at a subsampled resolution
#
# converted from make_los_ascii.csh, E. Lindsey, August 2017
#
if ($#argv < 3 || $#argv > 4) then
  echo ""
  echo "Usage: make_los_products.csh los_ll.grd PRMfile SAT [-Ix/y]"
  echo ""
  echo "SAT = ERS, ENVI, ALOS, ALOS2, TSX, S1, or generic SAT"
  echo ""
  echo "  Example: make_los_products.csh los_ll.grd IMG-HH-ALOS2046743050-150405-WBDR1.1__D-F1.PRM ALOS"
  echo ""
  echo "Optional 4th argument produces a subsampled ascii file (using blockmedian) in place of the full-resolution one. Grid files are always full resolution."
  echo ""
  echo "  Example: make_los_products.csh los_ll.grd IMG-HH-ALOS2046743050-150405-WBDR1.1__D-F1.PRM ALOS -I0.01/0.01"
  echo ""
  echo "Outputs: look_e.grd, look_n.grd, look_u.grd, los_ll.lltenud"
  echo ""
  exit 1
endif

#check SAT input value
set SAT = $3
if( ($SAT != ALOS2) && ($SAT != ALOS) && ($SAT != TSX) && ($SAT != ENVI) && ($SAT != ERS) && ($SAT != S1) && ($SAT != SAT)) then
  echo ""
  echo " SAT must be ERS, ENVI, ALOS, ALOS2, TSX, S1, or generic SAT"
  echo ""
  exit 1
endif

#to run SAT_look, the LED file needs to be linked in the same directory.
#We assume we are located in a directory like: intf/date1_date2/, so the LED file is in ../../raw/
set ledfile = `grep led_file $2 | awk '{print $3}'`
ln -s ../../raw/$ledfile .

#get the correct satellite name for SAT_look:
if ($SAT == TSX || $SAT == S1) then
  set SAT = 'SAT'
else if ($SAT == ERS) then
  set SAT = 'ENVI'
else if ($SAT == ALOS2) then
  set SAT = 'ALOS'
endif
  
#resample the topo at the resolution of input file $1
echo "resample topo grid and convert to ascii"
gmt grdsample ../../topo/dem.grd -Gtmp_topo.grd `grdinfo $1 -I-` `grdinfo $1 -I` -r
gmt grd2xyz -s tmp_topo.grd > tmp_topo.llt

#mask topo
gmt grdmath tmp_topo.grd $1 OR = tmp_topo_mask.grd
gmt grd2xyz -s tmp_topo_mask.grd > tmp_topo_mask.llt

#ascii file for data
gmt grd2xyz -s $1 > tmp_los.lld

#check line number consistency
set loslines = `wc -l tmp_los.lld |awk '{print $1}'`
set looklines = `wc -l tmp_topo_mask.llt |awk '{print $1}'`
if ($loslines != $looklines) then
  echo "Error: different number of lines in the two files. Check that your grid registration is consistent and try again"
  exit 1
endif

# really bad code - have to hardcode this path because later versions do not work for ALOS-1.

echo "running "$SAT"_look on full topo for grids..."
/usr/local/GMT5SAR5.2_GMT5.4.1/bin/$SAT"_"look $2 < tmp_topo.llt > tmp_topo_look.lltenu

echo "creating look_[e,n,u].grd files..."
awk '{print $1,$2,$4}' tmp_topo_look.lltenu |gmt xyz2grd -R$1 -Glook_e.grd
awk '{print $1,$2,$5}' tmp_topo_look.lltenu |gmt xyz2grd -R$1 -Glook_n.grd
awk '{print $1,$2,$6}' tmp_topo_look.lltenu |gmt xyz2grd -R$1 -Glook_u.grd

echo "running "$SAT"_look on masked topo for ascii product..."
/usr/local/GMT5SAR5.2_GMT5.4.1/bin/$SAT"_"look $2 < tmp_topo_mask.llt > tmp_topo_look_mask.lltenu

if ($#argv == 4) then
  echo "downsample each ascii column to $4 using blockmedian"
  cut -f1,2,3 tmp_topo_look_mask.lltenu | gmt blockmedian `grdinfo $1 -I-` $4 -V > tmp.t
  cut -f1,2,4 tmp_topo_look_mask.lltenu | gmt blockmedian `grdinfo $1 -I-` $4 -V > tmp.e
  cut -f1,2,5 tmp_topo_look_mask.lltenu | gmt blockmedian `grdinfo $1 -I-` $4 -V > tmp.n
  cut -f1,2,6 tmp_topo_look_mask.lltenu | gmt blockmedian `grdinfo $1 -I-` $4 -V > tmp.u
  paste tmp.t tmp.e tmp.n tmp.u | cut -f1,2,3,6,9,12 > tmp_topo_look_mask.lltenu
  gmt blockmedian tmp_los.lld `grdinfo $1 -I-` $4 -V > tmp
  mv tmp tmp_los.lld
endif

#file basename (without .grd extension)
set base = $1:r
#create ascii output file
echo "creating ascii product: $base.lltenud. Columns are lat, lon, topo, look_E, look_N, look_U, displacement, -1 placeholder for sigma"
awk '{ a=$3;getline <"tmp_topo_mask.llt";print $1,$2,$3,$4,$5,$6,a,-1}' tmp_los.lld > $base.lltenud

#cleanup temporary files
#rm tmp*

