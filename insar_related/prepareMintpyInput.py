#!/usr/bin/env python3

# Get metadata for some alos2App outputs (in ROI-PAC format) for running MintPy
# Rino Salman, Cheryl W. J. Tay
# Asian School of the Environment, NTU, Singapore
# May 2020


import isce, isceobj
import os, pathlib, glob,  shelve, argparse, numpy as np        
from osgeo import gdal     
from mintpy.utils import ptime, readfile, writefile, utils as ut
from mroipac.baseline.Baseline import Baseline
from isceobj.Planet.Planet import Planet
import xml.etree.ElementTree as ET


def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser(description='Prepare input files for running MintPy.')
    parser.add_argument('-w', '--working_directory', dest='workDir', type=str, default='./',
            help='Working directory ')
    parser.add_argument('-p', '--pair_directory', dest='pairDir', type=str,
            required=True, help='Working directory ')
    parser.add_argument('-d', '--dem', dest='dem', type=str, required=True, help='Path to dem.grd')
    return parser.parse_args()



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



def getCoordinatesAtCorners(lon, lat, losgeo):

    metadata = {}

    # lon
    data = readfile.read(lon)[0]
    r0, r1 = getNonzeroRowNumber(data)
    metadata['LON_REF1'] = str(data[r0, 0])
    metadata['LON_REF2'] = str(data[r0, -1])
    metadata['LON_REF3'] = str(data[r1, 0])
    metadata['LON_REF4'] = str(data[r1, -1])

    # lat
    data = readfile.read(lat)[0]
    r0, r1 = getNonzeroRowNumber(data)
    metadata['LAT_REF1'] = str(data[r0, 0])
    metadata['LAT_REF2'] = str(data[r0, -1])
    metadata['LAT_REF3'] = str(data[r1, 0])
    metadata['LAT_REF4'] = str(data[r1, -1])

    # losgeo
    data = readfile.read(losgeo, datasetName='az')[0]
    data[data == 0.] = np.nan
    azAngle = np.nanmean(data)
    # convert isce azimuth angle to roipac orbit heading angle
    headAngle = -1 * (270 + azAngle)
    headAngle -= np.round(headAngle / 360.) * 360.
    metadata['HEADING'] = str(headAngle)

    # length and width
    ds = gdal.Open(losgeo, gdal.GA_ReadOnly)
    metadata['FILE_LENGTH'] = ds.RasterYSize
    metadata['WIDTH'] = ds.RasterXSize

    # upper left corner coordinates, and pixel size
    st = gdal.Open(losgeo)
    xFirst, xres, xskew, yFirst, yskew, yres = st.GetGeoTransform()
    metadata['X_FIRST'] = xFirst
    metadata['Y_FIRST'] = yFirst
    metadata['X_STEP'] = xres
    metadata['Y_STEP'] = yres

    return metadata



def read_xml(xmlFile):
    root = ET.parse(xmlFile).getroot()
    xmlDict = {}
    for child in root.iter('property'):
        key = child.get('name')
        value = child.find('value').text
        xmlDict[key] = value
        # print(key, value)
    return xmlDict



def getFromXml(metadata, xmlFileTrack, preprocessXml):
    
    # Convert xml files to dictionary
    xmlFileTrackDict = read_xml(xmlFileTrack)
    preprocessXmlDict = read_xml(preprocessXml)

    # radar wavelength
    metadata['WAVELENGTH'] = float(xmlFileTrackDict['radarwavelength'])

    # rangePixelSize
    metadata['RANGE_PIXEL_SIZE'] = float(xmlFileTrackDict['rangepixelsize'])

    # prf
    metadata['PRF'] = float(xmlFileTrackDict['pulserepetitionfrequency'])

    # azimuthPixelSize
    metadata['AZIMUTH_PIXEL_SIZE'] = float(xmlFileTrackDict['azimuthpixelsize'])

    # azimuth look
    al1 = int(preprocessXmlDict['numberofazimuthlooks1'])
    al2 = int(preprocessXmlDict['numberofazimuthlooks2'])
    al = al1 * al2
    metadata['ALOOKS'] = al

    # range look
    rl1 = int(preprocessXmlDict['numberofrangelooks1'])
    rl2 = int(preprocessXmlDict['numberofrangelooks2'])
    rl = rl1 * rl2
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
    metadata['STARTING_RANGE'] = mFrame._startingRange
    metadata['POLARIZATION'] = str(mFrame._polarization).replace('/', '')
    if metadata['POLARIZATION'].startswith("b'"):
        metadata['POLARIZATION'] = metadata['POLARIZATION'][2:4]
    metadata['trackNumber'] = mFrame._trackNumber
    metadata['orbitNumber'] = mFrame._orbitNumber

    timeSeconds = (mFrame._sensingStart.hour * 3600.0 +
                    mFrame._sensingStart.minute * 60.0 +
                    mFrame._sensingStart.second)
    metadata['CENTER_LINE_UTC'] = timeSeconds

    return metadata, metadataBaseline
    


def writeToSlc(metadata, metadataBaseline, masterDate, slaveDate):

    for j in range(4):
        if j==0:
            metadata['FILE_TYPE'] = '.unw' 
            metadata['UNIT'] = 'radian' 
            rscFile = glob.glob(os.path.join('insar', 'filt_*28alks.unw.geo'))[0] + '.rsc'
            metadata = readfile.standardize_metadata(metadata)
            if rscFile:
                print('writing ', rscFile)
                writefile.write_roipac_rsc(metadata, rscFile)
        elif j==1:
            metadata['FILE_TYPE'] = '.cor' 
            metadata['UNIT'] = '1' 
            rscFile = glob.glob(os.path.join('insar', '*28alks.cor.geo'))[0] + '.rsc'
            metadata = readfile.standardize_metadata(metadata)
            if rscFile:
                print('writing ', rscFile)
                writefile.write_roipac_rsc(metadata, rscFile)
        elif j==2:
            metadata['FILE_TYPE'] = '.conncomp' 
            metadata['UNIT'] = '1' 
            rscFile = glob.glob(os.path.join('insar', 'filt*28alks.unw.conncomp.geo'))[0] + '.rsc'
            metadata = readfile.standardize_metadata(metadata)
            if rscFile:
                print('writing ', rscFile)
                writefile.write_roipac_rsc(metadata, rscFile)
        else:
            rscFile = os.path.join('insar', str(masterDate[2:])+'_'+str(slaveDate[2:])+'_baseline.rsc')
            metadataBaseline = readfile.standardize_metadata(metadataBaseline)
            if rscFile:
                print('writing ', rscFile)
                writefile.write_roipac_rsc(metadataBaseline, rscFile)



def getDem(losgeo, dem, scriptDir):
    src = gdal.Open(losgeo)
    ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
    lrx = ulx + (src.RasterXSize * xres)
    lry = uly + (src.RasterYSize * yres)

    demOut = dem.split('.')[0] + 'Crop'
    reg = '-R%s/%s/%s/%s'%(ulx,lrx,lry,uly)
    inc = '-I%s/%s'%(xres,xres)
    print(reg)
    cek = 'grdinfo {}'.format(dem)
    cmd = 'grdsample %s %s %s -G%s -r'%(dem,reg,inc,demOut+'.grd')
    os.system(cek)
    os.system(cmd)

    src = '%s/grd2dem.pl'%scriptDir
    cmd = '%s %s'%(src,demOut)
    os.system(cmd)



def incidenceAngleAndSlantRangeDistance(losgeo):
    """Calculate the corresponding slant range distance given an incidence angle

    Law of sines:
               r + H                   r               range_dist
       --------------------- = ----------------- = ------------------ = 2R
        sin(pi - inc_angle)     sin(look_angle)     sin(range_angle)

    where range_angle = inc_angle - look_angle
          R is the radius of the circumcircle.

    link: http://www.ambrsoft.com/TrigoCalc/Triangle/BasicLaw/BasicTriangle.htm

    Parameters: atr         - dict, metadata including the following items:
                                  EARTH_RADIUS
                                  HEIGHT
                inc_angle   - float / np.ndarray, incidence angle in degree
    Returns:    slant_range - float, slant range distance
    """
    
    # read attribute
    unwgeo = glob.glob(os.path.join('insar','*28alks.unw.geo'))[0]
    atr = readfile.read_attribute(unwgeo)
 
    # read incidence angle
    incAngle = readfile.read(losgeo, datasetName = 'incidenceAngle')[0]
   
    # compute slant range distance 
    if isinstance(incAngle, str):
        incAngle = float(incAngle)
    incAngle = np.array(incAngle, dtype=np.float32) / 180 * np.pi
    r = float(atr['EARTH_RADIUS'])
    H = float(atr['HEIGHT'])

    # calculate 2R based on the law of sines
    R2 = (r + H) / np.sin(np.pi - incAngle)

    lookAngle = np.arcsin( r / R2 )
    rangeAngle = incAngle - lookAngle
    rangeDist = R2 * np.sin(rangeAngle)

    # save
    Dict = {}
    Dict['incidenceAngle'] = incAngle
    Dict['slantRangeDistance'] = rangeDist

    geomOut = os.path.join('insar','geometry.trans')
    writefile.write(Dict, out_file = geomOut, metadata = atr)



def copyToMintpyFolder(cwd, date12, scriptDir, counter):

    mintpyDir = os.path.join(cwd, 'mintpy', 'interferograms', date12)
    if not os.path.isdir(mintpyDir):
        os.makedirs(mintpyDir)

    unwgeo = glob.glob(os.path.join('insar', 'filt_*lks.unw.geo'))
    corgeo = glob.glob(os.path.join('insar', '*lks.cor.geo'))
    conncompgeo = glob.glob(os.path.join('insar', 'filt_*lks.unw.conncomp.geo'))
    baseline = glob.glob(os.path.join('insar', '*baseline.rsc'))
        
    # .unw, .cor, .conncomp
    a,b,c = unwgeo[0].split('.') 
    d,e = a.split('/') 
    aa,bb,cc = corgeo[0].split('.') 
    dd,ee = aa.split('/')
    aaa,bbb,ccc,ddd = conncompgeo[0].split('.') 
    eee,fff = aaa.split('/')
    for k in range(5):
        # copy .unw and .cor
        if k==0:
           unwSrc = a + '.unw.geo'
           unwDst = e + '.unw'
           corSrc = aa + '.cor.geo'
           corDst = ee + '.cor'
           cmd1 = 'cp %s %s'%(unwSrc, os.path.join(mintpyDir, unwDst))
           cmd2 = 'cp %s %s'%(corSrc, os.path.join(mintpyDir, corDst))
           os.system(cmd1); os.system(cmd2)
        # copy .rsc (metadata in roipac format)
        elif k==1:
           unwSrc = a + '.unw.geo.rsc'
           unwDst = e + '.unw.rsc'
           corSrc = aa + '.cor.geo.rsc'
           corDst = ee + '.cor.rsc'
           cmd1 = 'cp %s %s'%(unwSrc, os.path.join(mintpyDir, unwDst))
           cmd2 = 'cp %s %s'%(corSrc, os.path.join(mintpyDir, corDst))
           os.system(cmd1); os.system(cmd2)
        # copy .xml
        elif k==2:
           unwSrc = a + '.unw.geo.xml'
           unwDst = e + '.unw.xml'
           corSrc = aa + '.cor.geo.xml'
           corDst = ee + '.cor.xml'
           cmd1 = 'cp %s %s'%(unwSrc, os.path.join(mintpyDir, unwDst))
           cmd2 = 'cp %s %s'%(corSrc, os.path.join(mintpyDir, corDst))
           os.system(cmd1); os.system(cmd2)
        # copy .vrt
        elif k==3:
           unwSrc = a + '.unw.geo.vrt'
           unwDst = e + '.unw.vrt'
           corSrc = aa + '.cor.geo.vrt'
           corDst = ee + '.cor.vrt'
           cmd1 = 'cp %s %s'%(unwSrc, os.path.join(mintpyDir, unwDst))
           cmd2 = 'cp %s %s'%(corSrc, os.path.join(mintpyDir, corDst))
        # copy .conncomp
        else:
           conncompSrc = aaa + '.unw.conncomp.geo'
           conncompDst = fff + '.conncomp.byt'
           cmd1 = 'cp %s %s'%(conncompSrc, os.path.join(mintpyDir, conncompDst))
           cmd2 = 'cp %s %s'%(conncompSrc+'.xml', os.path.join(mintpyDir, conncompDst+'.xml'))
           cmd3 = 'cp %s %s'%(conncompSrc+'.vrt', os.path.join(mintpyDir, conncompDst+'.vrt'))
           cmd4 = 'cp %s %s'%(conncompSrc+'.rsc', os.path.join(mintpyDir, conncompDst+'.rsc'))
           os.system(cmd1); os.system(cmd2); os.system(cmd4); os.system(cmd4)

    # copy baseline
    f,g = baseline[0].split('/')
    bslSrc = baseline[0]
    bslDst = g
    cmd = 'cp %s %s'%(bslSrc,os.path.join(mintpyDir, bslDst))
    os.system(cmd)

    # copy parameter setting
    if counter==0:
       cmd = 'cp %s/sumatranfaultAlos2.txt %s'%(scriptDir, os.path.join(cwd, 'mintpy'))
       print(cmd)
       os.system(cmd)

    # copy .los.geo and a python script for modifying inputs/geometryGeo.h5 after MintPy --dostep load_data
    if counter==0:
       # copy .los.geo
       losgeo = glob.glob(os.path.join('insar', '*28alks.los.geo'))[0]
       h,i,j = losgeo.split('.')
       k,l = h.split('/')
       losgeoSrc = losgeo
       losgeoDst = l + '.los.geo'
       losgeoRscSrc = a + '.unw.geo.rsc'
       losgeoRscDst = l + '.los.geo.rsc'
       cmd1 = 'cp %s %s'%(losgeoSrc, os.path.join(mintpyDir, losgeoDst))
       cmd2 = 'cp %s %s'%(losgeoSrc+'.xml', os.path.join(mintpyDir, losgeoDst+'.xml'))
       cmd3 = 'cp %s %s'%(losgeoSrc+'.vrt', os.path.join(mintpyDir, losgeoDst+'.vrt'))
       cmd4 = 'cp %s %s'%(losgeoRscSrc, os.path.join(mintpyDir, losgeoRscDst))
       os.system(cmd1); os.system(cmd2); os.system(cmd3); os.system(cmd4)

       # copy script for modifying geometryGeo.h5
       inputDir = os.path.join(cwd, 'mintpy', 'inputs')
       if not os.path.isdir(inputDir):
          os.makedirs(inputDir)
       cmd = 'cp %s/modifyGeometryGeo.py %s'%(scriptDir, inputDir)
       os.system(cmd)



if __name__ == '__main__':
    '''
    Main driver.
    '''

#    # getting the input
    inps = cmdLineParse()
    dem = os.path.join(os.path.abspath(inps.workDir), inps.dem)
    scriptDir = pathlib.Path(__file__).parent.absolute()

    # current directory
    cwd = os.getcwd()

    pairs = np.genfromtxt(inps.pairDir,str)
    for i in range(len(pairs)):

        # go to interferogram folder
        pair = pairs[i]
        os.chdir('intf/'+pair)
        print('')
        print('Current directory: %s'%os.getcwd())
        print('')

	# read longitude and latitude at corner 1/2/3/4
        lon = glob.glob(os.path.join('insar','*28alks.lon'))[0]
        lat = glob.glob(os.path.join('insar','*28alks.lat'))[0]
        losgeo = glob.glob(os.path.join('insar','*28alks.los.geo'))[0]
        metadata = getCoordinatesAtCorners(lon, lat, losgeo)

	# get earthRadius, heading, altitude, baselines
        masterDate = os.path.basename(pair).split('_')[0]
        slaveDate = os.path.basename(pair).split('_')[1]
        masterSlc = os.path.join(cwd, 'slc', masterDate, 'data')
        slaveSlc = os.path.join(cwd, 'slc', slaveDate, 'data')
        metadata, metadataBaseline = getRadiusHeadingBaseline(metadata, masterSlc, slaveSlc)

	# get radarWavelength, startingRange, rangePixelSize, prf, azimuthPixelSize, A/R_looks
        xmlFileTrack = glob.glob('*track.xml')[0]
        preprocessXml = 'PICKLE/preprocess.xml'
        metadata = getFromXml(metadata, xmlFileTrack, preprocessXml)

	# get the rest
        metadata['ANTENNA_SIDE'] = '-1'
        metadata['ORBIT_DIRECTION'] = 'DESCENDING'
        metadata['PLATFORM'] = 'ALOS2'
        metadata['PROCESSOR'] = 'isce'
        metadata['DATE12'] = str(masterDate[2:])+'-'+str(slaveDate[2:])
	
	# write to .rsc file
        writeToSlc(metadata, metadataBaseline, masterDate, slaveDate)

        # prepare dem and its metadata (hard-coded: path to dem.grd and grd2dem.pl)
        # also prepare incidence angle and slant range distance
        if i==0:
            getDem(losgeo, dem, scriptDir)
            ###incidenceAngleAndSlantRangeDistance(losgeo) #Mintpy can't read this output

        # create MintPy directory and copying files
        date12 = str(masterDate)+'_'+str(slaveDate)
        copyToMintpyFolder(cwd, date12, scriptDir, i)
           
        # go back to previous directory
        os.chdir(cwd)
