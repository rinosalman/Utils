#! /usr/bin/env python
# January 2023

from mintpy.utils import readfile, writefile
import h5py

# read in the correction scenes
infile = 'ERA5.h5'
f = h5py.File(infile,'r')
ref = f['timeseries'][0]
rep = f['timeseries'][1]

# take the difference
diff = rep - ref

# read in the attribute
timeseries,atr = readfile.read(infile, datasetName='timeseries')

# save
writefile.write(diff, 'troposphere_phase_screen.geo', metadata=atr)
#writefile.write_isce_xml(atr,'troposphere_phase_screen.geo')
