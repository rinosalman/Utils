#! /usr/bin/env python
# October 2021

import numpy as np
import h5py, os

# read in incidence angle and azimuth angle
infile = 'geometryRadar.h5'
f = h5py.File(infile,'r')
incAngle = f['incidenceAngle'][0]
azAngle = f['azimuthAngle'][0]

# convert to radian
incAngle *= np.pi/180.
azAngle *= np.pi/180.

# get LOS unit vector
unitVec = [np.sin(incAngle) * np.sin(azAngle) * -1,
                    np.sin(incAngle) * np.cos(azAngle),
                    np.cos(incAngle)]

# read in lon and lat
lon = f['longitude'][0]
lat = f['latitude'][0]

#os.system("echo %s %s %s > unit_vector_east"%(lon,lat,unitVec[0]))
for i in range(len(lon)):
    lonn = lon[i]
    latt = lat[i]
    uvE  = unitVec[0][i]
    os.system("echo %s %s %s >> unit_vector_east"%(lonn,latt,uvE))
