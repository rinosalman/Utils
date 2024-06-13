#! /usr/bin/env python
'''
ifgram_reconstruction.py timeseries.h5 
mv ifgramStackRecon.h5 ifgramStackRecon.h5

ifgram_reconstruction.py timeseries_ERA5.h5 
mv ifgramStackRecon.h5 ifgramStackReconERA5.h5

February 2021
'''

import numpy as np
import h5py, os

infile = 'ifgramStackReconOri.h5'
infileERA5 = 'ifgramStackReconERA5.h5'
f = h5py.File(infile,'r')
fERA5 = h5py.File(infileERA5,'r')
allintf = f['unwrapPhase']
allintfERA5 = fERA5['unwrapPhase']
for i in range(len(allintf)):
    intfN = allintf[i]
    intfN_ERA5 = allintfERA5[i]
    std = np.std(intfN)
    stdERA5 = np.std(intfN_ERA5)
    os.system("echo %s %s >> std_before_after_ERA.txt"%(std,stdERA5))

