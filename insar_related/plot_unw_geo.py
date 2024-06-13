from osgeo import gdal            ## GDAL support for reading virtual files
import os                         ## To create and remove directories
import matplotlib.pyplot as plt   ## For plotting
import numpy as np                ## Matrix calculations
import glob                       ## Retrieving list of files
import isce 


# Utility function to load data
def loadData(infile, band=1, background=None):
    ds = gdal.Open(infile, gdal.GA_ReadOnly)
    # Data array
    data = ds.GetRasterBand(band).ReadAsArray()

    # put all zero values to nan and do not plot nan
    if background is None:
       try:
           data[data==0]=np.nan
       except:
           pass

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
    unwGeo = glob.glob('filt_*5rlks*28alks.unw.geo')[0]
    unwGeoConv = 'for_plot.unw.geo'
    print(unwGeo)
    print(unwGeoConv)
 
    # convert to .geo
    os.system("imageMath.py -e a_1 --a %s -o %s -t FLOAT -s BIL"%(unwGeo,unwGeoConv))
     
    # load cropped data and plot
    aspect=1
    colormap='jet'
    unwGeoPlot, unwGeoExt = loadData(unwGeoConv+'.vrt')
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.imshow(unwGeoPlot, extent=unwGeoExt, cmap=colormap)
    plt.colorbar()
    ax1.title.set_text('Unwrapped')
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.set_aspect(aspect)
    plt.savefig("unwrapped_geo_%s.png"%intf.split("_")[1],bbox_inches='tight')
    #plt.show()


    unwGeoPlot = None
