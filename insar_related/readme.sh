#!/bin/bash

#whole
vv="-v -2 6"
view.py geo_filt_msk_ERA5.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude $vv -o geo_filt_msk_ERA5.unw-phase.png
view.py geo_filt_msk_GACOS.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude $vv -o geo_filt_msk_GACOS.unw-phase.png
view.py geo_filt_msk.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude $vv -o geo_filt_msk.unw-phase.png

#subset
xx="585 800"
yy="755 900"
vv="-v -2 6"
view.py geo_filt_msk_ERA5.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude --sub-x $xx --sub-y $yy $vv -o geo_filt_msk_ERA5.subset.unw-phase.png
view.py geo_filt_msk_GACOS.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude --sub-x $xx --sub-y $yy $vv -o geo_filt_msk_GACOS.subset.unw-phase.png
view.py geo_filt_msk.unw --dem height_geocoded_manually.hgt.dem --save --nodisplay --ex magnitude --sub-x $xx --sub-y $yy $vv -o geo_filt_msk.subset.unw-phase.png
