#!/usr/bin/env python3
# July 2023, Rino Salman, EOS-NTU

import os
import glob
import shutil
import datetime
import numpy as np
import xml.etree.ElementTree as ET

import isce, isceobj
from isceobj.Alos2Proc.Alos2ProcPublic import runCmd
from isceobj.Alos2Proc.Alos2ProcPublic import renameFile


if __name__ == '__main__':

    img = isceobj.createImage()
    img.load(glob.glob('lower*.int')[0] + '.xml')
    width = img.width
    length = img.length
    os.system('echo width={}, length={} > width_length_information'.format(width,length))
    wbdArguments = ''
    intf = glob.glob('lower*.int')[0]

    runCmd('mdx {} -s {} -c8pha -cmap cmy -wrap 6.283185307179586 -addr -3.141592653589793{} -P'.format(intf, width, wbdArguments))
