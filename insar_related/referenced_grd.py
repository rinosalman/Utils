# subtract the median value of the data around the reference point from each interferogram
import numpy as np
import grd_io
import os
import sys
import detrend_ts

inp=sys.argv[1]
reflon=float(sys.argv[2])
reflat=float(sys.argv[3])
refrad=int(sys.argv[4])
print('Referencing interferograms to median value of nearest %d pixels to point (%f,%f) '%(refrad,reflon,reflat))

#read files
grdnaming='xy'
ids=np.genfromtxt(inp,str,usecols=0)
for id in ids:
    x,y,z=grd_io.read_grd(id,naming=grdnaming)
    X,Y=np.meshgrid(x,y)
    xn,yn,meannear,mediannear=detrend_ts.get_near_data(X,Y,z,reflon,reflat,refrad)
    z-=mediannear

    #write
    grd_io.write_grd(x,y,z,'%s_ref.grd'%id,naming=grdnaming)

