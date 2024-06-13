#!/bin/bash


# masking
unw=filt_fine.unw
unwMsk=filt_fine_msk.unw
los=../../geom_reference/los.rdr
losMsk=los_msk.rdr
mask=../../../mintpy/maskTempCoh.h5
mask.py $unw -m $mask -o $unwMsk
mask.py $los -m $mask -o $losMsk

# geocode
geom=../../../mintpy/inputs/geometryRadar.h5
step=0.000833334  ##degre, ~90 meter
geocode.py $unwMsk -l $geom --lalo -$step $step -o geo_$unwMsk
geocode.py $losMsk -l $geom --lalo -$step $step -o geo_los.los
