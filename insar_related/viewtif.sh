#!/bin/bash

inp=$1
out=$1.geo
imageMath.py -e='abs(a); arg(a)' --a=./$inp -o $out -t FLOAT -s BIL
python3 isce2geotiff_unw.py $out -b 2 --nodata 0
