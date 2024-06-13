from osgeo import gdal            ## GDAL support for reading virtual files
import os                         ## To create and remove directories
import matplotlib.pyplot as plt   ## For plotting
import numpy as np                ## Matrix calculations
import glob                       ## Retrieving list of files
import isce 


# Utility function to load data
def loadData(infile, band=1):
    ds = gdal.Open(infile, gdal.GA_ReadOnly)
    # Data array
    data = ds.GetRasterBand(band).ReadAsArray()
    # Map extent
    trans = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    extent = [trans[0], trans[0] + xsize * trans[1],
            trans[3] + ysize*trans[5], trans[3]]
    
    ds = None
    return data, extent



if __name__ == '__main__':
    '''
    Main driver.
    '''

    # crop interferogram and interferogram-ionospheric correction
    intf = glob.glob('diff_*ori.int')[0]
    #intfMinIon = glob.glob('diff_*lks.int')[1]
    intfMinIon = glob.glob('diff_*5rlks*28alks.int')[0]
    intfGeo = intf+'.geo'
    intfMinIonGeo = intfMinIon+'.geo'
    intfCropped = 'intf_'+intf.split("_")[1]+'_cropped.vrt'
    intMinIonCropped = 'corrected_intf_'+intf.split("_")[1]+'_cropped.vrt'
    print('%s,%s'%(intf,intfMinIon))
 
    # convert to .geo
    os.system("imageMath.py -e='abs(a); arg(a)' --a=./%s -o %s -t FLOAT -s BIL"%(intf,intfGeo))
    os.system("imageMath.py -e='abs(a); arg(a)' --a=./%s -o %s -t FLOAT -s BIL"%(intfMinIon,intfMinIonGeo))
     
    # crop
    os.system("gdal_translate -of VRT -b 2 -projwin 0 2000 2814  4189 %s %s"%(intfGeo+'.vrt',intfCropped))
    os.system("gdal_translate -of VRT -b 2 -projwin 0 2000 2814  4189 %s %s"%(intfMinIonGeo+'.vrt',intMinIonCropped))
   
    # load cropped data and plot
    aspect=1
    colormap='jet'
    intfCroppedPlot, intfExt = loadData(intfCropped)
    intMinIonCroppedPlot, ionExt = loadData(intMinIonCropped)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    plt.imshow(intfCroppedPlot,clim=[-3.14,3.14], extent=intfExt, cmap=colormap)
    plt.gca().invert_xaxis()
    ax1.title.set_text('Interferogram')
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_aspect(aspect)   
    ax1 = fig.add_subplot(122)
    plt.imshow(intMinIonCroppedPlot,clim=[-3.14,3.14], extent=ionExt, cmap=colormap)
    plt.gca().invert_xaxis()
    ax1.title.set_text('Interferogram - Iono')
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_aspect(aspect)   
    #plt.savefig("intf_correctedIntf_%s.png"%intf.split("_")[1],bbox_inches='tight')
    plt.show()


    intfCroppedPlot = None
    ionCroppedPlot = None
