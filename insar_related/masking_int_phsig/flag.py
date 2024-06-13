#!/usr/bin/env python3

#Cunren Liang, JPL/Caltech, 2016

import os
import sys
import glob
import shutil
import pickle
import datetime
import argparse
import numpy as np
import numpy.matlib
import scipy.signal as ss
from xml.etree.ElementTree import ElementTree

import isce
import isceobj
from imageMath import IML
from isceobj.Alos2Proc.Alos2ProcPublic import create_xml

#from crlpac import getWidth
#from crlpac import getLength
#from crlpac import create_xml

def read_bands(filename, length, width, scheme, nbands, datatype):

    if datatype.upper() == 'FLOAT':
        datatype1 = np.float32
    elif datatype.upper() == 'CFLOAT':
        datatype1 = np.complex64
    elif datatype.upper() == 'DOUBLE':
        datatype1 = np.float64
    elif datatype.upper() == 'BYTE':
        datatype1 = np.int8

    elif datatype.upper() == 'UBYTE':
        datatype1 = np.uint8


    elif datatype.upper() == 'SHORT':
        datatype1 = np.int16
    else:
        raise Exception('data type not supported, please contact crl for your data type!')

    bands = []
    if scheme.upper() == 'BIP':
        data = np.fromfile(filename, dtype=datatype1).reshape(length, width*nbands)
        for i in range(nbands):
            bands.append(data[:, i:width*nbands:nbands])
    elif scheme.upper() == 'BIL':
        data = np.fromfile(filename, dtype=datatype1).reshape(length*nbands, width)
        for i in range(nbands):
            bands.append(data[i:length*nbands:nbands, :])
    elif scheme.upper() == 'BSQ':
        data = np.fromfile(filename, dtype=datatype1).reshape(length*nbands, width)
        for i in range(nbands):
            offset = length * i
            bands.append(data[0+offset:length+offset, :])        
    else:
        raise Exception('unknown band scheme!')

    return bands


if __name__ == '__main__':



    #width = 3041
    #length = 6156
    width = 5142
    length = 8782

    [r, g, b] = read_bands('out.data', length, width, 'BIP', 3, 'UBYTE')


    #flag = np.zeros((length, width))

    flag = ((r==0)*(g==0)*(b==0) == 0)
    flag.astype(np.float32).tofile('flag.float')
    create_xml('flag.float', width, length, 'float')



