#!/usr/bin/env python3
#check alos2 processing system software version
#modified from Cunren Liang

#import os
#import sys
#import datetime
#import pickle
#import struct
#import zipfile
import argparse, glob, os, struct
import numpy as np


def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='report ALOS-2 product version')
    parser.add_argument('-i', dest='intf', type=str, required=True,
          help = 'Interferogram pairs folder')
    return parser.parse_args()


if __name__ == '__main__':

    # get inputs
    inps = cmdLineParse()

    # get pairs
    pairs = sorted(glob.glob(os.path.join(inps.intf, '20*')))

    # extract the software version information
    npair = len(pairs)
    for i in range(npair):
        pair = pairs[i].split('/')[-1]

        # reference image
        mdate = pair.split('_')[0][2:]
        mdateled = glob.glob('raw/LED*{}*'.format(mdate))[0]
        with open(mdateled, 'rb') as f:
            f.seek(720+1070, 1) #Platform position data
            d = struct.unpack("8s", f.read(8))

        # version
        d = d[0]
        strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')
        d = strp_3(d)
        mversion = d

        # secondary image
        sdate = pair.split('_')[1][2:]
        sdateled = glob.glob('raw/LED*{}*'.format(sdate))[0]
        with open(sdateled, 'rb') as f:
            f.seek(720+1070, 1) #Platform position data
            d = struct.unpack("8s", f.read(8))

        # version
        d = d[0]
        strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')
        d = strp_3(d)
        sversion = d

        # check if software versions are same or not between reference and secondary images
        msversion = np.float(mversion[2:]) - np.float(sversion[2:])

        # save
        if i == 0:
           os.system('''echo "#Processing system software version used for reference and secondary images" > processing_system_software_version.txt''')
           if msversion == 0.0:
              os.system('''echo "20%s_20%s: %s_%s" >> processing_system_software_version.txt'''%(mdate,sdate,mversion,sversion))
           else:
              os.system('''echo "20%s_20%s: %s_%s <-- different software version" >> processing_system_software_version.txt'''%(mdate,sdate,mversion,sversion))
        else:
           if msversion == 0.0:
              os.system('''echo "20%s_20%s: %s_%s" >> processing_system_software_version.txt'''%(mdate,sdate,mversion,sversion))
           else:
              os.system('''echo "20%s_20%s: %s_%s <-- different software version" >> processing_system_software_version.txt'''%(mdate,sdate,mversion,sversion))


#    strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')
#
#    #zipped ALOS2 product
#    if '.zip' in inps.input:
#        zf = zipfile.ZipFile(inps.input, 'r')
#        fileNames = zf.namelist()
#        for fileNamex in fileNames:
#            if 'LED-ALOS' in fileNamex:
#                print('\nreading orbit type from: {}'.format(fileNamex))
#                f=zf.open(fileNamex, 'r')
#                f.read(720+1070)#no seek method for this kind of open file
#                d = struct.unpack("8s", f.read(8))
#                f.close()
#                zf.close()
#                break 
#
#    elif 'LED-ALOS' in inps.input:
#        with open(inps.input, 'rb') as f:
#            #f.seek(720, 1) #file descriptor
#            #f.seek(4096, 1) #Data set summary
#            #f.seek(12, 1) #Platform position data
#            f.seek(720+1070, 1) #Platform position data
#            d = struct.unpack("8s", f.read(8))
#    elif '.slc.pck' in inps.input:
#        import isce, isceobj
#        with open(inps.input, 'rb') as f:
#            frame = pickle.load(f)
#            d = frame.getProcessingSoftwareVersion()
#    else:
#        raise Exception('unknown input file format\n')
#
#
#    if ('.zip' in inps.input) or ('LED-ALOS' in inps.input):
#        d = d[0]
#        strp_3 = lambda x: str.strip(x.decode('utf-8')).rstrip('\x00')
#        d = strp_3(d)
#        version = d
#    else:
#        version = d
#
#
#
#    print('product version: {}'.format(version))
