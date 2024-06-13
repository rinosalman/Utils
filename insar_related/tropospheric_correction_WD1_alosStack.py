import mintpy
from mintpy.utils import utils1, readfile
from mintpy import tropo_gacos, tropo_pyaps3
import os
import ref_point


'''
README
Before executing this command, run MintPy to generate geometryRadar.h5
'''

## data information
dates = '221110-221124'
looks = '5rlks_28alks'
dates_rlks_alks = '{}_{}'.format(dates,looks)
refDate = '221110'
filt = 32


## copy .los
datesResampled = '../../../../../dates_resampled/{}/insar/{}/filt_{}/'.format(refDate,looks,filt)
los = '{}_{}.los'.format(refDate,looks)
wbd = '{}_{}.wbd'.format(refDate,looks)
hgt = '{}_{}.hgt'.format(refDate,looks)
os.system("cp {}/{}* .".format(datesResampled,los))
os.system("cp {}/{}* .".format(datesResampled,wbd))
os.system("cp {}/{}* .".format(datesResampled,hgt))


# generate water body in MintPy format
wbdMintpy = 'wbd_mintpy.wbd'
os.system('''generate_mask.py {} -M 0.5 -o {}'''.format(wbd,wbdMintpy))


# masking the files
unw = 'filt_{}_msk.unw'.format(dates_rlks_alks)
unwWbd = 'filt_msk_wbd.unw'
losWbd = 'los_wbd.los'
hgtWbd = 'hgt_wbd.hgt'
geomFile = 'geometryRadar.h5'
geomFileWbd = 'geometryRadarWbd.h5'
os.system('''mask.py {} -m {} -o {}'''.format(unw,wbdMintpy,unwWbd))
os.system('''mask.py {} -m {} -o {}'''.format(los,wbdMintpy,losWbd))
os.system('''mask.py {} -m {} -o {}'''.format(hgt,wbdMintpy,hgtWbd))
os.system('''mask.py inputs/{} -m {} -o {}'''.format(geomFile,wbdMintpy,geomFileWbd))


# update existing attribute for troposhere correction
atr = readfile.read_attribute(unw)
atrroipac = readfile.read_roipac_rsc('../data.rsc')
atr['DATE12'] = dates
atr['CENTER_LINE_UTC'] = atrroipac['CENTER_LINE_UTC']
atr['WAVELENGTH'] = atrroipac['WAVELENGTH']
utils1.add_attribute(unwWbd, atr)


## geocode manually *msk.unw, .hgt and .los
unwGeo = 'geo_filt_msk.unw'
losGeo = 'geo_los.los'
wbdGeo = 'geo_wbd.wbd'
hgtGeo = 'geo_hgt.hgt'
step = 0.000833334 # degrees, ~90 m
geomFileGeo = 'geo_'+geomFileWbd
os.system('''geocode.py {} -l inputs/{} --lalo -{} {} -o {}'''.format(unwWbd,geomFile,step,step,unwGeo))
os.system('''geocode.py {} -l inputs/{} --lalo -{} {} -o {}'''.format(losWbd,geomFile,step,step,losGeo))
os.system('''geocode.py {} -l inputs/{} --lalo -{} {} -o {}'''.format(hgtWbd,geomFile,step,step,hgtGeo))
os.system('''geocode.py inputs/{} -l inputs/{} --lalo -{} {} -o {}'''.format(geomFile,geomFile,step,step,geomFileGeo))


## spatial referencing 
ref_lat, ref_lon = -7.156991, 107.526131
cmd = '{} --lat {} --lon {} --write-data'.format(unwGeo,ref_lat,ref_lon)
ref_point.main(cmd.split())


## PyAPS correction
correctedUnw = 'geo_filt_msk_ERA5.unw'
correctedUnwERAh5 = 'geo_filt_msk_ERA5.h5'
os.system('''tropo_pyaps3.py -f {} -g {} -o {}'''.format(unwGeo,geomFileGeo,correctedUnwERAh5))
os.system('''tropo_pyaps3.py -f {} -g {} -o {}'''.format(unwGeo,geomFileGeo,correctedUnw))

## GACOS correction
correctedUnw = 'geo_filt_msk_GACOS.unw'
correctedUnwGACOSh5 = 'geo_filt_msk_GACOS.h5'
os.system('''tropo_gacos.py -f {} -g {} --dir ./GACOS -o {}'''.format(unwGeo,geomFileGeo,correctedUnwGACOSh5))
os.system('''tropo_gacos.py -f {} -g {} --dir ./GACOS -o {}'''.format(unwGeo,geomFileGeo,correctedUnw))

# convertion to GMT format
os.system("save_gmt.py {}".format(correctedUnwERAh5))
os.system("save_gmt.py {}".format(correctedUnwGACOSh5))
