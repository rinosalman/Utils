#!/usr/bin/env python3
"""
Map tiler PGE wrapper to generate map tiles following the
OSGeo Tile Map Service Specification.
"""

from subprocess import check_call

import os, sys, argparse, logging, traceback
import numpy as np
from osgeo import gdal
from gdalconst import GA_ReadOnly


gdal.UseExceptions() # make GDAL raise python exceptions


log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('create_tiles')


BASE_PATH = os.path.dirname(__file__)


def call_noerr(cmd):
    """Run command and warn if exit status is not 0."""

    try: check_call(cmd, shell=True)
    except Exception as e:
        logger.warn("Got exception running {}: {}".format(cmd, str(e)))
        logger.warn("Traceback: {}".format(traceback.format_exc()))


def get_clims(raster, band, clim_min_pct=None, clim_max_pct=None, nodata=None):
    """Get data absolute min/max values as well as min/max percentile values
       for a given GDAL-recognized file format for a particular band."""

    # load raster
    gd = gdal.Open(raster, GA_ReadOnly)

    # get number of bands
    bands = gd.RasterCount

    # process the raster
    b = gd.GetRasterBand(band)
    d = b.ReadAsArray()
    logger.info("band data: {}".format(d))
    # fetch max and min
    # min = band.GetMinimum()
    # max = band.GetMaximum()
    if nodata is not None:
        d = np.ma.masked_equal(d, nodata)
    min = np.amin(d)
    max = np.amax(d)
    min_pct = np.percentile(d, clim_min_pct) if clim_min_pct is not None else None
    max_pct = np.percentile(d, clim_max_pct) if clim_max_pct is not None else None

    logger.info("band {} absolute min/max: {} {}".format(band, min, max))
    logger.info("band {} {}/{} percentiles: {} {}".format(band, clim_min_pct,
                                                          clim_max_pct, min_pct,
                                                          max_pct))
    gd = None

    return min, max, min_pct, max_pct

def create_tiles(raster, band=1, cmap='jet', clim_min=None,
                 clim_max=None, clim_min_pct=None, clim_max_pct=None,
                  nodata=None):
    """Generate map tiles following the OSGeo Tile Map Service Specification."""

    # check mutually exclusive args
    if clim_min is not None and clim_min_pct is not None:
        raise(RuntimeError("Cannot specify both clim_min and clim_min_pct."))
    if clim_max is not None and clim_max_pct is not None:
        raise(RuntimeError("Cannot specify both clim_max and clim_max_pct."))

    # get clim
    min, max, min_pct, max_pct = get_clims(raster, band,
                                           clim_min_pct if clim_min_pct is not None else 20,
                                           clim_max_pct if clim_max_pct is not None else 80,
                                           nodata)

    # overwrite if options not specified
    if clim_min is not None: min = clim_min
    if clim_max is not None: max = clim_max
    if clim_min_pct is not None: min = min_pct
    if clim_max_pct is not None: max = max_pct

    # convert to geotiff
    logger.info("Generating GeoTIFF.")
    tif_file = "{}.tif".format(os.path.basename(raster))
    if os.path.exists(tif_file): os.unlink(tif_file)
    cmd = "isce2geotiff.py -i {} -o {} -c {:f} {:f} -b {} -m {}"
    check_call(cmd.format(raster, tif_file, min, max, band-1, cmap), shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raster", help="input raster file (any GDAL-recognized file format)")
    parser.add_argument("-b", "--band", dest="band", type=int,
                        default=1, help="raster band")
    parser.add_argument("-m", "--cmap", dest="cmap", type=str,
                        default='jet', help="matplotlib colormap")
    parser.add_argument("--clim_min", dest="clim_min", type=float,
                        default=None, help="color limit min value")
    parser.add_argument("--clim_max", dest="clim_max", type=float,
                        default=None, help="color limit max value")
    parser.add_argument("--clim_min_pct", dest="clim_min_pct", type=float,
                        default=None, help="color limit min percent")
    parser.add_argument("--clim_max_pct", dest="clim_max_pct", type=float,
                        default=None, help="color limit max percent")
    parser.add_argument("--nodata", dest="nodata", type=float,
                        default=None, help="nodata value")
    args = parser.parse_args()
    status = create_tiles(args.raster, args.band, args.cmap,
                          args.clim_min, args.clim_max, args.clim_min_pct,
                          args.clim_max_pct,  args.nodata)

