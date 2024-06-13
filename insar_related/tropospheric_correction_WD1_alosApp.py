import mintpy
#import mintpy.workflow
from mintpy.utils import utils1, readfile, writefile
from mintpy import tropo_gacos, tropo_pyaps3
import os
import ref_point


# data information
dates = '221110-221124'
looks = '5rlks_28alks'
dates_rlks_alks = '{}_{}'.format(dates,looks)
refDate = '221110'

# create .rsc for *.msk.unw, .lat, and .lon
unw = 'filt_{}_msk.unw'.format(dates_rlks_alks)
los = '{}.los'.format(dates_rlks_alks)
hgt = '{}.hgt'.format(dates_rlks_alks)
cor = '{}.cor'.format(dates_rlks_alks)
wbd = '{}.wbd'.format(dates_rlks_alks)
trackFile = '{}.track.xml'.format(refDate)
os.chdir('../')
os.system('''prep_isce.py -f insar/{}.geo -g insar/ -m {}'''.format(unw,trackFile))
os.chdir('insar')
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(unw,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(los,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(hgt,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(cor,trackFile))
os.system('''prep_isce.py -f {} -g insar/ -m ../{}'''.format(wbd,trackFile))

# geocode manually *msk.unw, .los, and .height
lonFile = '{}.lon'.format(dates_rlks_alks)
latFile = '{}.lat'.format(dates_rlks_alks)
unwGeo = 'geo_filt_msk.unw'
losGeo = 'geo_los.los'
hgtGeo = 'geo_hgt.hgt'
corGeo = 'geo_cor.cor'
wbdGeo = 'geo_wbd.wbd'
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(unw,latFile,lonFile,unwGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(los,latFile,lonFile,losGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(hgt,latFile,lonFile,hgtGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(cor,latFile,lonFile,corGeo))
os.system('''geocode.py {} --lat-file {} --lon-file {} -o {}'''.format(wbd,latFile,lonFile,wbdGeo))

# generate water body in MintPy format
wbdGeoMintpy = 'waterBody.geo'
os.system('''generate_mask.py {} -M 0.5 -o {}'''.format(wbdGeo,wbdGeoMintpy))

# masking the files
unwGeoWbd = 'geo_filt_msk_wbd.unw'
losGeoWbd = 'geo_los_wbd.los'
hgtGeoWbd = 'geo_hgt_wbd.hgt'
os.system('''mask.py {} -m {} -o {}'''.format(unwGeo,wbdGeoMintpy,unwGeoWbd))
os.system('''mask.py {} -m {} -o {}'''.format(losGeo,wbdGeoMintpy,losGeoWbd))
os.system('''mask.py {} -m {} -o {}'''.format(hgtGeo,wbdGeoMintpy,hgtGeoWbd))

# read attribute
atr = readfile.read_attribute(unwGeo)

# update existing attribute
atrroipac = readfile.read_roipac_rsc('../data.rsc')
atr['DATE12'] = dates
utils1.add_attribute(unwGeo, atr)

# spatial referencing 
ref_lat, ref_lon = -7.156991, 107.526131
cmd = '{} --lat {} --lon {} --write-data'.format(unwGeoWbd,ref_lat,ref_lon)
ref_point.main(cmd.split())

# incidence angle
dsDict = {}
dsDict['incidenceAngle']=readfile.read(losGeoWbd, datasetName='incidenceAngle')[0]
dsDict['height']=readfile.read(hgtGeoWbd, datasetName='height')[0]
writefile.write(dsDict, 'geometry.h5', metadata=atr)

# PyAPS correction
correctedUnw = 'geo_filt_msk_wbd_ERA5.unw'
os.system('''tropo_pyaps3.py -f {} -g geometry.h5 -o {}'''.format(unwGeoWbd,correctedUnw))

# GACOS correction
correctedUnw = 'geo_filt_msk_wbd_GACOS.unw'
os.system('''tropo_gacos.py -f {} -g geometry.h5 --dir ./GACOS -o {}'''.format(unwGeoWbd,correctedUnw))
