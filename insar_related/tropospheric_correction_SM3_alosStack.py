import mintpy
from mintpy.utils import utils1, readfile
from mintpy import tropo_gacos, tropo_pyaps3
import os
import ref_point


'''
README
Before executing this command, run MintPy to generate geometryRadar.h5
'''


def cmdLineParse():
    '''
    command line parser.
    '''
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='apply troposphere correction using ERA5.h5 data')
    parser.add_argument('-pair_dates', dest='pair_dates', type=str, required=True,
            help = 'dates of the interferogram pair.')

    if len(sys.argv) <= 1:
        print('')
        parser.print_help()
        sys.exit(1)
    else:
        return parser.parse_args()


if __name__ == '__main__':

    inp = cmdLineParse()
    dates = inp.pair_dates


    ## data information
    #dates = '221107-221121'
    looks = '16rlks_32alks'
    dates_rlks_alks = '{}_{}'.format(dates,looks)
    refDate = '220926'


    ## create .rsc
    unw = 'filt_{}_msk.unw'.format(dates_rlks_alks)
    trackFile = '{}.track.xml'.format(refDate)
    os.chdir('../')
    os.system('''prep_isce.py -f insar/{}.geo -g ../../dates_resampled/{}/insar/ -m {}'''.format(unw,refDate,trackFile))
    os.chdir('insar/')


    ## copy .los and .hgt
    datesResampled = '../../../dates_resampled/{}/insar'.format(refDate)
    los = '{}_{}.los'.format(refDate,looks)
    hgt = '{}_{}.hgt'.format(refDate,looks)
    os.system("cp {}/{}* .".format(datesResampled,los))
    os.system("cp {}/{}* .".format(datesResampled,hgt))


    # update existing attribute for troposhere correction
    atr = readfile.read_attribute(unw)
    atrroipac = readfile.read_roipac_rsc('../data.rsc')
    atr['DATE12'] = dates
    atr['CENTER_LINE_UTC'] = atrroipac['CENTER_LINE_UTC']
    atr['WAVELENGTH'] = atrroipac['WAVELENGTH']
    utils1.add_attribute(unw, atr)


    ## geocode manually *msk.unw, .hgt and .los
    geomFile = '../../inputs/geometryRadar.h5'
    geomFileWbd = 'geometryRadarWbd.h5'
    unwGeo = 'geo_filt_msk.unw'
    losGeo = 'geo_los.los'
    hgtGeo = 'geo_hgt.hgt'
    step = 0.000833334 # degrees, ~90 m
    geomFileGeo = 'geo_'+geomFileWbd
    os.system('''geocode.py {} -l {} --lalo -{} {} -o {}'''.format(unw,geomFile,step,step,unwGeo))
    os.system('''geocode.py {} -l {} --lalo -{} {} -o {}'''.format(los,geomFile,step,step,losGeo))
    os.system('''geocode.py {} -l {} --lalo -{} {} -o {}'''.format(hgt,geomFile,step,step,hgtGeo))
    os.system('''geocode.py {} -l {} --lalo -{} {} -o {}'''.format(geomFile,geomFile,step,step,geomFileGeo))


    ## spatial referencing 
    ref_lat, ref_lon = -6.911717, 106.727850
    cmd = '{} --lat {} --lon {} --write-data'.format(unwGeo,ref_lat,ref_lon)
    ref_point.main(cmd.split())


    ## PyAPS correction
    correctedUnw = 'geo_filt_msk_ERA5.unw'
    correctedUnwERAh5 = 'geo_filt_msk_ERA5.h5'
    os.system('''tropo_pyaps3.py -f {} -g {} -o {}'''.format(unwGeo,geomFileGeo,correctedUnwERAh5))
    os.system('''tropo_pyaps3.py -f {} -g {} -o {}'''.format(unwGeo,geomFileGeo,correctedUnw))

    ## GACOS correction
    #correctedUnw = 'geo_filt_msk_GACOS.unw'
    #correctedUnwGACOSh5 = 'geo_filt_msk_GACOS.h5'
    #os.system('''tropo_gacos.py -f {} -g {} --dir ./GACOS -o {}'''.format(unwGeo,geomFileGeo,correctedUnwGACOSh5))
    #os.system('''tropo_gacos.py -f {} -g {} --dir ./GACOS -o {}'''.format(unwGeo,geomFileGeo,correctedUnw))

    # convertion to GMT format
    #os.system("save_gmt.py {}".format(correctedUnwERAh5))
    #os.system("save_gmt.py {}".format(correctedUnwGACOSh5))
