import mintpy
#from mintpy.utils import utils1, readfile
import h5py, os
import numpy as np


'''
README
Before executing this command, run MintPy to generate geometryRadar.h5
'''

# geocoding
geomFile = 'geometryRadar.h5'
geomFileGeo = 'geo_'+geomFile
#step = 0.000833334 # degrees, ~90 m
step = 0.0089932160591873 # degrees, 1 km
#step = 0.0449660802959365 # degrees, 5 km
os.system('''geocode.py {} -l {} --lalo -{} {} -o {}'''.format(geomFile,geomFile,step,step,geomFileGeo))

# grab lon lat, compute unit vectors
f = h5py.File(geomFileGeo,'r')
row = f['longitude'].shape[0]

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
    print(lon)

    # save
    for j in range(len(lon)):
        lonn = lon[j]
        latt = lat[j]
        uvE  = unitVec[0][j]
        uvN  = unitVec[1][j]
        uvU  = unitVec[2][j]
        incA = incAngle[j]
        incA *= 180/np.pi
        os.system("echo %s %s %s %s %s>> lonLat_uvs_ENU"%(lonn,latt,uvE,uvN,uvU))
        #os.system("echo %s %s %s >> unit_vector_north"%(lonn,latt,uvN))
        #os.system("echo %s %s %s >> unit_vector_up"%(lonn,latt,uvU))
        #os.system("echo %s %s %s >> incidence_angle"%(lonn,latt,incA))


# remove nan
os.system("cat lonLat_uvs_ENU | awk '!/nan/' > lonLat_uvs_ENU_noNaN_1km.txt")
