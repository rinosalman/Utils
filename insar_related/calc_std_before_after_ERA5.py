#! /usr/bin/env python
# September 2021

import numpy as np
import h5py, os

infile = 'ifgramStackRecon.h5'
infileERA5 = 'ifgramStackReconERA5.h5'
f = h5py.File(infile,'r')
fERA5 = h5py.File(infileERA5,'r')
allintf = f['unwrapPhase']
allintfERA5 = fERA5['unwrapPhase']
os.system("echo '#stdv_no_correction stdv_after_ERA_correction' > std_before_after_ERA5.txt")
for i in range(len(allintf)):
    intfN = allintf[i]
    intfN_ERA5 = allintfERA5[i]
    std = np.std(intfN)
    stdERA5 = np.std(intfN_ERA5)
    os.system("echo %s %s >> std_before_after_ERA5.txt"%(std,stdERA5))

