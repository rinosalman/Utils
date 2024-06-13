from mintpy.utils import readfile, writefile
import numpy as np


#read necessary files
velo,atr1=readfile.read('geo_velocity_ITRF14.h5',datasetName='velocity')
incA,atr2=readfile.read('geo_geometryRadar.h5',datasetName='incidenceAngle')

#do computation
vert=velo/np.cos(incA*np.pi/180)

#save
writefile.write(vert,out_file='geo_velocity_ITRF14_vertical.h5',metadata=atr1)
