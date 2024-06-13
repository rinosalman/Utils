#!/bin/bash

echo "Transform radar coordinates to geographic coordinates"
echo ""
ln -s ../../topo/trans.dat .
gauss=`ls ../../intf/20*/gauss* | head -1`
ln -s $gauss .
proj_ra2ll.csh trans.dat vel.grd vel_ll.grd
gmt grd2cpt vel_ll.grd -T= -Z -Cjet > vel_ll.cpt
grd2kml.csh vel_ll vel_ll.cpt

for line in `ls disp_*.grd`;do
   ofile=$(basename $line .grd)_ll.grd
   proj_ra2ll.csh trans.dat $line $ofile
   nccopy -k classic $ofile $file.nc3
done


echo "Create png files of disp_ll*"
echo ""
n=1
for grd in `ls disp_*_ll.grd`;do

   grdnoext=$(basename $grd .grd)
      
   #if [ $n -eq 1 ];then
   echo "Making cpt file based on $grd"
   # make cpt
   cpt=$grd.cpt
   tmp=`gmt grdinfo -C -L2 $grd`
   limitU=`echo $tmp | awk '{printf("%5.1f", $12+$13*2)}'`
   limitL=`echo $tmp | awk '{printf("%5.1f", $12-$13*2)}'`
   makecpt -Cpolar -Z -T"$limitL"/"$limitU"/1 -D > $cpt
   #fi

   # geocode
   grd2kml.csh $grdnoext $cpt

   #counter
   let n=n+1

done


echo "Extract data for time series plot"
echo ""
rm point_*
points=points.txt
n=1
for i in `cat $points`;do

   #cut regions
   lon1=`echo $i | awk -F, '{print $1}'`
   lat1=`echo $i | awk -F, '{print $2}'`
   lon2=`echo $i | awk -F, '{print $1+0.05}'`
   lat2=`echo $i | awk -F, '{print $2+0.05}'`
   reg=$lon1/$lon2/$lat1/$lat2

   l=1
   for j in `ls disp_*_ll.grd`;do
      #grdcut
      grdcut $j -R$reg -Gtmp.grd
		
      #compute mean value
      grdmath tmp.grd DUP LOWER EXCH UPPER ADD 2 DIV = tmp2.grd

      #time and mean value
      time=`echo $j | awk '{ print substr($1,6,length($1)-12)}'`
      mean=`grdinfo tmp2.grd -C | awk '{print $6}'`

      #save
      echo $l $time $mean >> point_$n.txt

      #counter
      let l=l+1
   done
	
   #counter
   let n=n+1

done
