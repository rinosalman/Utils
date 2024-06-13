#!/bin/csh -f
#       $Id$

# sbas processing

# Xiaohua(Eric) Xu, Jan 25 2016
#

  if ($#argv != 2) then
    echo ""
    echo "Usage: prep_sbas.csh intf.in baseline_table.dat"
    echo ""
    echo "  outputs: "
    echo "    intf.tab scene.tab"
    echo ""
    echo "  Command to run sbas will be echoed"
    echo ""
    exit 1
  endif

  set file = $1
  set table = $2

  rm intf.tab scene.tab scene.temp
  
  set ni = "0"
  set ns = "0"
  set intf = "../intf"
  
  foreach line (`awk '{print $0}' $1`) 
    set ref = `echo $line | awk -F: '{print $1}'`
    set rep = `echo $line | awk -F: '{print $2}'`
    set ref_id  = `grep $ref $table | awk '{printf("%d",int($2))}' `
    set rep_id  = `grep $rep $table | awk '{printf("%d",int($2))}' `
    set b1 = `grep $ref $table | awk '{print $5}'`
    set b2 = `grep $rep $table | awk '{print $5}'`
    set bp = `echo $b1 $b2 | awk '{print ($2-$1)}'`
    echo "../$intf/$ref_id"_"$rep_id/unwrap_pad.grd ../$intf/$ref_id"_"$rep_id/corr_pad.grd $ref_id $rep_id $bp" >> intf.tab
    set ntmp = `echo $ni`
    set ni = `echo $ntmp | awk '{print ($1+1)}'`
  end

  foreach line  (`awk '{print $1":"$2":"$3":"$4":"$5}' < $table`)
    set sc = `echo $line | awk -F: '{print $1}'`
    set sc_id = `echo $line | awk -F: '{printf "%d", int($2)}'`
    set dy = `echo $line | awk -F: '{print $3}'`
    echo "$sc_id $dy" >> scene.temp
    set ntmp = `echo $ns`
    set ns = `echo $ntmp | awk '{print ($1+1)}'`
  end
  sort -k1 -n scene.temp > scene.tab

  set xdim = `gmt grdinfo -C ../$intf/$ref_id"_"$rep_id/unwrap_pad.grd | awk '{print $10}'`
  set ydim = `gmt grdinfo -C ../$intf/$ref_id"_"$rep_id/unwrap_pad.grd | awk '{print $11}'`
  
  set xmin = `gmt grdinfo -C ../$intf/$ref_id"_"$rep_id/unwrap_pad.grd | awk '{print $2}'`
  set xmax = `gmt grdinfo -C ../$intf/$ref_id"_"$rep_id/unwrap_pad.grd | awk '{print $3}'`
  set xminmax = `echo $xmin $xmax | awk '{print $1+$2}'`

  set Ninc = 40
  set wavel = 0.0554658
  set Nsm = 5.0
  set sol = 3e8
  set atm = 2
  set rngsamprate = `grep rng_samp_rate ../../topo/master.PRM | awk 'NR==1{print $3}'`
  set temp = `echo $sol $rngsamprate $xminmax | awk '{print $1/$2/$3}'`
  set range = `echo $temp 845000 | awk '{print $1+$2}'`
   
  echo ""
  echo "sbas intf.tab scene.tab $ni $ns $xdim $ydim -range $range -incidence $Ninc -wavelength $wavel -smooth $Nsm -rms -dem -atm $atm"
  echo ""
  sbas intf.tab scene.tab $ni $ns $xdim $ydim -range $range -incidence $Ninc -wavelength $wavel -smooth $Nsm -rms -dem -atm $atm
