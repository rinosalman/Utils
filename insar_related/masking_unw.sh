#!/bin/bash


#masking
#generate_mask.py ../geo_filt_msk_wbd_ERA5.unw --roipoly
generate_mask.py maskPoly.h5 -M 0.5 -o mask.h5
mask.py ../geo_filt_msk_wbd_ERA5.unw -m mask.h5 -o geo_filt_msk_wbd_ERA5.masked.unw
mask.py ../geo_los.los -m mask.h5 -o geo_los.masked.los
