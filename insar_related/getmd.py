#!/usr/bin/env python3
# Get metadata in ROI-PAC format for MintPy input
# Rino Salman, April 2020

# Use with your own risk!!

import isce, isceobj
from osgeo import gdal     
import os, glob, subprocess, shelve
import numpy as np        
from mintpy.utils import ptime, readfile, writefile, utils as ut
from mroipac.baseline.Baseline import Baseline
from isceobj.Planet.Planet import Planet


def getNonzeroRowNumber(data, buffer=2):
    """Find the first and last row number of rows without zero value
       for multiple swaths data
    """
    if np.all(data):
       r0, r1 = 0 + buffer, -1 - buffer
    else:
       row_flag = np.sum(data != 0., axis=1) == data.shape[1]
       row_idx = np.where(row_flag)[0]
       r0, r1 = row_idx[0] + buffer, row_idx[-1] - buffer
    return r0, r1


def getLengthWdithPixelSize(unw,unwgeo):
    
    metadata = {}

    # length and width
    ds = gdal.Open(unw, gdal.GA_ReadOnly)
    metadata['FILE_LENGTH'] = ds.RasterYSize
    metadata['WIDTH'] = ds.RasterXSize
 
    # pixel size
    dt = gdal.Open(unwgeo)
    dtt = dt.GetGeoTransform()
    metadata['X_STEP'] = dtt[1]
    metadata['Y_STEP'] = dtt[5]

    # upper left corner coordinates
    st = gdal.Open(unwgeo)
    xFirst, xres, xskew, yFirst, yskew, yres = st.GetGeoTransform()
    metadata['X_FIRST'] = xFirst
    metadata['Y_FIRST'] = yFirst

    return metadata 


def getCoordinatesAtCorners(metadata, lon, lat, los):

    # lon
    #lon = glob.glob(os.path.join('insar','*.lon'))[0]
    data = readfile.read(lon)[0]
    r0, r1 = getNonzeroRowNumber(data)
    metadata['LON_REF1'] = str(data[r0, 0])
    metadata['LON_REF2'] = str(data[r0, -1])
    metadata['LON_REF3'] = str(data[r1, 0])
    metadata['LON_REF4'] = str(data[r1, -1])

    # lat
    #lat = glob.glob(os.path.join('insar','*.lat'))[0]
    data = readfile.read(lat)[0]
    r0, r1 = getNonzeroRowNumber(data)
    latRef1 = str(data[r0, 0])
    latRef2 = str(data[r0, -1])
    latRef3 = str(data[r1, 0])
    latRef4 = str(data[r1, -1])
    metadata['LAT_REF1'] = str(data[r0, 0])
    metadata['LAT_REF2'] = str(data[r0, -1])
    metadata['LAT_REF3'] = str(data[r1, 0])
    metadata['LAT_REF4'] = str(data[r1, -1])

    # los
    #los = glob.glob(os.path.join('insar','*.lat'))[0]
    data = readfile.read(los, datasetName='az')[0]
    data[data == 0.] = np.nan
    azAngle = np.nanmean(data)
    # convert isce azimuth angle to roipac orbit heading angle
    headAngle = -1 * (270 + azAngle)
    headAngle -= np.round(headAngle / 360.) * 360.
    metadata['HEADING'] = str(headAngle)

    return metadata


def getValues(xml, category):

    return [x.attrib['value'] for x in 
           xml.findall('/parent[@name="%s"]/*' % category)]

def grepFromXml(metadata, xmlFileTrack, preprocessXml):
    
    # radar wavelength
    cmd = ''' grep -A 1 "radarwavelength" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%xmlFileTrack
    rw = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    metadata['WAVELENGTH'] = rw
    metadata['radarWavelength'] = rw

    # rangePixelSize
    cmd = ''' grep -A 1 "rangepixelsize" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%xmlFileTrack
    rps = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    metadata['RANGE_PIXEL_SIZE'] = rps
    metadata['rangePixelSize'] = rps

    # prf
    cmd = ''' grep -A 1 "pulserepetitionfrequency" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%xmlFileTrack
    prf = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    metadata['PRF'] = prf
    metadata['prf'] = prf

    # azimuthPixelSize
    cmd = ''' grep -A 1 "azimuthpixelsize" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%xmlFileTrack
    aps = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    metadata['AZIMUTH_PIXEL_SIZE'] = aps
    metadata['azimuthPixelSize'] = aps

    # azimuth look
    cmd = ''' grep -A 1 "numberofazimuthlooks1" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%preprocessXml
    al1 = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    cmd = ''' grep -A 1 "numberofazimuthlooks2" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%preprocessXml
    al2 = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    al = int(al1) * int(al2)
    metadata['ALOOKS'] = al

    # range look
    cmd = ''' grep -A 1 "numberofrangelooks1" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%preprocessXml
    rl1 = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    cmd = ''' grep -A 1 "numberofrangelooks2" %s | awk 'NR==2{print $0}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' '''%preprocessXml
    rl2 = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True).communicate()[0].decode('utf-8').strip()
    rl = int(rl1) * int(rl2)
    metadata['RLOOKS'] = rl

    return metadata


def getRadiusHeadingBaseline(metadata, masterSlc, slaveSlc):

    mdb = shelve.open(masterSlc, flag='r')
    sdb = shelve.open(slaveSlc, flag='r')
    mFrame = mdb['frame']
    sFrame = sdb['frame']

    # baselines
    metadataBaseline = {}
    bObj = Baseline()
    bObj.configure()
    bObj.wireInputPort(name='masterFrame', object=mFrame)
    bObj.wireInputPort(name='slaveFrame', object=sFrame)
    bObj.baseline()    # calculate baseline from orbits
    pBaselineBottom = bObj.pBaselineBottom
    pBaselineTop = bObj.pBaselineTop
    metadataBaseline['P_BASELINE_TOP_HDR'] = bObj.pBaselineTop
    metadataBaseline['P_BASELINE_BOTTOM_HDR'] = bObj.pBaselineBottom


    # earth radius and heading
    sensingMid = mFrame._sensingMid
    orbit = mFrame.orbit
    peg = orbit.interpolateOrbit(mFrame.sensingMid, method='hermite')
    refElp = Planet(pname='Earth').ellipsoid
    llh = refElp.xyz_to_llh(peg.getPosition())
    refElp.setSCH(llh[0], llh[1], orbit.getENUHeading(mFrame.sensingMid))
    metadata['EARTH_RADIUS'] = refElp.pegRadCur
    metadata['altitude'] = llh[2]

    
    # others
    metadata['startUTC'] = mFrame._sensingStart
    metadata['stopUTC'] = mFrame._sensingStop
    metadata['startingRange'] = mFrame._startingRange
    metadata['polarization'] = str(mFrame._polarization).replace('/', '')
    if metadata['polarization'].startswith("b'"):
        metadata['polarization'] = metadata['polarization'][2:4]
    metadata['trackNumber'] = mFrame._trackNumber
    metadata['orbitNumber'] = mFrame._orbitNumber

    timeSeconds = (mFrame._sensingStart.hour * 3600.0 +
                    mFrame._sensingStart.minute * 60.0 +
                    mFrame._sensingStart.second)
    metadata['CENTER_LINE_UTC'] = timeSeconds

    return metadata, metadataBaseline
    


if __name__ == '__main__':
    '''
    Main driver.
    '''

    # current directory
    cwd = os.getcwd()

    #pairs = glob.glob('intf/20*_20*')
    pairs = np.genfromtxt('folderIntf12',str)
    for i in range(len(pairs)):

        # go to dir
        pair = pairs[i]
        os.chdir(pair)
        os.system("pwd")

	# read file length, width, pixel size, and upper left corner coordinates
        unw = glob.glob(os.path.join('insar', 'filt_*lks.unw'))[0]
        unwgeo = glob.glob(os.path.join('insar', 'filt_*lks.unw.geo'))[0]
        metadata = getLengthWdithPixelSize(unw,unwgeo)

	# read longitude and latitude at corner 1/2/3/4
        lon = glob.glob(os.path.join('insar','*.lon'))[0]
        lat = glob.glob(os.path.join('insar','*.lat'))[0]
        los = glob.glob(os.path.join('insar','*.los'))[0]
        metadata = getCoordinatesAtCorners(metadata, lon, lat, los)

	# get radarWavelength, startingRange, rangePixelSize, prf, azimuthPixelSize, A/R_looks
        xmlFileTrack = glob.glob('*track.xml')[0]
        preprocessXml = 'PICKLE/preprocess.xml'
        metadata = grepFromXml(metadata, xmlFileTrack, preprocessXml)

	# get earthRadius, heading, altitude, baselines
        masterDate = os.path.basename(pair).split('_')[0]
        slaveDate = os.path.basename(pair).split('_')[1]
        masterSlc = os.path.join(cwd, 'slc', masterDate, 'data')
        slaveSlc = os.path.join(cwd, 'slc', slaveDate, 'data')
        metadata, metadataBaseline = getRadiusHeadingBaseline(metadata, masterSlc, slaveSlc)

	# get the rest
        metadata['ANTENNA_SIDE'] = '-1'
        metadata['ORBIT_DIRECTION'] = 'DESCENDING'
        metadata['PLATFORM'] = 'PALSAR'
        metadata['PROCESSOR'] = 'isce'
        metadata['DATE12'] = str(masterDate[2:])+'-'+str(slaveDate[2:])
	
	# write to .rsc file
        for i in range(3):
            if i==0:
               metadata['FILE_TYPE'] = '.unw' 
               metadata['UNIT'] = 'radian' 
               rsc_file = unw + '.rsc'
               metadata = readfile.standardize_metadata(metadata)
               if rsc_file:
                  print('writing ', rsc_file)
                  writefile.write_roipac_rsc(metadata, rsc_file)
            elif i==1:
               metadata['FILE_TYPE'] = '.cor' 
               metadata['UNIT'] = '1' 
               cor = glob.glob('insar/*.cor')[0]
               rsc_file = cor + '.rsc'
               metadata = readfile.standardize_metadata(metadata)
               if rsc_file:
                  print('writing ', rsc_file)
                  writefile.write_roipac_rsc(metadata, rsc_file)
            else:
               outFileName = str(masterDate[2:])+'_'+str(slaveDate[2:])+'_baseline.rsc'
               rsc_file = os.path.join('insar', outFileName)
               metadataBaseline = readfile.standardize_metadata(metadataBaseline)
               if rsc_file:
                  print('writing ', rsc_file)
                  writefile.write_roipac_rsc(metadataBaseline, rsc_file)



        # go back to previous directory
        os.chdir(cwd)
