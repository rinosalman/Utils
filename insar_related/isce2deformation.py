#all functions are all from MintPy
#13 Oct 2020

from osgeo import gdal   
import glob,os
from mintpy.utils import readfile
import numpy as np



def azimuth2heading_angle(azAngle):
    headAngle = -1 * (180 + azAngle + 90)
    headAngle -= np.round(headAngle / 360.) * 360.
    return headAngle

def get_unit_vectors(incAngle,headAngle):

    #convert to radian
    incAngle *= np.pi/180.
    headAngle *= np.pi/180.

    unitVec = [np.sin(incAngle) * np.cos(headAngle) * -1,
               np.sin(incAngle) * np.sin(headAngle),
               np.cos(incAngle)]
    return unitVec

if __name__ == '__main__':
    '''
    Main driver
    '''
    #geocoded original interferogram
    intOri = glob.glob('diff_*_5rlks_28alks_ori.int.geo')[0]

    #geocoded corrected interferogram
    intt = glob.glob('diff_*_5rlks_28alks.int.geo')[0]

    #geocoded unwrapped phase
    unwGeo = glob.glob('filt_*5rlks_28alks.unw.geo')[0]

    #translate to grd
    os.system("gdal_translate -of GMT -b 1 {} {}".format(intOri,intOri+'.grd'))
    os.system("gdal_translate -of GMT -b 1 {} {}".format(intt,intt+'.grd'))
    os.system("gdal_translate -of GMT -b 2 {} {}".format(unwGeo,unwGeo+'.grd'))
    
    #convert to xyz
    os.system("gmt grd2xyz {} > {}".format(unwGeo+'.grd',unwGeo+'.xyz'))

    #read in incidence and azimuth angles (units in degree)
    losgeo = glob.glob('*5rlks_28alks.los.geo')[0]
    incAngle = readfile.read(losgeo, datasetName = 'incidenceAngle')[0]
    azAngle = readfile.read(losgeo, datasetName = 'az')[0]

    #convert azimuth angle to heading angle
    headAngle = azimuth2heading_angle(azAngle)

    #get LOS unit vectors
    unitVec = get_unit_vectors(incAngle,headAngle)
    
    #get unit vector for each component
    uvE=np.matrix.flatten(unitVec[0]).tolist()
    uvN=np.matrix.flatten(unitVec[1]).tolist()
    uvU=np.matrix.flatten(unitVec[2]).tolist()

    #grab coordinates
    lonLatLos = np.loadtxt(unwGeo+'.xyz',float)

    #save
    lonLatE=np.vstack([lonLatLos[:,0],lonLatLos[:,1],uvE])
    lonLatN=np.vstack([lonLatLos[:,0],lonLatLos[:,1],uvN])
    lonLatU=np.vstack([lonLatLos[:,0],lonLatLos[:,1],uvU])
    unitVectorsENU=np.vstack([uvE,uvN,uvU])
    np.savetxt('lonLatE.txt',np.array(lonLatE).T)
    np.savetxt('lonLatN.txt',np.array(lonLatN).T)
    np.savetxt('lonLatU.txt',np.array(lonLatU).T)
    np.savetxt('unitVectorsENU.txt',np.array(unitVectorsENU).T)
    
    #convert to grd
    unwGrd = glob.glob('filt_*5rlks_28alks.unw.geo.grd')[0]
    os.system("gmt xyz2grd lonLatE.txt `gmt grdinfo {} -I-` `gmt grdinfo {} -I` -GunitVectorE.grd".format(unwGrd,unwGrd))
    os.system("gmt xyz2grd lonLatN.txt `gmt grdinfo {} -I-` `gmt grdinfo {} -I` -GunitVectorN.grd".format(unwGrd,unwGrd))
    os.system("gmt xyz2grd lonLatU.txt `gmt grdinfo {} -I-` `gmt grdinfo {} -I` -GunitVectorU.grd".format(unwGrd,unwGrd))
