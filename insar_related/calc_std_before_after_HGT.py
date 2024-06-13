#! /usr/bin/env python
'''
ifgram_reconstruction.py timeseries.h5 -r inputs/ifgramStack.h5 -o ifgramStackRecon.h5
mv ifgramStackRecon.h5 ifgramStackRecon.h5

September 2021
'''

import numpy as np
import h5py, os

infile = 'ifgramStackRecon.h5'
infileHgt = 'ifgramStackReconHGT.h5'
f = h5py.File(infile,'r')
fHgt = h5py.File(infileHgt,'r')
allintf = f['unwrapPhase']
allintfHgt = fHgt['unwrapPhase']
os.system("echo '#stdv_no_correction stdv_after_HGT_correction' > std_before_after_HGT.txt")
for i in range(len(allintf)):
    intfN = allintf[i]
    intfN_hgt = allintfHgt[i]
    std = np.std(intfN)
    stdHgt = np.std(intfN_hgt)
    os.system("echo %s %s >> std_before_after_HGT.txt"%(std,stdHgt))
