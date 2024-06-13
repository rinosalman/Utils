#!/usr/bin/env python3
# Prepare input files for running alos2App.py based on time_threshold and baseline_threshold
# Rino Salman, 22 April 2020

import isce
from isceobj.Sensor import createSensor
from isceobj.Util import Poly1D
from isceobj.Planet.AstronomicalHandbook import Const
from mroipac.baseline.Baseline import Baseline
import datetime, os, shutil, time, argparse, glob, shelve, numpy as np

def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(description='Prepare input files for stack processing of alos2.')
    parser.add_argument('-w', '--working_directory', dest='workDir', type=str, default='./',
            help='Working directory ')
    parser.add_argument('-i','--input', dest='rawdir', type=str,
            required=True, help='Input IMG* and LED* ALOS2 directory')
    parser.add_argument('-t', '--time_threshold', dest='dtThr', type=float, default=1000.0,
            help='Time threshold (max temporal baseline in days)')
    parser.add_argument('-b', '--baseline_threshold', dest='dbThr', type=float, default=1000.0,
            help='Baseline threshold (max bperp in meters)')
    parser.add_argument('-s', '--starting_swath', dest='sSwath', type=str, default=1,
            help='Starting swath')
    parser.add_argument('-e', '--ending_swath', dest='eSwath', type=str, default=5,
            help='Ending swath')
    parser.add_argument('-m', '--master_date', dest='masterDate', type=str, default=None,
            help='Directory with master acquisition')
    parser.add_argument('-d', '--dem_region', dest='dbox', type = int, nargs = '+', 
            required=True, help='Defines the dem spatial region in the format South North West East.\
            The values should be integers from (-90,90) for latitudes and (-180,180) for longitudes.')
    parser.add_argument('-g', '--geocode_region', dest='gbox', type = float, nargs = '+', default=None,
            help='Defines the geocode spatial region in the format South North West East.')
    return parser.parse_args()


def unpack(inps,slcname):
    '''
    Unpack IMG* to binary SLC file.
    '''

    print('Unpack IMG* to binary SLC files')
    img=glob.glob(os.path.join(inps.rawdir, 'IMG*F1'))
    for ii in range(len(img)):
        imgname = img[ii]
        print('Process: %s'%imgname)
        a,b,c,d,e,f=imgname.split("-")
        ldrname = inps.rawdir+'/LED-'+c+'-'+d+'-'+e
        slcdir=slcname+'/20'+d
    
        if not os.path.isdir(slcdir):
           os.makedirs(slcdir)

        date = os.path.basename(slcdir)
        obj = createSensor('ALOS2')
        obj.configure()
        obj._leaderFile = ldrname
        obj._imageFile = imgname

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

        pickName = os.path.join(slcdir, 'data')
        with shelve.open(pickName) as db:
           db['frame'] = obj.frame
           db['doppler'] = poly
           db['fmrate'] = fpoly
           db['info'] = obj.leaderFile.facilityRecord.metadata


def get_dates(slcOut):

    dirs = glob.glob(slcOut+'/*')
    acuisitionDates = []
    for dirf in dirs:
         expectedRaw = os.path.join(dirf,os.path.basename(dirf) + '.slc')

         if os.path.exists(expectedRaw):
             acuisitionDates.append(os.path.basename(dirf))

    acuisitionDates.sort()
    if inps.masterDate is None or inps.masterDate not in acuisitionDates:
        inps.masterDate = acuisitionDates[0]
    slaveDates = acuisitionDates.copy()
    slaveDates.remove(inps.masterDate)
    return acuisitionDates, inps.masterDate, slaveDates


def baselinePair(master, slave,doBaselines=True):

    if doBaselines: # open files to calculate baselines
        try:
            mdb = shelve.open( os.path.join(master, 'raw'), flag='r')
            sdb = shelve.open( os.path.join(slave, 'raw'), flag='r')
        except:
            mdb = shelve.open( os.path.join(master, 'data'), flag='r')
            sdb = shelve.open( os.path.join(slave, 'data'), flag='r')

        mFrame = mdb['frame']
        sFrame = sdb['frame']


        bObj = Baseline()
        bObj.configure()
        bObj.wireInputPort(name='masterFrame', object=mFrame)
        bObj.wireInputPort(name='slaveFrame', object=sFrame)
        bObj.baseline()    # calculate baseline from orbits
        pBaselineBottom = bObj.pBaselineBottom
        pBaselineTop = bObj.pBaselineTop
    else:       # set baselines to zero if not calculated
        pBaselineBottom = 0.0
        pBaselineTop = 0.0

    baselineDirName = os.path.basename(master) + "_" + os.path.basename(slave)
    baselineDirNamePair = os.path.join('baselines', baselineDirName)
    if not os.path.isdir(baselineDirNamePair):
        os.makedirs(baselineDirNamePair)
        baselineOutName = os.path.basename(master) + "_" + os.path.basename(slave) + ".txt"
        f = open(os.path.join(baselineDirNamePair, baselineOutName) , 'w')
        f.write("PERP_BASELINE_BOTTOM " + str(pBaselineBottom) + '\n')
        f.write("PERP_BASELINE_TOP " + str(pBaselineTop) + '\n')
        f.close()
        #print('Baseline at top/bottom: %f %f'%(pBaselineTop,pBaselineBottom))
        return (pBaselineTop+pBaselineBottom)/2.


def baselineStack(inps,stackMaster,acqDates,doBaselines=True):
    from collections import OrderedDict
    baselineDict = OrderedDict()
    timeDict = OrderedDict()
    datefmt = '%Y%m%d'
    t0 = datetime.datetime.strptime(stackMaster, datefmt)
    master = os.path.join(inps.slcDir, stackMaster)
    for slv in acqDates:
        if slv != stackMaster:
            slave = os.path.join(inps.slcDir, slv)
            baselineDict[slv]=baselinePair( master, slave, doBaselines)
            t = datetime.datetime.strptime(slv, datefmt)
            timeDict[slv] = t - t0
        else:
            baselineDict[stackMaster] = 0.0
            timeDict[stackMaster] = datetime.timedelta(0.0)

    return baselineDict, timeDict


def plotNetwork(baselineDict, timeDict, pairs,save_name='pairs.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    datefmt='%Y%m%d'
    fig1 = plt.figure(1)
    ax1=fig1.add_subplot(111)

    ax1.cla()
    for ni in range(len(pairs)):
         ax1.plot([datetime.datetime.strptime(pairs[ni][0],datefmt), datetime.datetime.strptime(pairs[ni][1], datefmt)],
                 np.array([baselineDict[pairs[ni][0]],baselineDict[pairs[ni][1]]]),
                 '-ko',lw=1, ms=5, alpha=0.7, mfc='r')


    #myFmt = mdates.DateFormatter('%Y-%m')
    myFmt = mdates.DateFormatter('%Y')
    ax1.xaxis.set_major_formatter(myFmt)

    plt.title('Baseline plot: %s pairs'%len(pairs))
    plt.xlabel('Time')
    plt.ylabel('Perp. Baseline (m)')
    plt.tight_layout()
    plt.savefig(save_name, bbox_inches='tight')

    ###Check degree of each SLC
    datelist = [k for k,v in list(timeDict.items())]
    connMat = np.zeros((len(pairs), len(timeDict)))
    for ni in range(len(pairs)):
        connMat[ni, datelist.index(pairs[ni][0])] = 1.0
        connMat[ni, datelist.index(pairs[ni][1])] = -1.0

    slcSum = np.sum( np.abs(connMat), axis=0)
    minDegree = np.min(slcSum)

    print('##################')
    print('SLCs with min degree connection of {0}'.format(minDegree))
    for ii in range(slcSum.size):
        if slcSum[ii] == minDegree:
            print(datelist[ii])
    print('##################')

    #if np.linalg.matrix_rank(connMat) != (len(timeDict) - 1):
    #    raise Exception('The network for cascading coregistration is not connected. Possible reason is due to short time_threshold and baseline threshold')


def writePbsFile(inps,masterSlave,masterId,slaveId):
    ''' 
    also create pbs command in each pair folder in case needed for reproprocessing individual pair
    '''
    pbsName = 'runCommand.pbs'
    dirName = os.path.join(inps.workDir, 'intf', masterSlave, pbsName)
    f = open(dirName,'w')
    f.write('#!/bin/bash '+ '\n')
    f.write('#PBS -N ' + masterId + '_' + slaveId + '\n')
    
    writePbs='''#PBS -P eos_ehill
#PBS -q q128
#PBS -l walltime=120:00:00
#PBS -l select=1:ncpus=1:mpiprocs=1

echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR

# load isce
source /home/share/insarscripts/isce2-code/isce_env_latest.sh

# run alos2App
'''
    f.write(writePbs)
    f.write('alos2App.py --steps >& $PBS_JOBID.log 2>&1'+'\n')
    f.write('')
    f.close()


def writeXmlFile(inps,frame,masterId,slaveId):

    xmlName = 'alos2App.xml'
    masterSlave = '20'+str(masterId)+'_20'+str(slaveId)
    dirName = os.path.join(inps.workDir, 'intf', masterSlave, xmlName)
    f = open(dirName,'w')
    f.write('''<?xml version="1.0" encoding="UTF-8"?>'''+ '\n')
    f.write('<alos2App>' + '\n')
    f.write('''  <component name="alos2insar">'''+ '\n')
    f.write('\n')
    f.write('''      <property name="master directory">master</property>'''+'\n')
    f.write('''      <property name="slave directory">slave</property>'''+'\n')
    f.write('''      <property name="master frames">['''+frame+']</property>'+'\n')
    f.write('''      <property name="slave frames">['''+frame+']</property>'+'\n')
    f.write('''      <property name="starting swath">'''+str(inps.sSwath)+'</property>'+'\n') 
    f.write('''      <property name="ending swath">'''+str(inps.eSwath)+'</property>'+'\n')
    f.write('''      <property name="dem for coregistration">../../dem1/demLat_'''\
                     +str(inps.south)+'_'+str(inps.north)+'_Lon_'\
                     +str(inps.west)+'_'+str(inps.east)+'.dem.wgs84</property>'+'\n')
    f.write('''      <property name="dem for geocoding">../../dem3/demLat_'''\
                     +str(inps.south)+'_'+str(inps.north)+'_Lon_'\
                     +str(inps.west)+'_'+str(inps.east)+'.dem.wgs84</property>'+'\n')
    f.write('''      <property name="water body">../../wbd/swbdLat_'''\
                     +str(inps.south)+'_'+str(inps.north)+'_Lon_'\
                     +str(inps.west)+'_'+str(inps.east)+'.wbd</property>'+'\n')
    if inps.gbox!=None:
       f.write('''      <property name="geocode bounding box">['''\
                        +str(inps.gbox[0])+', '+str(inps.gbox[1])+', '\
                        +str(inps.gbox[2])+', '+str(inps.gbox[3])+']</property> ''' + '\n')
       f.write('''      <property name="geocode interpolation method">nearest</property> ''' + '\n')
       f.write('''      <property name="geocode file list">[filt_'''\
                        +str(masterId)+'-'+str(slaveId)+'_5rlks_28alks.unw.conncomp'+', '\
                        +str(masterId)+'-'+str(slaveId)+'_5rlks_28alks.los'+', '\
                        +str(masterId)+'-'+str(slaveId)+'_5rlks_28alks.cor'+', '+'filt_'\
                        +str(masterId)+'-'+str(slaveId)+'_5rlks_28alks.unw]</property> ''' + '\n')
    f.write('''      <property name="minimum window size for filtering ionosphere phase">101</property> ''' + '\n')
    f.write('\n')
    f.write('  </component>'+ '\n')
    f.write('</alos2App>'+ '\n')
    f.write('')
    f.close()
 


def selectPairs(inps,stackMaster, slaveDates, acuisitionDates,doBaselines=True):

    #plot
    baselineDict, timeDict = baselineStack(inps, stackMaster, acuisitionDates,doBaselines)
    numDates = len(acuisitionDates)
    pairs = []
    for i in range(numDates-1):
       for j in range(i+1,numDates):
          db = np.abs(baselineDict[acuisitionDates[j]] - baselineDict[acuisitionDates[i]])
          dt  = np.abs(timeDict[acuisitionDates[j]].days - timeDict[acuisitionDates[i]].days)
          if (db < inps.dbThr) and (dt < inps.dtThr):
              pairs.append((acuisitionDates[i],acuisitionDates[j]))

    plotNetwork(baselineDict, timeDict, pairs,os.path.join(inps.workDir,'pairs.ps'))
    #shutil.rmtree('baselines')
    print ('Number of pairs created: ', len(pairs))


    # interferogram folders
    for jj in range(len(pairs)):
        #create folders
        pairs = np.array(pairs).astype(int)
        masterslave = pairs[jj]
        master = masterslave[0]
        slave = masterslave[1]
        masterSlave = str(master)+'_'+str(slave)
        intfMsM = os.path.join(inps.workDir, 'intf', masterSlave, 'master')
        intfMsS = os.path.join(inps.workDir, 'intf', masterSlave, 'slave')
        if not os.path.exists(intfMsM):
           os.makedirs(intfMsM)
           os.makedirs(intfMsS)
        
        # copy IMG* and LED* (symbolic link) to pairs folder
        masterId = str(masterslave[0])[2:]
        slaveId = str(masterslave[1])[2:]
        imgMaster = glob.glob(os.path.join(inps.rawdir, 'IMG-HH*%s*'%masterId))
        imgSlave = glob.glob(os.path.join(inps.rawdir, 'IMG-HH*%s*'%slaveId))
        for kk in range(len(imgMaster)):
            masterRealPath = os.path.realpath(imgMaster[kk])
            masterName = imgMaster[kk].split("/")[1]
            slaveRealPath = os.path.realpath(imgSlave[kk])
            slaveName = imgSlave[kk].split("/")[1]
            os.symlink(masterRealPath,intfMsM+'/'+masterName) 
            os.symlink(slaveRealPath,intfMsS+'/'+slaveName) 

        ledMaster = glob.glob(os.path.join(inps.rawdir, 'LED*%s*'%masterId))[0]
        ledSlave = glob.glob(os.path.join(inps.rawdir, 'LED*%s*'%slaveId))[0]
        ledMasterRealPath = os.path.realpath(ledMaster)
        ledMasterName = ledMaster.split("/")[1]
        ledSlaveRealPath = os.path.realpath(ledSlave)
        ledSlaveName = ledSlave.split("/")[1]
        os.symlink(ledMasterRealPath,intfMsM+'/'+ledMasterName) 
        os.symlink(ledSlaveRealPath,intfMsS+'/'+ledSlaveName) 
        

        # write pbs file
        writePbsFile(inps,masterSlave,masterId,slaveId)


        # write xml file        
        frame=str(ledSlaveName.split("-")[1])[-4:]
        writeXmlFile(inps,frame,masterId,slaveId)

        
        # save intf.in
        intfMs = os.path.join(inps.workDir, 'intf', masterSlave)
        logFolder = os.path.join(intfMs, 'log')
        if not os.path.isdir(logFolder):
           os.makedirs(logFolder)
        log = 'log/pair_'+masterSlave+'_'+time.strftime("%Y_%m_%d")+'.log'
        logFullPath = os.path.join(intfMs, log)
        os.system("echo %s %s >> intf.in"%(intfMs, logFullPath))

    # write intf list and submission scripts
    jobsDir = 'commands'
    if not os.path.isdir(jobsDir):
        os.makedirs(jobsDir)

        # pbs commands
        ll = 1
        for kk in range(0,len(pairs),32):
            intfDotIn = 'intf.in.%s'%ll
            os.system("cat intf.in | sed -n '1,32p' > %s/%s"%(jobsDir,intfDotIn))
            os.system("cp intf.in %s/intf.in.all"%jobsDir)
            os.system("cat intf.in | sed -e '1,32d' > temp && mv temp intf.in") 

            pbsName = 'runCommand_%s.pbs'%ll
            pbsNameFullPath = os.path.join(inps.workDir, jobsDir, pbsName)
            f = open(pbsNameFullPath,'w')
            f.write('#!/bin/bash '+ '\n')
            f.write('#PBS -N ' + intfDotIn + '\n')
    
            writePbs='''#PBS -P eos_ehill
#PBS -q q128
#PBS -l walltime=120:00:00
#PBS -l select=1:ncpus=32

echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR

# load isce
source /home/share/insarscripts/isce2-code/isce_env_latest.sh

# run parallel processing
'''
            f.write(writePbs)
            f.write('python /home/rino/scripts/insarscripts/parallel_processing.py ' + intfDotIn + ' 32' + '\n')
            f.write('')
            f.close()
 
            # counter
            ll = ll + 1


        # sh command
        shName = 'submitAllrunCommands.sh'
        shNameFullPath = os.path.join(inps.workDir, jobsDir, shName)
        f = open(shNameFullPath,'w')
        f.write('#!/bin/bash '+ '\n')
        writeSh='''# Submit all .job commands

for i in `ls *.pbs`;do
    qsub $i
done
'''
        f.write(writeSh)
        f.write('')
        f.close()
    
    os.remove('intf.in') 

    # also create pbs command in each pair folder in case needed for reproprocessing individual pair
    createJobList(inps)



def defineRegionBox(inps):
    
    # latitude
    if inps.dbox[0] > 0:
        if inps.dbox[0]>10:
            inps.south = 'N%2d'%inps.dbox[0]
        else:
            inps.south = 'N0%d'%inps.dbox[0]
    elif inps.dbox[0] < 0:
        if inps.dbox[0]>10:
            inps.south = 'S%2d'%inps.dbox[0]
        else:
            inps.south = 'S0%d'%inps.dbox[0]
    if inps.dbox[1] > 0:
        if inps.dbox[1]>10:
            inps.north = 'N%2d'%inps.dbox[1]
        else:
            inps.north = 'N0%d'%inps.dbox[1]
    elif inps.dbox[1] < 0:
        if inps.dbox[1]>10:
            inps.north = 'S%2d'%inps.dbox[1]
        else:
            inps.north = 'S0%d'%inps.dbox[1]
 
    # longitude
    if inps.dbox[2] > 0:
        if inps.dbox[2]>100:
            inps.west = 'E%3d'%inps.dbox[2]
        elif inps.dbox[2]>10:
            inps.west = 'E0%d'%inps.dbox[2]
        else:
            inps.west = 'E00%d'%inps.dbox[2]
    elif inps.dbox[2] < 0:
        if inps.dbox[2]>100:
            inps.west = 'W%3d'%inps.dbox[2]
        elif inps.dbox[2]>10:
            inps.west = 'W0%d'%inps.dbox[2]
        else:
            inps.west = 'W00%d'%inps.dbox[2]
    if inps.dbox[3] > 0:
        if inps.dbox[3]>100:
            inps.east = 'E%3d'%inps.dbox[3]
        elif inps.dbox[3]>10:
            inps.east = 'E0%d'%inps.dbox[3]
        else:
            inps.west = 'E00%d'%inps.dbox[3]
    elif inps.dbox[3] < 0:
        if inps.dbox[3]>100:
            inps.east = 'W%3d'%inps.dbox[3]
        elif inps.dbox[3]>10:
            inps.east = 'W0%d'%inps.dbox[3]
        else:
            inps.east = 'W00%d'%inps.dbox[3]


def downloadDemWdb(inps):
    
    # download dem_1_arcsec for coregistration
    dem1 = 'dem1'
    if not os.path.isdir(dem1):
        os.makedirs(dem1)
    
        os.chdir(dem1)
        os.system("dem.py -a stitch -b %s %s %s %s -k -s 1 -c -f -u\
                  http://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11"%\
                  (str(inps.dbox[0]),str(inps.rbox[1]),str(inps.rbox[2]),str(inps.rbox[3])))

        os.system("fixImageXml.py -i demLat_*_*_Lon_*_*.dem.wgs84 -f")
        os.system("rm *.hgt* *.log demLat*Lon*.dem demLat*Lon*.dem.vrt demLat*Lon*dem.xml")
        os.chdir('..')


    # download dem_3_arcsec for geocoding
    dem3 = 'dem3'
    if not os.path.isdir(dem3):
        os.makedirs(dem3)
    
        os.chdir(dem3)
        os.system("dem.py -a stitch -b %s %s %s %s -k -s 3 -c -f -u\
                  http://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL3.003/2000.02.11"%\
                  (str(inps.dbox[0]),str(inps.rbox[1]),str(inps.rbox[2]),str(inps.rbox[3])))

        os.system("fixImageXml.py -i demLat_*_*_Lon_*_*.dem.wgs84 -f")
        os.system("rm *.hgt* *.log demLat*Lon*.dem demLat*Lon*.dem.vrt demLat*Lon*dem.xml")
        os.chdir('..')
        os.system("rm isce.lo*")


    # download water body (ALWAYS FAIL TO DOWNLOAD IT)
    #wbd = 'wbd'
    #if not os.path.isdir(wbd):
    #    os.makedirs(wbd)
    
    #    os.chdir(wbd)
    #    os.system("wbd.py %s %s %s %s"%(str(inps.dbox[0]),str(inps.rbox[1]),str(inps.rbox[2]),str(inps.rbox[3])))

    #    os.system("fixImageXml.py -i swbdLat_*_*_Lon_*_*.wbd -f")
    #    os.chdir('..')


def createJobList(inps):
    
    dotpbs=glob.glob(os.path.join(inps.intfOut, '20*_20*/*.pbs'))
    shName = 'submit_multi_jobs.sh'
    shDirName = os.path.join(inps.workDir, 'commands', shName)
    f = open(shDirName,'w')
    f.write('#!/bin/bash'+ '\n')
    f.write('# Submit multiple jobs '+ '\n')
    f.write('cDir=`pwd` '+ '\n')
    f.write('\n')
    for ll in range(len(dotpbs)):
        pair = dotpbs[ll].split("/")[-2] 
        f.write('cd ../intf/'+str(pair)+'; '+ 'qsub runCommand.pbs; cd $cDir' + '\n')
    f.write('')
    f.close()
 
    # sort
    os.system("cat %s | sort -nk2 > temp && mv temp %s"%(shDirName, shDirName))



if __name__ == '__main__':
    '''
    Main driver.
    '''

    # getting the input
    inps = cmdLineParse()
    inps.workDir = os.path.abspath(inps.workDir)
    defineRegionBox(inps)


    # check input folder for raw
    if inps.rawdir.endswith('/'):
        inps.rawdir = inps.rawdir[:-1]


    # unpack IMG* binary to SLC file
    slcDir = 'slc'
    fullPathSlc = os.path.join(inps.workDir, slcDir)
    inps.slcDir = fullPathSlc
    if not os.path.exists(fullPathSlc):
        unpack(inps, slcDir)


    # create pairs based on time_threshold and baseline_threshold, also create .xml and .pbs files
    intfDir = 'intf'
    fullPathIntf = os.path.join(inps.workDir, intfDir)
    inps.intfOut = fullPathIntf
    if not os.path.exists(fullPathIntf):
        acquisitionDates, stackMasterDate, slaveDates = get_dates(fullPathSlc) 
        selectPairs(inps,stackMasterDate, slaveDates, acquisitionDates,doBaselines=True)

    # download dem and water body
    downloadDemWdb(inps)
    
