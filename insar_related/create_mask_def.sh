#!/bin/bash

polygon=clip_F1.gmt
basename=$(basename $polygon .gmt)
clipin=$basename".gmt"
clipra=$basename"_ra.xy"
regcorr=`grdinfo intf/20*/corr.grd -I- | head -1`
inccorr=`grdinfo intf/20*/corr.grd -I | head -1`
maskdef=mask_def.grd

#ll to llh
grep -v ">" $clipin | awk '{print $1,$2,0}' > temp && mv temp $clipin

# llh to radar
proj_ll2ra_ascii.csh topo/trans.dat $clipin $clipra

# create mask_def.grd
grdmask $clipra $regcorr $inccorr -N0/0/1 -G$maskdef
