from osgeo import gdal            ## GDAL support for reading virtual files
import os                         ## To create and remove directories
import matplotlib.pyplot as plt   ## For plotting
import numpy as np                ## Matrix calculations
import glob                       ## Retrieving list of files
import isce 


def plotdata(GDALfilename,band=1,title=None,colormap='gray',aspect=1, datamin=None, datamax=None,draw_colorbar=True,colorbar_orientation="horizontal",background=None):
    ds = gdal.Open(GDALfilename, gdal.GA_ReadOnly)
    data = ds.GetRasterBand(band).ReadAsArray()
    transform = ds.GetGeoTransform()
    ds = None
    
    # getting the min max of the axes
    firstx = transform[0]
    firsty = transform[3]
    deltay = transform[5]
    deltax = transform[1]
    lastx = firstx+data.shape[1]*deltax
    lasty = firsty+data.shape[0]*deltay
    ymin = np.min([lasty,firsty])
    #ymax = np.max([lasty,firsty])
    ymax = 6
    #xmin = np.min([lastx,firstx])
    xmin = 95
    #xmax = np.max([lastx,firstx])
    xmax = 97

    # put all zero values to nan and do not plot nan
    if background is None:
        try:
            data[data==0]=np.nan
        except:
            pass

    mindata=np.min(data)
    maxdata=np.max(data)
    b=data.flatten()
    print('min: %s'%np.min(b))
    print('max: %s'%np.max(b))

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111)
    cax = ax.imshow(data, vmin = datamin, vmax=datamax, cmap=colormap,extent=[xmin,xmax,ymin,ymax])
    ax.set_title(title)
    #if draw_colorbar is not None:
    #    cbar = fig.colorbar(cax,orientation=colorbar_orientation)
    ax.set_aspect(aspect)    
    #plt.savefig('unw.png')
    plt.show()
    data = None

#Utility function to load data
def loadData(infile, band=1):
    ds = gdal.Open(infile, gdal.GA_ReadOnly)
    #Data array
    data = ds.GetRasterBand(band).ReadAsArray()
    #Map extent
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
    #intf = glob.glob('diff*.int.geo.vrt')[0]
    #intfMinIon = glob.glob('diff*.int.geo.vrt')[1]
    intf = glob.glob('diff*.int.vrt')[0]
    intfMinIon = glob.glob('diff*.int.vrt')[1]
    intfCropped = 'intf_'+intf.split("_")[1]+'_cropped.vrt'
    intMinIonCropped = 'corrected_intf_'+intf.split("_")[1]+'_cropped.vrt'
     
    os.system("gdal_translate -of VRT -b 2 -projwin 0 5000 14000 9800 %s %s"%(intf,intfCropped))
    os.system("gdal_translate -of VRT -b 2 -projwin 0 2500 2800 4800 %s %s"%(intfMinIon,intMinIonCropped))
   
    # plot
    intfCroppedPlot, intfExt = loadData(intfCropped)
    intMinIonCroppedPlot, ionExt = loadData(intMinIonCropped)
    
    plt.figure('intf & intf-iono')
    plt.subplot(2,1,1)
    plt.imshow(intfCroppedPlot,clim=[-3.14,3.14], extent=intfExt, cmap='jet')
    plt.subplot(2,1,2)
    plt.imshow(intMinIonCroppedPlot,clim=[-3.14,3.14], extent=ionExt, cmap='jet')
    #plt.show()
    plt.savefig('intf_correctedIntf_%s.png'%intf.split("_")[1])

    intfCroppedPlot = None
    ionCroppedPlot = None
    
    #gdalfile='diff_170110-170516_1rlks_14alks.int.geo'
    #plotdata(gdalfile,2,title="int.geo",colormap='jet',datamin=-3.14,datamax=3.14)

    #ds=gdal.Open('diff_170110-170516_5rlks_28alks.int.geo.tif')
    #ds=gdal.Translate('output.tif',ds,projWin=[96.4,4.3,95,6])
    #ds=None
    #crop,cropext=loadData('filt_170110-170516_5rlks_28alks.unw.geo_crop.vrt')
    #plt.figure('crop')
    #plt.imshow(crop,clim=[-50.,50.],extent=cropext,cmap='jet')
    #plt.show()
