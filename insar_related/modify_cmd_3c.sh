#!/bin/bash

a='/usr/local/anaconda3-2020/envs/isce2_v2.5.1/share/isce2/alosStack/ion_ls.py -idir pairs_ion -odir dates_ion -ref_date_stack 150224 -nrlks1 1 -nalks1 14 -nrlks2 10 -nalks2 4 -nrlks_ion 80 -nalks_ion 32 -interp -exc_pair'

b=`cat exclude_pairs | awk 'BEGIN {ORS = " "} {print}'`

echo "$a $b"
