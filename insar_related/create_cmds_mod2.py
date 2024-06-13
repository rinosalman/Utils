#!/usr/bin/env python3

#
# Author: Cunren Liang
# Copyright 2015-present, NASA-JPL/Caltech
# Modified by Rino Salman, March 2021

import os
import glob
import shutil
import datetime
import numpy as np
import xml.etree.ElementTree as ET

import isce, isceobj
from isceobj.Alos2Proc.Alos2ProcPublic import runCmd

from StackPulic import loadStackUserParameters
from StackPulic import loadInsarUserParameters
from StackPulic import acquisitionModesAlos2
from StackPulic import datesFromPairs


def checkDem(fileName):
    if fileName is None:
        raise Exception('dem for coregistration, dem for geocoding, water body must be set')
    else:
        if not os.path.isfile(fileName):
            raise Exception('file not found: {}'.format(fileName))
        else:
            img = isceobj.createDemImage()
            img.load(fileName+'.xml')
            if os.path.abspath(fileName) != img.filename:
                raise Exception('please use absolute path for <property name="file_name"> in {} xml file'.format(fileName))


def getFolders(directory):
    '''
    return sorted folders in a directory
    '''
    import os
    import glob

    folders = glob.glob(os.path.join(os.path.abspath(directory), '*'))
    folders = sorted([os.path.basename(x) for x in folders if os.path.isdir(x)])

    return folders


def unionLists(list1, list2):
    import copy

    list3 = copy.deepcopy(list1)

    for x in list2:
        if x not in list1:
            list3.append(x)

    return sorted(list3)


def removeCommonItemsLists(list1, list2):
    '''
    remove common items of list1 and list2 from list1
    '''

    import copy

    list3 = copy.deepcopy(list1)

    list4 = []
    for x in list1:
        if x in list2:
            list3.remove(x)
            list4.append(x)

    return (sorted(list3), sorted(list4))


def formPairs(idir, numberOfSubsequentDates, pairTimeSpanMinimum=None, pairTimeSpanMaximum=None, 
    datesIncluded=None, pairsIncluded=None, 
    datesExcluded=None, pairsExcluded=None):
    '''
    datesIncluded: list
    pairsIncluded: list
    datesExcluded: list
    pairsExcluded: list
    '''
    datefmt = "%y%m%d"

    #get date folders
    dateDirs = sorted(glob.glob(os.path.join(os.path.abspath(idir), '*')))
    dateDirs = [x for x in dateDirs if os.path.isdir(x)]
    dates = [os.path.basename(x) for x in dateDirs]
    ndate = len(dates)

    #check input parameters
    if datesIncluded is not None:
        if type(datesIncluded) != list:
            raise Exception('datesIncluded must be a list')
        for date in datesIncluded:
            if date not in dates:
                raise Exception('in datesIncluded, date {} is not found in data directory {}'.format(date, idir))

    if pairsIncluded is not None:
        if type(pairsIncluded) != list:
            raise Exception('pairsIncluded must be a list')
        #check reference must < secondary
        for pair in pairsIncluded:
            rdate = pair.split('-')[0]
            sdate = pair.split('-')[1]
            rtime = datetime.datetime.strptime(rdate, datefmt)
            stime = datetime.datetime.strptime(sdate, datefmt)
            if rtime >= stime:
                raise Exception('in pairsIncluded, first date must be reference') 
            if (sdate not in dates) or (mdate not in dates):
                raise Exception('in pairsIncluded, reference or secondary date of pair {} not in data directory {}'.format(pair, idir)) 

    if datesExcluded is not None:
        if type(datesExcluded) != list:
            raise Exception('datesExcluded must be a list')
    if pairsExcluded is not None:
        if type(pairsExcluded) != list:
            raise Exception('pairsExcluded must be a list')

    #get initial pairs to process
    pairsProcess = []
    for i in range(ndate):
        rdate = dates[i]
        rtime = datetime.datetime.strptime(rdate, datefmt)
        for j in range(numberOfSubsequentDates):
            if i+j+1 <= ndate - 1:
                sdate = dates[i+j+1]
                stime = datetime.datetime.strptime(sdate, datefmt)
                pair = rdate + '-' + sdate
                ts = np.absolute((stime - rtime).total_seconds()) / (365.0 * 24.0 * 3600)
                if pairTimeSpanMinimum is not None:
                    if ts < pairTimeSpanMinimum:
                        continue
                if pairTimeSpanMaximum is not None:
                    if ts > pairTimeSpanMaximum:
                        continue
                pairsProcess.append(pair)

    #included dates
    if datesIncluded is not None:
        pairsProcess2 = []
        for pair in pairsProcess:
            rdate = pair.split('-')[0]
            sdate = pair.split('-')[1]
            if (rdate in datesIncluded) or (sdate in datesIncluded):
                pairsProcess2.append(pair)
        pairsProcess = pairsProcess2

    #included pairs
    if pairsIncluded is not None:
        pairsProcess = pairsIncluded

    #excluded dates
    if datesExcluded is not None:
        pairsProcess2 = []
        for pair in pairsProcess:
            rdate = pair.split('-')[0]
            sdate = pair.split('-')[1]
            if (rdate not in datesIncluded) and (sdate not in datesIncluded):
                pairsProcess2.append(pair)
        pairsProcess = pairsProcess2

    #excluded pairs
    if pairsExcluded is not None:
        pairsProcess2 = []
        for pair in pairsProcess:
            if pair not in pairsExcluded:
               pairsProcess2.append(pair)
        pairsProcess = pairsProcess2

    # #datesProcess
    # datesProcess = []
    # for pair in pairsProcess:
    #     rdate = pair.split('-')[0]
    #     sdate = pair.split('-')[1]
    #     if rdate not in datesProcess:
    #         datesProcess.append(rdate)
    #     if sdate not in datesProcess:
    #         datesProcess.append(sdate)
    
    # datesProcess = sorted(datesProcess)
    pairsProcess = sorted(pairsProcess)

    #return (datesProcess, pairsProcess)
    return pairsProcess


def stackRank(dates, pairs):
    from numpy.linalg import matrix_rank

    dates = sorted(dates)
    pairs = sorted(pairs)
    ndate = len(dates)
    npair = len(pairs)

    #observation matrix
    H0 = np.zeros((npair, ndate))
    for k in range(npair):
        dateReference = pairs[k].split('-')[0]
        dateSecondary = pairs[k].split('-')[1]
        dateReference_i = dates.index(dateReference)
        H0[k, dateReference_i] = 1
        dateSecondary_i = dates.index(dateSecondary)
        H0[k, dateSecondary_i] = -1

    rank = matrix_rank(H0)

    return rank




def checkStackDataDir(idir):
    '''
    idir:          input directory where data of each date is located. only folders are recognized
    '''
    stack.dataDir

    #get date folders
    dateDirs = sorted(glob.glob(os.path.join(os.path.abspath(idir), '*')))
    dateDirs = [x for x in dateDirs if os.path.isdir(x)]

    #check dates and acquisition mode
    mode = os.path.basename(sorted(glob.glob(os.path.join(dateDirs[0], 'IMG-HH-ALOS2*')))[0]).split('-')[4][0:3]
    for x in dateDirs:
        dateFolder = os.path.basename(x)
        images = sorted(glob.glob(os.path.join(x, 'IMG-HH-ALOS2*')))
        leaders = sorted(glob.glob(os.path.join(x, 'LED-ALOS2*')))
        for y in images:
            dateFile   = os.path.basename(y).split('-')[3]
            if dateFolder != dateFile:
                raise Exception('date: {} in data folder name is different from date: {} in file name: {}'.format(dateFolder, dateFile, y))
            ymode = os.path.basename(y).split('-')[4][0:3]
            if mode != ymode:
                #currently only allows S or D polarization, Q should also be OK?
                if (mode[0:2] == ymode[0:2]) and (mode[2] in ['S', 'D']) and (ymode[2] in ['S', 'D']):
                    pass
                else:
                    raise Exception('all acquisition modes should be the same')

        for y in leaders:
            dateFile   = os.path.basename(y).split('-')[2]
            if dateFolder != dateFile:
                raise Exception('date: {} in data folder name is different from date: {} in file name: {}'.format(dateFolder, dateFile, y))
            ymode = os.path.basename(y).split('-')[3][0:3]
            if mode != ymode:
                #currently only allows S or D polarization, Q should also be OK?
                if (mode[0:2] == ymode[0:2]) and (mode[2] in ['S', 'D']) and (ymode[2] in ['S', 'D']):
                    pass
                else:
                    raise Exception('all acquisition modes should be the same')


def createCmds(stack, datesProcess, pairsProcess, pairsProcessIon, mode):
    '''
    create scripts to process an InSAR stack
    '''
    import os
    import copy

    stack.dem = os.path.abspath(stack.dem)
    stack.demGeo = os.path.abspath(stack.demGeo)
    stack.wbd = os.path.abspath(stack.wbd)

    insar = stack

    def header(txt):
        hdr  = '##################################################\n'
        hdr += '# {}\n'.format(txt)
        hdr += '##################################################\n'
        return hdr


    stackScriptPath = os.environ['PATH_ALOSSTACK']

    def parallelSettings(array):
        settings = '''
# For parallelly processing the dates/pairs.
# Uncomment and set the following variables, put these settings and the following
# one or multiple for loops for a group (with an individual group_i) in a seperate 
# bash script. Then you can run the different groups parallelly. E.g. if you have 
# 38 pairs and if you want to process them in 4 parallel runs, then you may set 
# group_n=10, and group_i=1 for the first bash script (and 2, 3, 4 for the other 
# three bash scripts).

# Number of threads for this run
# export OMP_NUM_THREADS=1

# CUDA device you want to use for this run. Only need to set if you have CUDA GPU
# installed on your computer. To find GPU IDs, run nvidia-smi
# export CUDA_VISIBLE_DEVICES=7

# Parallel processing mode. 0: no, 1 yes.
# Must set 'parallel=1' for parallel processing!
# parallel=1

# Group number for this run (group_i starts from 1)
# group_i=1

# Number of dates or pairs in a group
# group_n=10

# set the array variable used in this for loop here. The array can be found at the
# beginning of this command file.
# {}=()

'''.format(array)
        return settings

    parallelCommands = '''  if [[ ${parallel} -eq 1 ]]; then
    if !(((0+(${group_i}-1)*${group_n} <= ${i})) && ((${i} <= ${group_n}-1+(${group_i}-1)*${group_n}))); then
      continue
    fi
  fi'''

    print('                       * * *')
    if stack.dateReferenceStack in datesProcess:
        print('reference date of stack in date list to be processed.')
        if os.path.isfile(os.path.join(stack.datesResampledDir, stack.dateReferenceStack, 'insar', 'affine_transform.txt')):
            print('reference date of stack already processed previously.')
            print('do not implement reference-date-related processing this time.')
            processDateReferenceStack = False
        else:
            print('reference date of stack not processed previously.')
            print('implement reference-date-related processing this time.')
            processDateReferenceStack = True
    else:
        print('reference date of stack NOT in date list to be processed.')
        if not os.path.isfile(os.path.join(stack.datesResampledDir, stack.dateReferenceStack, 'insar', 'affine_transform.txt')):
            raise Exception('but it does not seem to have been processed previously.')
        else:
            print('assume it has already been processed previously.')
            print('do not implement reference-date-related processing this time.')
            processDateReferenceStack = False
    print('                       * * *')
    print()

    #WHEN PROVIDING '-sec_date' BECAREFUL WITH 'datesProcess' AND 'datesProcessSecondary'
    datesProcessSecondary = copy.deepcopy(datesProcess)
    if stack.dateReferenceStack in datesProcessSecondary:
        datesProcessSecondary.remove(stack.dateReferenceStack)

    #pairs also processed in regular InSAR processing
    pairsProcessIon1 = [ipair for ipair in pairsProcessIon if ipair in pairsProcess]
    #pairs  not processed in regular InSAR processing
    pairsProcessIon2 = [ipair for ipair in pairsProcessIon if ipair not in pairsProcess]


    #start new commands: processing each date
    #################################################################################
    cmd  = '#!/bin/bash\n'
    cmd += '\n'
    cmd += '#########################################################################\n'
    cmd += '#set the environment variable before running the following steps\n'
    cmd += '#########################################################################\n'
    cmd += 'dates=({})\n'.format(' '.join(datesProcessSecondary))
    cmd += '\n'


    #read data
    if datesProcess != []:
        cmd += header('read data')
        cmd += os.path.join(stackScriptPath, 'read_data.py') + ' -idir {} -odir {} -ref_date {} -sec_date {} -pol {}'.format(stack.dataDir, stack.datesProcessingDir, stack.dateReferenceStack, ' '.join(datesProcess), stack.polarization)
        if stack.frames is not None:
            cmd += ' -frames {}'.format(' '.join(stack.frames))
        if stack.startingSwath is not None:
            cmd += ' -starting_swath {}'.format(stack.startingSwath)
        if stack.endingSwath is not None:
            cmd += ' -ending_swath {}'.format(stack.endingSwath)
        if insar.useVirtualFile:
            cmd += ' -virtual'
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'
        #frame and swath names use those from frame and swath dirs from now on


    #compute baseline
    if datesProcessSecondary != []:
        cmd += header('compute baseline')
        cmd += os.path.join(stackScriptPath, 'compute_baseline.py') + ' -idir {} -odir {} -ref_date {} -sec_date {} -baseline_center baseline_center.txt -baseline_grid -baseline_grid_width 10 -baseline_grid_length 10'.format(stack.datesProcessingDir, stack.baselineDir, stack.dateReferenceStack, ' '.join(datesProcessSecondary))
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'


    #compute burst synchronization
    spotlightModes, stripmapModes, scansarNominalModes, scansarWideModes, scansarModes = acquisitionModesAlos2()
    if mode in scansarNominalModes:
        cmd += header('compute burst synchronization')
        cmd += os.path.join(stackScriptPath, 'compute_burst_sync.py') + ' -idir {} -burst_sync_file burst_synchronization.txt -ref_date {}'.format(stack.datesProcessingDir, stack.dateReferenceStack)
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'


    #estimate SLC offsets
    #################################################################################
    if datesProcessSecondary != []:
        cmd += header('estimate SLC offsets')
        cmd += '\n\n'
        cmd += '''for ((i=0;i<${#dates[@]};i++)); do

   qsub -v sec_date=${dates[i]} pbs_1a.pbs

done'''

    #save commands
    cmd1a = cmd


    #start new commands: estimate SLC offsets, .pbs file
    #################################################################################
    if datesProcessSecondary != []:
        extraArguments = ''
        if insar.useWbdForNumberOffsets is not None:
            extraArguments += '-use_wbd_offset'
        if insar.numberRangeOffsets is not None:
            for x in insar.numberRangeOffsets:
                extraArguments += '-num_rg_offset {}'.format(' '.join(x))
        if insar.numberAzimuthOffsets is not None:
            for x in insar.numberAzimuthOffsets:
                extraArguments += '-num_az_offset {}'.format(' '.join(x))

        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N SLC_offset\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $sec_date ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v sec_date=your-secondary-date"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # run code\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'estimate_slc_offset.py'))
        cmd += '   idir={}\n'.format(stack.datesProcessingDir)
        cmd += '   ref_date={}\n'.format(stack.dateReferenceStack)
        cmd += '   wbd={}\n'.format(insar.wbd)
        cmd += '   dem={}\n'.format(stack.dem)
        cmd += '\n'
        cmd += '   $code -idir $idir -ref_date $ref_date -sec_date $sec_date -wbd $wbd -dem $dem {}\n'.format(extraArguments)
        cmd += '\n'
        cmd += 'fi\n'

        #save commands
        pbs1a = cmd


    #start new commands: estimate swath and frame offsets, resample to a common grid
    #################################################################################
    #estimate swath offsets
    if processDateReferenceStack:
        cmd  = '#!/bin/bash\n\n'
        cmd += '\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '#########################################################################\n'
        cmd += 'dates=({})\n'.format(' '.join(datesProcess))
        cmd += header('estimate swath offsets')
        cmd += os.path.join(stackScriptPath, 'estimate_swath_offset.py') + ' -idir {} -date {} -output swath_offset.txt'.format(os.path.join(stack.datesProcessingDir, stack.dateReferenceStack), stack.dateReferenceStack)
        if insar.swathOffsetMatching:
            cmd += ' -match'
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'

    #estimate frame offsets
    if processDateReferenceStack:
        cmd += header('estimate frame offsets')
        cmd += os.path.join(stackScriptPath, 'estimate_frame_offset.py') + ' -idir {} -date {} -output frame_offset.txt'.format(os.path.join(stack.datesProcessingDir, stack.dateReferenceStack), stack.dateReferenceStack)
        if insar.frameOffsetMatching:
            cmd += ' -match'
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'


    #resample to a common grid
    #################################################################################
    if datesProcess != []:
        cmd += header('resample to a common grid')
        cmd += '\n'
        cmd += '\n'
        cmd += '''for ((i=0;i<${#dates[@]};i++)); do

   qsub -v sec_date=${dates[i]} pbs_1b.pbs

done'''

    #save commands
    cmd1b = cmd


    #start new commands: resample to a common grid, .pbs file
    #################################################################################
    if datesProcess != []:
        extraArguments = ''
        if stack.gridFrame is not None:
            extraArguments += '-ref_frame {}'.format(stack.gridFrame)
        if stack.gridSwath is not None:
            extraArguments += '-ref_swath {}'.format(stack.gridSwath)
        if insar.doIon:
            extraArguments += '-subband'

        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N Resampling\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $sec_date ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v sec_date=your-secondary-date"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # run code\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'resample_common_grid.py'))
        cmd += '   idir={}\n'.format(stack.datesProcessingDir)
        cmd += '   odir={}\n'.format(stack.datesResampledDir)
        cmd += '   ref_date={}\n'.format(stack.dateReferenceStack)
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += '   $code -idir $idir -odir $odir -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 {}\n'.format(extraArguments)
        cmd += '\n'
        cmd += 'fi\n'

        #save commands
        pbs1b = cmd


    #start new commands: mosaic parameter, compute lon/lat/hgt, compute geometrical offsets
    #######################################################################################
    if datesProcess != []:
        cmd  = '#!/bin/bash\n'
        cmd += '\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '#########################################################################\n'
        cmd += 'dates=({})\n'.format(' '.join(datesProcessSecondary))
        cmd += '\n'
        cmd += header('mosaic parameter')
        cmd += os.path.join(stackScriptPath, 'mosaic_parameter.py') + ' -idir {} -ref_date {} -sec_date {} -nrlks1 {} -nalks1 {}'.format(stack.datesProcessingDir, stack.dateReferenceStack, ' '.join(datesProcess), insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        if stack.gridFrame is not None:
            cmd += ' -ref_frame {}'.format(stack.gridFrame)
        if stack.gridSwath is not None:
            cmd += ' -ref_swath {}'.format(stack.gridSwath)
        cmd += '\n'

    if processDateReferenceStack:
        cmd += os.path.join(stackScriptPath, 'mosaic_parameter.py') + ' -idir {} -ref_date {} -sec_date {} -nrlks1 {} -nalks1 {}'.format(stack.datesResampledDir, stack.dateReferenceStack, stack.dateReferenceStack, insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        if stack.gridFrame is not None:
            cmd += ' -ref_frame {}'.format(stack.gridFrame)
        if stack.gridSwath is not None:
            cmd += ' -ref_swath {}'.format(stack.gridSwath)
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'
    else:
        cmd += '\n'
        cmd += '\n'


    #compute lat/lon/hgt
    if processDateReferenceStack:
        cmd += header('compute latitude, longtitude and height')
        cmd += 'cd {}\n'.format(os.path.join(stack.datesResampledDir, stack.dateReferenceStack))
        cmd += os.path.join(stackScriptPath, 'rdr2geo.py') + ' -date {} -dem {} -wbd {} -nrlks1 {} -nalks1 {}'.format(stack.dateReferenceStack, stack.dem, insar.wbd, insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        if insar.useGPU:
            cmd += ' -gpu'
        cmd += '\n'

        # #should move it to look section???!!!
        # cmd += os.path.join(stackScriptPath, 'look_geom.py') + ' -date {} -wbd {} -nrlks1 {} -nalks1 {} -nrlks2 {} -nalks2 {}'.format(stack.dateReferenceStack, insar.wbd, insar.numberRangeLooks1, insar.numberAzimuthLooks1, insar.numberRangeLooks2, insar.numberAzimuthLooks2)
        # cmd += '\n'

        cmd += 'cd ../../'
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'


    #compute geometrical offsets
    if datesProcessSecondary != []:
        #################################################################################
        cmd += '\n\n'
        cmd += header('compute geometrical offsets')
        cmd += '\n\n'
        cmd += '''for ((i=0;i<${#dates[@]};i++)); do

   qsub -v sec_date=${dates[i]} pbs_1c.pbs

done'''

    #save commands
    cmd1c = cmd


    #start new commands: compute geometrical offsets, .pbs file
    #################################################################################
    if datesProcessSecondary != []:
        extraArguments = ''
        if insar.useGPU:
            extraArguments += ' -gpu'
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N GeometricalOffsets\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $sec_date ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v sec_date=your-secondary-date"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # go to working directory\n'
        cmd += '   cd dates_resampled/$sec_date\n'
        cmd += '\n'
        cmd += '   # run code\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'geo2rdr.py'))
        cmd += '   dateParDir=../../{}/$sec_date\n'.format(stack.datesProcessingDir)
        cmd += '   lat=../{}/insar/{}_{}rlks_{}alks.lat\n'.format(stack.dateReferenceStack, stack.dateReferenceStack, insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += '   lon=../{}/insar/{}_{}rlks_{}alks.lon\n'.format(stack.dateReferenceStack, stack.dateReferenceStack, insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += '   hgt=../{}/insar/{}_{}rlks_{}alks.hgt\n'.format(stack.dateReferenceStack, stack.dateReferenceStack, insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += '   $code -date $sec_date -date_par_dir $dateParDir -lat $lat -lon $lon -hgt $hgt -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 {}\n'.format(extraArguments)
        cmd += '   cd ../../'
        cmd += '\n\n'
        cmd += 'fi\n'


        #save commands
        pbs1c = cmd


    #start new commands: pair up scenes, form and mosaic interferograms
    #################################################################################
    if pairsProcess != []:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '#########################################################################\n'
        cmd += 'insarpair=({})\n'.format(' '.join(pairsProcess))
        cmd += '#########################################################################\n'
        cmd += '\n\n'
    else:
        cmd  = '#!/bin/bash\n'
        cmd += '#no pairs for InSAR processing.'


    #pair up
    if pairsProcess != []:
        cmd += header('pair up')
        cmd += os.path.join(stackScriptPath, 'pair_up.py') + ' -idir1 {} -idir2 {} -odir {} -ref_date {} -pairs {}'.format(stack.datesProcessingDir, stack.datesResampledDir, stack.pairsProcessingDir, stack.dateReferenceStack, ' '.join(pairsProcess))
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'


    #form and mosaic interferograms
    if pairsProcess != []:
        #################################################################################
        cmd += header('form and mosaic interferograms')
        cmd += '\n\n'
        cmd += '''for ((i=0;i<${#insarpair[@]};i++)); do

   qsub -v pair=${insarpair[i]} pbs_2a.pbs

done'''

    #save commands
    cmd2a = cmd


    #start new commands: form and mosaic interferograms, .pbs file
    #################################################################################
    if pairsProcess != []:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N FormMosaicInterferogram\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $pair ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v pair=your-pair"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # go to working directory\n'
        cmd += '   cd pairs/$pair\n'
        cmd += '\n'
        cmd += '   #form interferogram\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'form_interferogram.py'))
        cmd += "   ref_date=`echo $pair | awk -F- '{print $1}'`\n"
        cmd += "   sec_date=`echo $pair | awk -F- '{print $2}'`\n"
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += '   $code -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1\n'
        cmd += '\n'
        cmd += '   #mosaic interferograms\n'
        cmd += '   ref_date_stack={}\n'.format(stack.dateReferenceStack)
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'mosaic_interferogram.py'))
        cmd += '\n'
        cmd += '   $code -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1\n'
        cmd += '   cd ../../'
        cmd += '\n\n'
        cmd += 'fi\n'

        #save commands
        pbs2a = cmd


    #start new commands: estimate residual offsets between radar and DEM, rectify range offsets
    if processDateReferenceStack:
    #if not os.path.isfile(os.path.join(stack.datesResampledDir, stack.dateReferenceStack, 'insar', 'affine_transform.txt')):
        #amplitde image of any pair should work, since they are all coregistered now
        if pairsProcess == []:
            pairsProcessTmp = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(stack.pairsProcessingDir, '*'))) if os.path.isdir(x)]
        else:
            pairsProcessTmp = pairsProcess
        if pairsProcessTmp == []:
            raise Exception('no InSAR pairs available for estimating residual offsets between radar and DEM')
        for x in pairsProcessTmp:
            if stack.dateReferenceStack in x.split('-'):
                pairToUse = x
                break

        cmd  = '#!/bin/bash\n\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '#########################################################################\n'
        cmd += 'dates=({})\n'.format(' '.join(datesProcessSecondary))
        cmd += '#########################################################################\n'
        cmd += '\n'
        cmd += header('estimate residual offsets between radar and DEM')
        cmd += '\n'
        cmd += '# run code\n'
        cmd += 'code={}\n'.format(os.path.join(stackScriptPath, 'radar_dem_offset.py'))
        cmd += 'track={}.track.xml\n'.format(stack.dateReferenceStack)
        cmd += 'dem={}\n'.format(stack.dem)
        cmd += 'wbd={}_{}rlks_{}alks.wbd\n'.format(os.path.join('insar', stack.dateReferenceStack), insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += 'hgt={}_{}rlks_{}alks.hgt\n'.format(os.path.join('insar', stack.dateReferenceStack), insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += 'amp={}_{}rlks_{}alks.amp\n'.format(os.path.join('../../', stack.pairsProcessingDir, pairToUse, 'insar', pairToUse), insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += 'numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += 'numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += 'cd {}/{}\n'.format(stack.datesResampledDir,stack.dateReferenceStack)
        cmd += '$code -track $track -dem $dem -wbd $wbd -hgt $hgt -amp $amp -output affine_transform.txt -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1\n'
        if insar.numberRangeLooksSim is not None:
            cmd += ' -nrlks_sim {}'.format(insar.numberRangeLooksSim)
        if insar.numberAzimuthLooksSim is not None:
            cmd += ' -nalks_sim {}'.format(insar.numberAzimuthLooksSim)
        cmd += 'cd ../../'
        cmd += '\n\n'


    #rectify range offsets
    if datesProcessSecondary != []:
        cmd += header('rectify range offsets')
        cmd += '\n\n'
        cmd += '''for ((i=0;i<${#dates[@]};i++)); do

   qsub -v date=${dates[i]} pbs_2b.pbs

done'''

    #save commands
    cmd2b = cmd


    #start new commands: rectify range offsets, .pbs file
    #################################################################################
    if datesProcessSecondary != []:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N RectifyRangeOffsets\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $date ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v date=your-secondary-date"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # go to working directory\n'
        cmd += '   cd dates_resampled/$date/insar\n'
        cmd += '\n'
        cmd += '   # run code\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'rect_range_offset.py'))
        cmd += '   aff={}\n'.format(os.path.join('../../', stack.dateReferenceStack, 'insar', 'affine_transform.txt'))
        cmd += "   input=$date'_{}rlks_{}alks_rg.off'\n".format(insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += "   output=$date'_{}rlks_{}alks_rg_rect.off'\n".format(insar.numberRangeLooks1, insar.numberAzimuthLooks1)
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += '   $code -aff $aff -input $input -output $output -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1\n'
        cmd += '   cd ../../../'
        cmd += '\n\n'
        cmd += 'fi\n'

    #save commands
    pbs2b = cmd


    #start new commands: diff interferograms, look and coherence, .sh file
    if pairsProcess != []:
        cmd  = '#!/bin/bash\n\n'
        cmd += header('diff interferograms, look and coherence')
        cmd += '\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += '#########################################################################\n'
        cmd += 'insarpair=({})\n'.format(' '.join(pairsProcess))
        cmd += '\n'
        cmd += '''for ((i=0;i<${#insarpair[@]};i++)); do

   qsub -v pair=${insarpair[i]} pbs_2c.pbs

done'''

        #save commands
        cmd2c = cmd


        #start new commands: diff interferograms, look and coherence, look geom, .pbs file
        #################################################################################
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N DiffLookCoherence\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $pair ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v pair=your-pair"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # go to working directory\n'
        cmd += '   cd pairs/$pair\n'
        cmd += '\n'
        cmd += '   #diff interferogram\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'diff_interferogram.py'))
        cmd += '   idir={}\n'.format(os.path.join('../../', stack.datesResampledDir))
        cmd += "   ref_date=`echo $pair | awk -F- '{print $1}'`\n"
        cmd += "   sec_date=`echo $pair | awk -F- '{print $2}'`\n"
        cmd += '   ref_date_stack={}\n'.format(stack.dateReferenceStack)
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '\n'
        cmd += '   $code -idir $idir -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1\n'
        cmd += '\n'
        if (pairsProcess != []) or processDateReferenceStack:
            if pairsProcess != []:
               cmd += '   #look and coherence\n'
               cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'look_coherence.py'))
               cmd += '   numberRangeLooks2={}\n'.format(insar.numberRangeLooks2)
               cmd += '   numberAzimuthLooks2={}\n'.format(insar.numberAzimuthLooks2)
               cmd += '\n'
               cmd += '   $code -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 -nrlks2 $numberRangeLooks2 -nalks2 $numberAzimuthLooks2\n'
 
               cmd += '   cd ../../\n'
        cmd += '\n'
        cmd += '\n'
        cmd += 'fi\n'

        #save commands
        pbs2c = cmd


    #start new commands: look geom, pair up, ionospheric phase estimation
    if insar.doIon and (pairsProcessIon != []):
        #start new commands: ionospheric phase estimation
        #################################################################################
        cmd  = '#!/bin/bash\n\n'
        cmd += '#########################################################################\n'
        cmd += '#set the environment variable before running the following steps\n'
        cmd += 'ionpair=({})\n'.format(' '.join(pairsProcessIon))
        cmd += '#########################################################################\n'
        cmd += '\n'
        if processDateReferenceStack:
           cmd += header('look geom')
           cmd += '\n'
           cmd += 'code={}\n'.format(os.path.join(stackScriptPath, 'look_geom.py'))
           cmd += 'wbd={}\n'.format(insar.wbd)
           cmd += 'ref_date_stack={}\n'.format(stack.dateReferenceStack)
           cmd += 'numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
           cmd += 'numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
           cmd += 'numberRangeLooks2={}\n'.format(insar.numberRangeLooks2)
           cmd += 'numberAzimuthLooks2={}\n'.format(insar.numberAzimuthLooks2)
           cmd += '\n'
           cmd += 'cd {}/$ref_date_stack\n'.format(stack.datesResampledDir)
           cmd += '$code -date $ref_date_stack -wbd $wbd -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 -nrlks2 $numberRangeLooks2 -nalks2 $numberAzimuthLooks2\n'
           cmd += 'cd ../../\n\n'
        cmd += header('pair up for ionospheric phase estimation')
        cmd += 'code={}\n'.format(os.path.join(stackScriptPath, 'pair_up.py'))
        cmd += 'idir1={}\n'.format(stack.datesProcessingDir)
        cmd += 'idir2={}\n'.format(stack.datesResampledDir)
        cmd += 'odir={}\n'.format(stack.pairsProcessingDirIon)
        cmd += 'ref_date_stack={}\n'.format(stack.dateReferenceStack)
        cmd += '$code -idir1 $idir1 -idir2 $idir2 -odir $odir -ref_date $ref_date_stack -pairs {}\n'.format(' '.join(pairsProcessIon))
        cmd += '\n\n'


    #ionospheric phase estimation
    if insar.doIon and (pairsProcessIon != []):
        cmd += header('ionospheric phase estimation')
        cmd += '\n\n'
        cmd += '''for ((i=0;i<${#ionpair[@]};i++)); do

   qsub -v ionpair=${ionpair[i]} pbs_3a.pbs

done'''

    #save commands
    cmd3a = cmd


    #start new commands: ionospheric phase estimation, .pbs file
    #################################################################################
    if insar.doIon and (pairsProcessIon != []):
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N IonosphericPhaseEstimation\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $ionpair ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v ionpair=your-ion-pair"\n'
        cmd += 'else\n'
        cmd += '\n'
        cmd += '   # go to working directory\n'
        cmd += '   cd pairs_ion/$ionpair\n'
        cmd += '\n'
        cmd += '   #subband interferograms\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'ion_subband.py'))
        cmd += '   idir={}\n'.format(os.path.join('../../', stack.datesResampledDir))
        cmd += '   ref_date_stack={}\n'.format(stack.dateReferenceStack)
        cmd += "   ref_date=`echo $ionpair | awk -F- '{print $1}'`\n"
        cmd += "   sec_date=`echo $ionpair | awk -F- '{print $2}'`\n"
        cmd += '   numberRangeLooks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   numberAzimuthLooks1={}\n'.format(insar.numberAzimuthLooks1)
        #subband interferograms
        if insar.swathPhaseDiffSnapIon is not None:
            snap = [[1 if y else 0 for y in x] for x in insar.swathPhaseDiffSnapIon]
            snapArgument = ' ' + ' '.join(['-snap {}'.format(' '.join([str(y) for y in x])) for x in snap])
        else:
            snapArgument = ''
        cmd += '\n'
        cmd += '   $code -idir $idir -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 {}\n\n'.format(snapArgument)
        #unwrap subband interferograms
        if insar.filterSubbandInt:
            filtArgument = ' -filt -alpha {} -win {} -step {}'.format(insar.filterStrengthSubbandInt, insar.filterWinsizeSubbandInt, insar.filterStepsizeSubbandInt)
            if not insar.removeMagnitudeBeforeFilteringSubbandInt:
                 filtArgument += ' -keep_mag'
        else:
            filtArgument = ''

        cmd += '   #unwrap subband interferograms\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'ion_unwrap.py'))
        cmd += '   wbd={}\n'.format(insar.wbd)
        cmd += '   nrlksIon={}\n'.format(insar.numberRangeLooksIon)
        cmd += '   nalksIon={}\n'.format(insar.numberAzimuthLooksIon)
        cmd += '\n'
        cmd += '   $code -idir $idir -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -wbd $wbd -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 -nrlks_ion $nrlksIon -nalks_ion $nalksIon {}\n'.format(filtArgument)


        #filter ionosphere
        filtArgument = ''
        if insar.fitIon:
            filtArgument += ' -fit'
        if insar.filtIon:
            filtArgument += ' -filt'
        if insar.fitAdaptiveIon:
            filtArgument += ' -fit_adaptive'
        if insar.filtSecondaryIon:
            filtArgument += ' -filt_secondary -win_secondary {}'.format(insar.filteringWinsizeSecondaryIon)
        if insar.filterStdIon is not None:
            filtArgument += ' -filter_std_ion {}'.format(insar.filterStdIon)
        if insar.maskedAreasIon is not None:
            filtArgument += ''.join([' -masked_areas '+' '.join([str(y) for y in x]) for x in insar.maskedAreasIon])

        cmd += '\n'
        cmd += '   # filter ionosphere\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'ion_filt.py'))
        cmd += '   idir2={}\n'.format(os.path.join('../../', stack.datesProcessingDir))
        cmd += '   wbd={}\n'.format(insar.wbd)
        cmd += '   numberRangeLooks2={}\n'.format(insar.numberRangeLooks2)
        cmd += '   numberAzimuthLooks2={}\n'.format(insar.numberAzimuthLooks2)
        cmd += '   winMin={}\n'.format(insar.filteringWinsizeMinIon)
        cmd += '   winMax={}\n'.format(insar.filteringWinsizeMaxIon)
        cmd += '\n'
        cmd += '   $code -idir $idir -idir2 $idir2 -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $numberRangeLooks1 -nalks1 $numberAzimuthLooks1 -nrlks2 $numberRangeLooks2 -nalks2 $numberAzimuthLooks2 -nrlks_ion $nrlksIon -nalks_ion $nalksIon -win_min $winMin -win_max $winMax {}\n'.format(filtArgument)
        cmd += '\n'
        cmd += '   cd ../../'
        cmd += '\n\n'
        cmd += 'fi\n'

        #save commands
        pbs3a = cmd


        #start new commands: prepare interferograms for checking ionospheric correction
        if pairsProcessIon1 != []:
           if (insar.numberRangeLooksIon != 1) or (insar.numberAzimuthLooksIon != 1):
              cmd  = '#!/bin/bash\n\n'
              cmd += '\n'
              cmd += '#########################################################################\n'
              cmd += '#set the environment variable before running the following steps\n'
              cmd += 'ionpair=({})\n'.format(' '.join(pairsProcessIon))
              cmd += 'ionpair1=({})\n'.format(' '.join(pairsProcessIon1))
              cmd += 'ionpair2=({})\n'.format(' '.join(pairsProcessIon2))
              cmd += 'insarpair=({})\n'.format(' '.join(pairsProcess))
              cmd += '#########################################################################\n'
              cmd += '\n'
              cmd += header('prepare interferograms for checking ionosphere estimation results')
              cmd += '''for ((i=0;i<${{#ionpair1[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair1[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  {script} -i {pairsProcessingDir}/${{ionpair1[i]}}/insar/diff_${{ionpair1[i]}}_{nrlks1}rlks_{nalks1}alks.int -o {pairsProcessingDirIon}/${{ionpair1[i]}}/ion/ion_cal/diff_${{ionpair1[i]}}_{nrlks}rlks_{nalks}alks_ori.int -r {nrlks_ion} -a {nalks_ion}

done'''.format(script              = os.path.join('', 'looks.py'),
               pairsProcessingDir  = stack.pairsProcessingDir.strip('/'),
               pairsProcessingDirIon  = stack.pairsProcessingDirIon.strip('/'),
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1,
               nrlks_ion           = insar.numberRangeLooksIon,
               nalks_ion           = insar.numberAzimuthLooksIon,
               nrlks               = insar.numberRangeLooks1 * insar.numberRangeLooksIon, 
               nalks               = insar.numberAzimuthLooks1 * insar.numberAzimuthLooksIon)
              cmd += '\n'
              cmd += '\n'
              cmd += '\n'
           else:
              cmd += '''for ((i=0;i<${{#ionpair1[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair1[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cp {pairsProcessingDir}/${{ionpair1[i]}}/insar/diff_${{ionpair1[i]}}_{nrlks1}rlks_{nalks1}alks.int* {pairsProcessingDirIon}/${{ionpair1[i]}}/ion/ion_cal

done'''.format(pairsProcessingDir  = stack.pairsProcessingDir.strip('/'),
               pairsProcessingDirIon  = stack.pairsProcessingDirIon.strip('/'),
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1)
              cmd += '\n'
              cmd += '\n'
              cmd += '\n'


        if pairsProcessIon2 != []:
           cmd  = '#!/bin/bash\n\n'
           cmd += header('prepare interferograms for checking ionosphere estimation results')
           cmd += '\n'
           cmd += '#########################################################################\n'
           cmd += '#set the environment variable before running the following steps\n'
           cmd += 'ionpair=({})\n'.format(' '.join(pairsProcessIon))
           cmd += 'ionpair1=({})\n'.format(' '.join(pairsProcessIon1))
           cmd += 'ionpair2=({})\n'.format(' '.join(pairsProcessIon2))
           cmd += 'insarpair=({})\n'.format(' '.join(pairsProcess))
           cmd += '#########################################################################\n'
           cmd += '\n'

           cmd += '''for ((i=0;i<${{#ionpair2[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair2[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cd {pairsProcessingDir}
  cd ${{ionpair2[i]}}
  {script} -ref_date ${{ref_date}} -sec_date ${{sec_date}} -nrlks1 {nrlks1} -nalks1 {nalks1}
  cd ../../

done'''.format(script              = os.path.join(stackScriptPath, 'form_interferogram.py'),
               pairsProcessingDir  = stack.pairsProcessingDirIon,
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1)
           cmd += '\n'
           cmd += '\n'

           cmd += '''for ((i=0;i<${{#ionpair2[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair2[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cd {pairsProcessingDir}
  cd ${{ionpair2[i]}}
  {script} -ref_date_stack {ref_date_stack} -ref_date ${{ref_date}} -sec_date ${{sec_date}} -nrlks1 {nrlks1} -nalks1 {nalks1}
  cd ../../

done'''.format(script              = os.path.join(stackScriptPath, 'mosaic_interferogram.py'),
               pairsProcessingDir  = stack.pairsProcessingDirIon,
               ref_date_stack      = stack.dateReferenceStack,
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1)
           cmd += '\n'
           cmd += '\n'

           cmd += '''for ((i=0;i<${{#ionpair2[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair2[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cd {pairsProcessingDir}
  cd ${{ionpair2[i]}}
  {script} -idir {idir} -ref_date_stack {ref_date_stack} -ref_date ${{ref_date}} -sec_date ${{sec_date}} -nrlks1 {nrlks1} -nalks1 {nalks1}
  cd ../../

done'''.format(script              = os.path.join(stackScriptPath, 'diff_interferogram.py'),
               pairsProcessingDir  = stack.pairsProcessingDirIon,
               idir                = os.path.join('../../', stack.datesResampledDir),
               ref_date_stack      = stack.dateReferenceStack,
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1)
           cmd += '\n'
           cmd += '\n'

           if (insar.numberRangeLooksIon != 1) or (insar.numberAzimuthLooksIon != 1):
              cmd += '''for ((i=0;i<${{#ionpair2[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair2[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  {script} -i {pairsProcessingDir}/${{ionpair2[i]}}/insar/diff_${{ionpair2[i]}}_{nrlks1}rlks_{nalks1}alks.int -o {pairsProcessingDir}/${{ionpair2[i]}}/ion/ion_cal/diff_${{ionpair2[i]}}_{nrlks}rlks_{nalks}alks_ori.int -r {nrlks_ion} -a {nalks_ion}

done'''.format(script              = os.path.join('', 'looks.py'),
               pairsProcessingDir  = stack.pairsProcessingDirIon.strip('/'),
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1,
               nrlks_ion           = insar.numberRangeLooksIon,
               nalks_ion           = insar.numberAzimuthLooksIon,
               nrlks               = insar.numberRangeLooks1 * insar.numberRangeLooksIon, 
               nalks               = insar.numberAzimuthLooks1 * insar.numberAzimuthLooksIon)
              cmd += '\n'
              cmd += '\n'
              cmd += '\n'
           else:
              cmd += '''for ((i=0;i<${{#ionpair2[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair2[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cp {pairsProcessingDir}/${{ionpair2[i]}}/insar/diff_${{ionpair2[i]}}_{nrlks1}rlks_{nalks1}alks.int* {pairsProcessingDir}/${{ionpair2[i]}}/ion/ion_cal

done'''.format(pairsProcessingDir  = stack.pairsProcessingDirIon.strip('/'),
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1)
              cmd += '\n'
              cmd += '\n'
              cmd += '\n'


        #check ionosphere estimation results
        cmd += header('check ionosphere estimation results')
        cmd += '''for ((i=0;i<${{#ionpair[@]}};i++)); do

  IFS='-' read -ra dates <<< "${{ionpair[i]}}"
  ref_date=${{dates[0]}}
  sec_date=${{dates[1]}}

  cd {pairsProcessingDir}
  cd ${{ionpair[i]}}
  {script} -e='a*exp(-1.0*J*b)' --a=ion/ion_cal/diff_${{ionpair[i]}}_{nrlks}rlks_{nalks}alks_ori.int --b=ion/ion_cal/filt_ion_{nrlks}rlks_{nalks}alks.ion -s BIP -t cfloat -o ion/ion_cal/diff_${{ionpair[i]}}_{nrlks}rlks_{nalks}alks.int
  cd ../../

done'''.format(script              = os.path.join('', 'imageMath.py'),
               pairsProcessingDir  = stack.pairsProcessingDirIon,
               nrlks               = insar.numberRangeLooks1*insar.numberRangeLooksIon, 
               nalks               = insar.numberAzimuthLooks1*insar.numberAzimuthLooksIon)
        cmd += '\n'
        cmd += '\n'

        cmd += os.path.join(stackScriptPath, 'ion_check.py') + ' -idir {} -odir fig_ion -pairs {}'.format(stack.pairsProcessingDirIon, ' '.join(pairsProcessIon))
        cmd += '\n'
        cmd += '\n'
        cmd += '\n'

 
        #save commands
        cmd3b = cmd


        #start new commands: estimate ionospheric phase for each date
        #################################################################################
        cmd  = '#!/bin/bash\n'
        cmd += '\n'
        #estimate ionospheric phase for each date
        cmd += header('estimate ionospheric phase for each date')
        cmd += "#check the ionospheric phase estimation results in folder 'fig_ion', and find out the bad pairs.\n"
        cmd += '#these pairs should be excluded from this step by specifying parameter -exc_pair. For example:\n'
        cmd += '#-exc_pair 150401-150624 150401-150722\n\n'
        cmd += '#MUST re-run all the following commands, each time after running this command!!!\n'
        cmd += '#uncomment to run this command\n'
        cmd += '#'
        cmd += os.path.join(stackScriptPath, 'ion_ls.py') + ' -idir {} -odir {} -ref_date_stack {} -nrlks1 {} -nalks1 {} -nrlks2 {} -nalks2 {} -nrlks_ion {} -nalks_ion {} -interp\n\n\n'.format(stack.pairsProcessingDirIon, stack.datesDirIon, stack.dateReferenceStack, insar.numberRangeLooks1, insar.numberAzimuthLooks1, insar.numberRangeLooks2, insar.numberAzimuthLooks2, insar.numberRangeLooksIon, insar.numberAzimuthLooksIon)
        if stack.dateReferenceStackIon is not None:
           cmd += ' -zro_date {}'.format(stack.dateReferenceStackIon)
           cmd += '\n'
           cmd += '\n'
           cmd += '\n'


        #correct ionosphere
        if insar.applyIon:
           cmd += header('correct ionosphere')
           cmd += '#no need to run parallelly for this for loop, it is fast!!!\n'
           cmd += '''#redefine insarpair to include all processed InSAR pairs
insarpair=($(ls -l {pairsProcessingDir} | grep ^d | awk '{{print $9}}'))
for ((i=0;i<${{#insarpair[@]}};i++)); do

   IFS='-' read -ra dates <<< "${{insarpair[i]}}"
   ref_date=${{dates[0]}}
   sec_date=${{dates[1]}}

   cd {pairsProcessingDir}
   cd ${{insarpair[i]}}
   #uncomment to run this command
   #{script} -ion_dir {ion_dir} -ref_date ${{ref_date}} -sec_date ${{sec_date}} -nrlks1 {nrlks1} -nalks1 {nalks1} -nrlks2 {nrlks2} -nalks2 {nalks2}
   cd ../../

done'''.format(script              = os.path.join(stackScriptPath, 'ion_correct.py'),
               pairsProcessingDir  = stack.pairsProcessingDir,
               ion_dir             = os.path.join('../../', stack.datesDirIon),
               nrlks1              = insar.numberRangeLooks1, 
               nalks1              = insar.numberAzimuthLooks1,
               nrlks2              = insar.numberRangeLooks2,
               nalks2              = insar.numberAzimuthLooks2)
           cmd += '\n'
           cmd += '\n'

        cmd += '#########################################################################\n'
        cmd += '#processing each pair after ionosphere correction\n'
        cmd += '#########################################################################\n'
        cmd += '''for ((i=0;i<${#insarpair[@]};i++)); do

   qsub -v insarpair=${insarpair[i]} pbs_3c.pbs

done'''


    else:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#no pairs for estimating ionosphere.'

    #save commands
    cmd3c = cmd


    #################################################################################
    #start new commands: processing each pair after ionosphere correction
    ################################################################################# 
    if True:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#PBS -N FilterUnwrapInterferogram\n'
        cmd += '#PBS -P eos_ehill\n'
        cmd += '#PBS -q q32\n'
        cmd += '#PBS -l walltime=120:00:00\n'
        cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
        cmd += '\n'
        cmd += '# go to working directory\n'
        cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
        cmd += 'cd $PBS_O_WORKDIR\n'
        cmd += '\n'
        cmd += '# load isce\n'
        cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
        cmd += '\n'
        cmd += '# set option\n'
        cmd += 'if [[ -z $insarpair ]]; then\n'
        cmd += '   echo "$0 ERROR: need to specify secondary date, using -v insarpair=your-insar-pair"\n'
        cmd += 'else\n'
        cmd += '\n'

        #filter interferograms
        extraArguments = ''
        if not insar.removeMagnitudeBeforeFiltering:
            extraArguments += '-keep_mag'
        if insar.waterBodyMaskStartingStep == 'filt':
            extraArguments += '-wbd_msk'

        cmd += '   #filter interferograms\n'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'filt.py'))
        cmd += '   idir={}\n'.format(os.path.join('../../', stack.datesResampledDir))
        cmd += '   ref_date_stack={}\n'.format(stack.dateReferenceStack)
        cmd += "   ref_date=`echo $insarpair | awk -F- '{print $1}'`\n"
        cmd += "   sec_date=`echo $insarpair | awk -F- '{print $2}'`\n"
        cmd += '   nrlks1={}\n'.format(insar.numberRangeLooks1)
        cmd += '   nalks1={}\n'.format(insar.numberAzimuthLooks1)
        cmd += '   nrlks2={}\n'.format(insar.numberRangeLooks2)
        cmd += '   nalks2={}\n'.format(insar.numberAzimuthLooks2)
        cmd += '   alpha={}\n'.format(insar.filterStrength)
        cmd += '   win={}\n'.format(insar.filterWinsize)
        cmd += '   step={}\n'.format(insar.filterStepsize)
        cmd += '\n'
        cmd += '   cd {}/$insarpair\n'.format(stack.pairsProcessingDir)
        cmd += '\n'
        cmd += '   $code -idir $idir -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $nrlks1 -nalks1 $nalks1 -nrlks2 $nrlks2 -nalks2 $nalks2 -alpha $alpha -win $win -step $step {}\n'.format(extraArguments)
        cmd += '\n\n'
        cmd += '   #unwrap interferograms\n'
        extraArguments = ''
        if insar.waterBodyMaskStartingStep == 'unwrap':
            extraArguments += ' -wbd_msk'
        cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'unwrap_snaphu.py'))
        cmd += '   $code -idir $idir -ref_date_stack $ref_date_stack -ref_date $ref_date -sec_date $sec_date -nrlks1 $nrlks1 -nalks1 $nalks1 -nrlks2 $nrlks2 -nalks2 $nalks2 {}\n'.format(extraArguments)
        cmd += '\n'
        extraArguments = ''
        if insar.geocodeInterpMethod is not None:
            extraArguments += '-interp_method {}'.format(insar.geocodeInterpMethod)
        if insar.bbox is not None:
            extraArguments += ' -bbox {} {} {} {}'.format(insar.bbox[0],insar.bbox[1],insar.bbox[2],insar.bbox[3])
        cmd += '\n'
        cmd += '   #geocode\n'
        #cmd += '   code={}\n'.format(os.path.join(stackScriptPath, 'geocode.py'))
        cmd += '   code=/home/rino/scripts/insarscripts/geo.py\n'
        cmd += '   dem={}\n'.format(stack.demGeo)
        cmd += '   xmlFile=../{}.track.xml\n'.format(stack.dateReferenceStack)
        cmd += '   nrlks={}\n'.format(insar.numberRangeLooks1*insar.numberRangeLooks2)
        cmd += '   nalks={}\n'.format(insar.numberAzimuthLooks1*insar.numberAzimuthLooks2)
        cmd += "   cor=$insarpair'_'$nrlks'rlks_'$nalks'alks.cor'\n"
        cmd += "   unw=filt_$insarpair'_'$nrlks'rlks_'$nalks'alks.unw'\n"
        cmd += "   mskUnw=filt_$insarpair'_'$nrlks'rlks_'$nalks'alks_msk.unw'\n"
        cmd += "   los={}_$nrlks'rlks_'$nalks'alks.los'\n".format(stack.dateReferenceStack)
        cmd += '\n'
        cmd += '   cd insar\n'
        cmd += '   $code -ref_date_stack_track $xmlFile -dem $dem -input $cor -nrlks $nrlks -nalks $nalks {}\n'.format(extraArguments)
        cmd += '   $code -ref_date_stack_track $xmlFile -dem $dem -input $unw -nrlks $nrlks -nalks $nalks {}\n'.format(extraArguments)
        cmd += '   $code -ref_date_stack_track $xmlFile -dem $dem -input $mskUnw -nrlks $nrlks -nalks $nalks {}\n'.format(extraArguments)
        cmd += '   cd ../../../\n'
        cmd += '\n'
        cmd += "   onepair=($(ls -l {pairsProcessingDir} | grep ^d | awk 'NR==1{{print $9}}'))\n".format(pairsProcessingDir = stack.pairsProcessingDir)
        cmd += '   if [[ "$insarpair" == "$onepair" ]]; then\n'
        cmd += '      cd {}/{}/insar\n'.format(stack.datesResampledDir,stack.dateReferenceStack)
        cmd += '      $code -ref_date_stack_track $xmlFile -dem $dem -input $los -nrlks $nrlks -nalks $nalks {}\n'.format(extraArguments)
        cmd += '      cd ../../../\n'
        cmd += '   fi\n\n'
        cmd += 'fi\n'
        cmd += '\n'

    else:
        cmd  = '#!/bin/bash\n\n'
        cmd += '#no pairs for InSAR processing.'

    #save commands
    pbs3c = cmd


    ##########################################
    #start new commands: combine all .sh files
    ##########################################
    cmd  = '#!/bin/bash\n\n'
    cmd += '#PBS -N alos2Stack\n'
    cmd += '#PBS -P eos_ehill\n'
    cmd += '#PBS -q q32\n'
    cmd += '#PBS -l walltime=120:00:00\n'
    cmd += '#PBS -l select=1:ncpus=1:mpiprocs=1\n'
    cmd += '\n'
    cmd += '# go to working directory\n'
    cmd += 'echo Working directory is $PBS_O_WORKDIR\n'
    cmd += 'cd $PBS_O_WORKDIR\n'
    cmd += '\n'
    cmd += '# load isce\n'
    cmd += 'source /home/share/insarscripts/isce2-code/isce_env_v2.6.3_MPv1.5.2.sh\n'
    cmd += '\n'
    cmd += '#read data, compute baseline and burst synchronization, estimate SLC offset\n'
    cmd += '#./cmd_1a.sh\n'
    cmd += '\n'
    cmd += '#estimate swath and frame offsets, resample to a common grid\n'
    cmd += '#./cmd_1b.sh\n'
    cmd += '\n'
    cmd += '#mosaic parameter, compute latitude, longitude and height, compute geometrical offsets\n'
    cmd += '#./cmd_1c.sh\n'
    cmd += '\n'
    cmd += '#pair up scenes, form and mosaic interferograms\n'
    cmd += '#./cmd_2a.sh\n'
    cmd += '\n'
    cmd += '#estimate residual offsets between radar and DEM, rectify range offsets\n'
    cmd += '#./cmd_2b.sh\n'
    cmd += '\n'
    cmd += '#diff interferograms, look and coherence\n'
    cmd += '#./cmd_2c.sh\n'
    cmd += '\n'
    cmd += '#look geom, pair up for ionospheric phase estimation, ionospheric phase estimation\n'
    cmd += '#./cmd_3a.sh\n'
    cmd += '\n'
    cmd += '#prepare interferograms for/and checking ionospheric estimation results\n'
    cmd += '#./cmd_3b.sh\n'
    cmd += '\n'
    cmd += '#estimate ionopheric phase for each date, correct ionophere\n'
    cmd += '#then filter, unwrap and geocode interferograms\n'
    cmd += '#before running this, check the instructions inside\n'
    cmd += '#./cmd_3c.sh\n'

    #save commands
    pbs4a = cmd


    return (cmd1a, pbs1a, cmd1b, pbs1b, cmd1c, pbs1c, cmd2a, pbs2a, cmd2b, pbs2b, cmd2c, pbs2c, cmd3a, pbs3a, cmd3b, cmd3c, pbs3c, pbs4a)

def cmdLineParse():
    '''
    command line parser.
    '''
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='create commands to process a stack of acquisitions')
    parser.add_argument('-stack_par', dest='stack_par', type=str, required=True,
            help = 'stack processing input parameter file.')

    if len(sys.argv) <= 1:
        print('')
        parser.print_help()
        sys.exit(1)
    else:
        return parser.parse_args()


if __name__ == '__main__':

    inps = cmdLineParse()

    stackParameter = inps.stack_par


    #need to remove -stack_par from arguments, otherwise application class would complain
    import sys
    #sys.argv.remove(sys.argv[1])
    #sys.argv = [sys.argv[2]]
    sys.argv = [sys.argv[0], sys.argv[2]]

    stack = loadStackUserParameters(stackParameter)
    insar = stack
    print()


    #0. parameters that must be set.
    if stack.dataDir is None:
        raise Exception('data directory not set.')
    checkDem(stack.dem)
    checkDem(stack.demGeo)
    checkDem(stack.wbd)
    if stack.dateReferenceStack is None:
        raise Exception('reference date of the stack not set.')


    #1. check if date dirctories are OK
    checkStackDataDir(stack.dataDir)


    #2. regular InSAR processing
    print('get dates and pairs from user input')
    pairsProcess = formPairs(stack.dataDir, stack.numberOfSubsequentDates, 
        stack.pairTimeSpanMinimum, stack.pairTimeSpanMaximum, 
        stack.datesIncluded, stack.pairsIncluded, 
        stack.datesExcluded, stack.pairsExcluded)
    datesProcess = datesFromPairs(pairsProcess)
    print('InSAR processing:')
    print('dates: {}'.format(' '.join(datesProcess)))
    print('pairs: {}'.format(' '.join(pairsProcess)))

    rank = stackRank(datesProcess, pairsProcess)
    if rank != len(datesProcess) - 1:
        print('\nWARNING: dates in stack not fully connected by pairs to be processed in regular InSAR processing\n')
    print()


    #3. ionospheric correction
    if insar.doIon:
        pairsProcessIon = formPairs(stack.dataDir, stack.numberOfSubsequentDatesIon, 
            stack.pairTimeSpanMinimumIon, stack.pairTimeSpanMaximumIon, 
            stack.datesIncludedIon, stack.pairsIncludedIon, 
            stack.datesExcludedIon, stack.pairsExcludedIon)
        datesProcessIon = datesFromPairs(pairsProcessIon)
        print('ionospheric phase estimation:')
        print('dates: {}'.format(' '.join(datesProcessIon)))
        print('pairs: {}'.format(' '.join(pairsProcessIon)))

        rankIon = stackRank(datesProcessIon, pairsProcessIon)
        if rankIon != len(datesProcessIon) - 1:
            print('\nWARNING: dates in stack not fully connected by pairs to be processed in ionospheric correction\n')
        print('\n')
    else:
        pairsProcessIon = []


    #4. union
    if insar.doIon:
        datesProcess = unionLists(datesProcess, datesProcessIon)
    else:
        datesProcess = datesProcess


    #5. find acquisition mode
    mode = os.path.basename(sorted(glob.glob(os.path.join(stack.dataDir, datesProcess[0], 'LED-ALOS2*-*-*')))[0]).split('-')[-1][0:3]
    print('acquisition mode of stack: {}'.format(mode))
    print('\n')


    #6. check if already processed previously
    datesProcessedAlready = getFolders(stack.datesResampledDir)
    if not stack.datesReprocess:
        datesProcess, datesProcessRemoved = removeCommonItemsLists(datesProcess, datesProcessedAlready)
        if datesProcessRemoved != []:
            print('the following dates have already been processed, will not reprocess them.')
            print('dates: {}'.format(' '.join(datesProcessRemoved)))
            print()

    pairsProcessedAlready = getFolders(stack.pairsProcessingDir)
    if not stack.pairsReprocess:
        pairsProcess, pairsProcessRemoved = removeCommonItemsLists(pairsProcess, pairsProcessedAlready)
        if pairsProcessRemoved != []:
            print('the following pairs for InSAR processing have already been processed, will not reprocess them.')
            print('pairs: {}'.format(' '.join(pairsProcessRemoved)))
            print()

    if insar.doIon:
        pairsProcessedAlreadyIon = getFolders(stack.pairsProcessingDirIon)
        if not stack.pairsReprocessIon:
            pairsProcessIon, pairsProcessRemovedIon = removeCommonItemsLists(pairsProcessIon, pairsProcessedAlreadyIon)
            if pairsProcessRemovedIon != []:
                print('the following pairs for estimating ionospheric phase have already been processed, will not reprocess them.')
                print('pairs: {}'.format(' '.join(pairsProcessRemovedIon)))
                print()

    print()
    
    print('dates and pairs to be processed:')
    print('dates: {}'.format(' '.join(datesProcess)))
    print('pairs (for InSAR processing): {}'.format(' '.join(pairsProcess)))
    if insar.doIon:
        print('pairs (for estimating ionospheric phase): {}'.format(' '.join(pairsProcessIon)))
    print('\n')


    #7. use mode to define processing parameters
    #number of looks
    from isceobj.Alos2Proc.Alos2ProcPublic import modeProcParDict
    if insar.numberRangeLooks1 is None:
        insar.numberRangeLooks1 = modeProcParDict['ALOS-2'][mode]['numberRangeLooks1']
    if insar.numberAzimuthLooks1 is None:
        insar.numberAzimuthLooks1 = modeProcParDict['ALOS-2'][mode]['numberAzimuthLooks1']
    if insar.numberRangeLooks2 is None:
        insar.numberRangeLooks2 = modeProcParDict['ALOS-2'][mode]['numberRangeLooks2']
    if insar.numberAzimuthLooks2 is None:
        insar.numberAzimuthLooks2 = modeProcParDict['ALOS-2'][mode]['numberAzimuthLooks2']
    if insar.numberRangeLooksIon is None:
        insar.numberRangeLooksIon = modeProcParDict['ALOS-2'][mode]['numberRangeLooksIon']
    if insar.numberAzimuthLooksIon is None:
        insar.numberAzimuthLooksIon = modeProcParDict['ALOS-2'][mode]['numberAzimuthLooksIon']


    #7. create commands
    if (datesProcess == []) and (pairsProcess == []) and (pairsProcessIon == []):
        print('no dates and pairs need to be processed.')
        print('no processing script is generated.')
    else:
        cmd1a, pbs1a, cmd1b, pbs1b, cmd1c, pbs1c, cmd2a, pbs2a, cmd2b, pbs2b, cmd2c, pbs2c, cmd3a, pbs3a, cmd3b, cmd3c, pbs3c, pbs4a = createCmds(stack, datesProcess, pairsProcess, pairsProcessIon, mode)
        with open('cmd_1a.sh', 'w') as f:
            f.write(cmd1a)
        with open('pbs_1a.pbs', 'w') as f:
            f.write(pbs1a)
        with open('cmd_1b.sh', 'w') as f:
            f.write(cmd1b)
        with open('pbs_1b.pbs', 'w') as f:
            f.write(pbs1b)
        with open('cmd_1c.sh', 'w') as f:
            f.write(cmd1c)
        with open('pbs_1c.pbs', 'w') as f:
            f.write(pbs1c)
        with open('cmd_2a.sh', 'w') as f:
            f.write(cmd2a)
        with open('pbs_2a.pbs', 'w') as f:
            f.write(pbs2a)
        with open('cmd_2b.sh', 'w') as f:
            f.write(cmd2b)
        with open('pbs_2b.pbs', 'w') as f:
            f.write(pbs2b)
        with open('cmd_2c.sh', 'w') as f:
            f.write(cmd2c)
        with open('pbs_2c.pbs', 'w') as f:
            f.write(pbs2c)
        with open('cmd_3a.sh', 'w') as f:
            f.write(cmd3a)
        with open('pbs_3a.pbs', 'w') as f:
            f.write(pbs3a)
        with open('cmd_3b.sh', 'w') as f:
            f.write(cmd3b)
        with open('cmd_3c.sh', 'w') as f:
            f.write(cmd3c)
        with open('pbs_3c.pbs', 'w') as f:
            f.write(pbs3c)
        with open('run_alos2Stack_cmds.pbs', 'w') as f:
            f.write(pbs4a)

    runCmd('chmod +x cmd_1a.sh cmd_1b.sh cmd_1c.sh cmd_2a.sh cmd_2b.sh cmd_2c.sh cmd_3a.sh cmd_3b.sh cmd_3c.sh', silent=1)
