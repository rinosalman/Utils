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

    # necessary files
    udir = '../upper'
    ldir = '../lower'
    intf1 = 'diff_220905-230220_1rlks_14alks.int'
    intf2 = 'filt_220905-230220_5rlks_28alks.int'

    # do operation on the original and unfiltered interferograms
    uintf = os.path.join(udir, 'insar/', intf1)
    lintf = os.path.join(ldir, 'insar/', intf1)
    residualintf ='diff_residual_1rlks_14alks_intf.int'
    runCmd("imageMath.py -e='a*exp(-1.0*J*arg(b))' --a={} --b={} -t cfloat -o {}".format(uintf,lintf,residualintf))


    # do operation on the multilooked and filtered interferograms
    uintf = os.path.join(udir, 'insar/', intf2)
    lintf = os.path.join(ldir, 'insar/', intf2)
    residualintf = intf2
    runCmd("imageMath.py -e='a*exp(-1.0*J*arg(b))' --a={} --b={} -t cfloat -o {}".format(uintf,lintf,residualintf))
