#!/usr/bin/env python3

import isce
from isceobj.Sensor import createSensor
import shelve
import argparse
import glob
from isceobj.Util import Poly1D
from isceobj.Planet.AstronomicalHandbook import Const
import os
import datetime
import numpy as np

def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(description='Unpack Envisat SLC data and store metadata in pickle file.')
    parser.add_argument('-i','--input', dest='datadir', type=str,
            required=True, help='Input Envisat directory')
    parser.add_argument('-o', '--output', dest='slcdir', type=str,
            required=True, help='Output SLC directory')
    parser.add_argument('--orbitdir', dest='orbitdir', type=str, required=True, help='Orbit directory')
    parser.add_argument('--instrdir',dest='instrdir', type = str, required=True,help='Instrument directory')

    return parser.parse_args()

def get_Date(file):
    yyyymmdd=file[14:22]
    return yyyymmdd

def write_xml(shelveFile, slcFile):
    with shelve.open(shelveFile,flag='r') as db:
        frame = db['frame']

    length = frame.numberOfLines 
    width = frame.numberOfSamples
    print (width,length)

    slc = isceobj.createSlcImage()
    slc.setWidth(width)
    slc.setLength(length)
    slc.filename = slcFile
    slc.setAccessMode('write')
    slc.renderHdr()
    slc.renderVRT()

def unpack(fname, slcname, orbitdir, instrdir):
    '''
    Unpack HDF5 to binary SLC file.
    '''

    #fname = glob.glob(os.path.join(hdf5,'ASA*.N1'))[0]
    #if not os.path.isdir(slcname):
    #    os.mkdir(slcname)

    #date = os.path.basename(slcname)

    obj = createSensor('ENVISAT_SLC')
    obj._imageFileName = fname
    obj.orbitDir = orbitdir
    obj.instrumentDir = instrdir
    obj.output = os.path.join(slcname,os.path.basename(slcname)+'.slc')

    obj.extractImage()
    obj.frame.getImage().renderHdr()
    #obj.extractDoppler()


    ######Numpy polynomial manipulation
    #pc = obj._dopplerCoeffs[::-1]
    pc = obj.dopplerRangeTime[::-1]
    
    inds = np.linspace(0, obj.frame.numberOfSamples-1, len(pc) + 1)+1
    rng = obj.frame.getStartingRange() + inds * obj.frame.instrument.getRangePixelSize()
    #dops = np.polyval(pc, 2*rng/Const.c-obj._dopplerTime)
    dops = np.polyval (pc, 2*rng/Const.c-obj.rangeRefTime)

    print('Near range doppler: ', dops[0])
    print('Far range doppler: ', dops[-1])
   
    dopfit = np.polyfit(inds, dops, len(pc)-1)
    
    poly = Poly1D.Poly1D()
    poly.initPoly(order=len(pc)-1)
    poly.setCoeffs(dopfit[::-1])

    print('Poly near range doppler: ', poly(1))
    print('Poly far range doppler: ', poly(obj.frame.numberOfSamples))

#    width = obj.frame.getImage().getWidth()
#    midrange = r0 + 0.5 * width * dr
#    dt = datetime.timedelta(seconds = midrange / Const.c)

#    obj.frame.sensingStart = obj.frame.sensingStart - dt
#    obj.frame.sensingStop = obj.frame.sensingStop - dt
#    obj.frame.sensingMid = obj.frame.sensingMid - dt


    pickName = os.path.join(slcname, 'data')
    with shelve.open(pickName) as db:
        db['frame'] = obj.frame
        db['doppler'] = poly 


if __name__ == '__main__':
    '''
    Main driver.
    '''

    inps = cmdLineParse()
    if inps.slcdir.endswith('/'):
        inps.slcdir = inps.slcdir[:-1]
    if not os.path.isdir(inps.slcdir):
        os.mkdir(inps.slcdir)
    for fname in glob.glob(os.path.join(inps.datadir, '*.N*')):
        date = get_Date(os.path.basename(fname))
        slcname = os.path.abspath(os.path.join(inps.slcdir, date))
        os.makedirs(slcname, exist_ok=True)

        print(fname)
        unpack(fname, slcname, inps.orbitdir, inps.instrdir)

        #slcFile = os.path.abspath(os.path.join(slcname, date+'.slc'))

        #shelveFile = os.path.join(slcname, 'data')
        #write_xml(shelveFile,slcFile)

#        if inps.bbox is not None:
#            slccropname = os.path.abspath(os.path.join(inps.slcdir+'_crop',date))
#            os.makedirs(slccropname, exist_ok=True)
#            cmd = 'cropFrame.py -i {} -o {} -b {}'.format(slcname, slccropname, ' '.join([str(x) for x in inps.bbox]))
#            print(cmd)
#            os.system(cmd)
