#!/usr/bin/env python3


import os
import sys
import argparse
import datetime
import pickle
import struct
import zipfile

#import isce
#import isceobj
#from isceobj.Orbit.Orbit import Orbit


def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser( description='report ALOS-2 product version')
    parser.add_argument('-i', dest='input', type=str, required=True,
            help = 'ALOS-2 product zipped ONLY once, leader file of standard ALOS-2 product, or date.slc.pck file')

    return parser.parse_args()



if __name__ == '__main__':

    inps = cmdLineParse()

    strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')

    #zipped ALOS2 product
    if '.zip' in inps.input:
        zf = zipfile.ZipFile(inps.input, 'r')
        fileNames = zf.namelist()
        for fileNamex in fileNames:
            if 'LED-ALOS' in fileNamex:
                print('\nreading orbit type from: {}'.format(fileNamex))
                f=zf.open(fileNamex, 'r')
                f.read(720+1070)#no seek method for this kind of open file
                d = struct.unpack("8s", f.read(8))
                f.close()
                zf.close()
                break 

    elif 'LED-ALOS' in inps.input:
        with open(inps.input, 'rb') as f:
            #f.seek(720, 1) #file descriptor
            #f.seek(4096, 1) #Data set summary
            #f.seek(12, 1) #Platform position data
            f.seek(720+1070, 1) #Platform position data
            d = struct.unpack("8s", f.read(8))
    elif '.slc.pck' in inps.input:
        import isce, isceobj
        with open(inps.input, 'rb') as f:
            frame = pickle.load(f)
            d = frame.getProcessingSoftwareVersion()
    else:
        raise Exception('unknown input file format\n')


    if ('.zip' in inps.input) or ('LED-ALOS' in inps.input):
        d = d[0]
        strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')
        d = strp_3(d)
        version = d
    else:
        version = d



    print('product version: {}'.format(version))
