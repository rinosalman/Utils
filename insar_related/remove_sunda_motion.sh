#!/bin/bash

# euler pole parameters
#sunda="0.047 -1.000 0.975" #from /LujiaMatlab/euler_pole/SUNDA-ITRF2008.euler
#sunda="45.51 -89.44 0.345" #from sen etal
sunda="50 -89.8 0.328"      #from panda etal

# run the code
#plate_motion.py -g geo_geometryRadar.h5  --om-cart $sunda -v geo_velocity.h5 
plate_motion.py -g geo_geometryRadar.h5  --om-sph $sunda -v geo_velocity.h5 

