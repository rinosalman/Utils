#!/usr/bin/env python3

import isce
from isceobj.Sensor import createSensor
import shelve
import argparse
import glob
from isceobj.Util import Poly1D
from isceobj.Planet.AstronomicalHandbook import Const
import os

def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(description='Unpack ALOS2 SLC data and store metadata in pickle file.')
    parser.add_argument('-i','--input', dest='h5dir', type=str,
            required=True, help='Input ALOS2 directory')
    parser.add_argument('-o', '--output', dest='slcdir', type=str,
            required=True, help='Output SLC directory')
    parser.add_argument('-d', '--deskew', dest='deskew', action='store_true',
            default=False, help='To read in for deskewing data later')
    parser.add_argument('-p', '--polarization', dest='polarization', type=str,
            default='HH', help='polarization in case if quad or full pol data exists. Deafult: HH')
    return parser.parse_args()


def unpack(hdf5, slcname, deskew=False, polarization='HH'):
    '''
    Unpack HDF5 to binary SLC file.
    '''
    img=glob.glob(os.path.join(hdf5, 'IMG-{}*F1'.format(polarization)))
    print('%s'%img)
    for ii in range(len(img)):
        imgname = img[ii]
        print('Process: %s'%imgname)
        a,b,c,d,e,f=imgname.split("-")
        ldrname = hdf5+'/LED-'+c+'-'+d+'-'+e
        slcdir=slcname+'/20'+d
    
        if not os.path.isdir(slcdir):
           os.makedirs(slcdir)

        date = os.path.basename(slcdir)
        obj = createSensor('ALOS2')
        obj.configure()
        obj._leaderFile = ldrname
        obj._imageFile = imgname

        if deskew:
           obj.output = os.path.join(slcdir, date+'_orig.slc')
        else:
           obj.output = os.path.join(slcdir, date + '.slc')
        
        print(obj._leaderFile)
        print(obj._imageFile)
        print(obj.output)
        obj.extractImage()
        obj.frame.getImage().renderHdr()


        coeffs = obj.doppler_coeff
        dr = obj.frame.getInstrument().getRangePixelSize()
        r0 = obj.frame.getStartingRange()


        poly = Poly1D.Poly1D()
        poly.initPoly(order=len(coeffs)-1)
        poly.setCoeffs(coeffs)


        fcoeffs = obj.azfmrate_coeff
        fpoly = Poly1D.Poly1D()
        fpoly.initPoly(order=len(fcoeffs)-1)
        fpoly.setCoeffs(fcoeffs)

        if deskew:
           pickName = os.path.join(slcdir, 'original')
        else:
           pickName = os.path.join(slcdir, 'data')
        with shelve.open(pickName) as db:
           db['frame'] = obj.frame
           db['doppler'] = poly
           db['fmrate'] = fpoly
           db['info'] = obj.leaderFile.facilityRecord.metadata

        print(poly._coeffs)
        print(fpoly._coeffs)

if __name__ == '__main__':
    '''
    Main driver.
    '''

    inps = cmdLineParse()
    if inps.slcdir.endswith('/'):
        inps.slcdir = inps.slcdir[:-1]

    if inps.h5dir.endswith('/'):
        inps.h5dir = inps.h5dir[:-1]

    obj = unpack(inps.h5dir, inps.slcdir,
                 deskew=inps.deskew,
                 polarization=inps.polarization)

