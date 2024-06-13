#!/bin/bash

# exclude some pairs
cd pairs
a='/home/share/miniconda3/envs/isce2_v2.6.3/share/isce2/alosStack/ion_check.py -idir pairs_ion -odir fig_ion -pairs'
b=`ls -d *-* | awk 'BEGIN {ORS = " "} {print}'`
cd ../
echo "$a $b"
