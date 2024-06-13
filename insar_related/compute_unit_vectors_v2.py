#! /usr/bin/env python
# October 2021

import numpy as np
import h5py, os
from mintpy.utils import utils1, readfile, writefile


# read in incidence angle, azimuth angle, longitude, and latitude
#infile = 'geo_geometryRadar.h5'
#f = h5py.File(infile,'r')
#row = f['incidenceAngle'].shape[0]
losGeo = '220905-230220_5rlks_28alks.los.geo'
lonGeo = '220905-230220_5rlks_28alks.lon.geo'
latGeo = '220905-230220_5rlks_28alks.lat.geo'
f = {}
f['incidenceAngle']=readfile.read(losGeo, datasetName='incidenceAngle')[0]
f['azimuthAngle']=readfile.read(losGeo, datasetName='azimuthAngle')[0]
f['longitude']=readfile.read(lonGeo, datasetName='longitude')[0]
f['latitude']=readfile.read(latGeo, datasetName='latitude')[0]
row = f['incidenceAngle'].shape[0]


#for i in range(1):
for i in range(row):
    incAngle = f['incidenceAngle'][i]
    azAngle = f['azimuthAngle'][i]

    # convert to radian
    incAngle *= np.pi/180.
    azAngle *= np.pi/180.

    # get LOS unit vector
    unitVec = [np.sin(incAngle) * np.sin(azAngle) * -1,
               np.sin(incAngle) * np.cos(azAngle),
               np.cos(incAngle)]

    # read in lon and lat
    lon = f['longitude'][i]
    lat = f['latitude'][i]
    
    # save
    for j in range(len(lon)):
        lonn = lon[j]
        latt = lat[j]
        uvE  = unitVec[0][j]
        uvN  = unitVec[1][j]
        uvU  = unitVec[2][j]
        incA = incAngle[j]
        incA *= 180/np.pi
        os.system("echo %s %s %s >> unit_vector_east"%(lonn,latt,uvE))
        os.system("echo %s %s %s >> unit_vector_north"%(lonn,latt,uvN))
        os.system("echo %s %s %s >> unit_vector_up"%(lonn,latt,uvU))
        os.system("echo %s %s %s >> incidence_angle"%(lonn,latt,incA))
