import numpy as np
import grd_io
import os
import sys

inp=sys.argv[1]

#write files and sum up
ids=np.genfromtxt(inp,str,usecols=0)
len_ids=len(ids)
data=[]
for id in ids:
    x,y,z=grd_io.read_grd(id,naming='xy')
    data.append(z)

#compute the mean
sumCorr=np.sum(data,axis=0)
meanCorr=sumCorr/len_ids

#write
grd_io.write_grd(x,y,meanCorr,'mean_corr.grd',naming='xy')

