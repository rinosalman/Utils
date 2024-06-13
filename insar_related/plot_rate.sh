#!/bin/bash

# make a cpt file
gmt makecpt -Cjet -T-20/20/0.1 -D -Z > jet20.cpt

# plot rate.grd
gmt grdimage rate.grd -Cjet20.cpt -JM5i -Rrate.grd -P > rate.ps

# grab points for cross section
gmt grd2xyz rate.grd -s |gmt project -C95.886/4.73 -E96.3/5.118 -Q -W-1/1 -Fpz > rate_transect.dat

# plot cross section
gmt psxy rate_transect.dat -JX5i/3i -R-100/100/-50/50 -P -Sc0.1c -Gblack -Bafg > rate_transect.ps

# open
gs rate.ps &
gs rate_transect.ps &
