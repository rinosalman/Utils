#! /usr/bin/env python
# September 2021

import numpy as np
import h5py, os

infile = 'ifgramStackRecon.h5'
infileGACOS = 'ifgramStackReconGACOS.h5'
f = h5py.File(infile,'r')
fGACOS = h5py.File(infileGACOS,'r')
allintf = f['unwrapPhase']
allintfGACOS = fGACOS['unwrapPhase']
os.system("echo '#stdv_no_correction stdv_after_GACOS_correction' > std_before_after_GACOS.txt")
for i in range(len(allintf)):
    intfN = allintf[i]
    intfN_GACOS = allintfGACOS[i]
    std = np.std(intfN)
    stdGACOS = np.std(intfN_GACOS)
    os.system("echo %s %s >> std_before_after_GACOS.txt"%(std,stdGACOS))

