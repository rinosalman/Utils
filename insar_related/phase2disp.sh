#!/bin/bash

inp=filt_220905-230220_5rlks_28alks_msk.unw.geo
out=filt_220905-230220_5rlks_28alks_msk.unw.mtr.geo 
wvl=0.2424
gdal_calc.py -A $inp --A_band=2 --calc="-1*A*${wvl}/(4*numpy.pi)" --outfile=$out --format=ENVI --NoDataValue=0 --overwrite
