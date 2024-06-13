import re
import numpy as np
import glob
import os

#########################################################################
def read_binary(fname, shape, box=None, data_type='float32', byte_order='l',
                num_band=1, interleave='BIL', band=1, cpx_band='phase',
                xstep=1, ystep=1):
    """Read binary file using np.fromfile.
    Parameters: fname : str, path/name of data file to read
                shape : tuple of 2 int in (length, width)
                box   : tuple of 4 int in (x0, y0, x1, y1)
                data_type : str, data type of stored array, e.g.:
                    bool_
                    int8, int16, int32
                    float16, float32, float64
                    complex64, complex128
                byte_order      : str, little/big-endian
                num_band        : int, number of bands
                interleave : str, band interleav type, e.g.: BIP, BIL, BSQ
                band     : int, band of interest, between 1 and num_band.
                cpx_band : str, e.g.:
                    real,
                    imag, imaginary
                    phase,
                    mag, magnitude
                    cpx
                x/ystep  : int, number of pixels to pick/multilook for each output pixel
    Returns:    data     : 2D np.array
    Examples:   # ISCE files
                atr = read_attribute(fname)
                shape = (int(atr['LENGTH']), int(atr['WIDTH']))
                data = read_binary('filt_fine.unw', shape, num_band=2, band=2)
                data = read_binary('filt_fine.cor', shape)
                data = read_binary('filt_fine.int', shape, data_type='complex64', cpx_band='phase')
                data = read_binary('burst_01.slc', shape, data_type='complex64', cpx_band='mag')
                data = read_binary('los.rdr', shape, num_band=2, band=1)
    """
    length, width = shape
    if not box:
        box = (0, 0, width, length)

    if byte_order in ['b', 'big', 'big-endian', 'ieee-be']:
        letter, digit = re.findall('(\d+|\D+)', data_type)
        # convert into short style: float32 --> c4
        if len(letter) > 1:
            letter = letter[0]
            digit = int(int(digit) / 8)
        data_type = '>{}{}'.format(letter, digit)

    # read data
    interleave = interleave.upper()
    if interleave == 'BIL':
        data = np.fromfile(fname,
                           dtype=data_type,
                           count=box[3]*width*num_band).reshape(-1, width*num_band)
        data = data[box[1]:box[3],
                    width*(band-1)+box[0]:width*(band-1)+box[2]]

    elif interleave == 'BIP':
        data = np.fromfile(fname,
                           dtype=data_type,
                           count=box[3]*width*num_band).reshape(-1, width*num_band)
        data = data[box[1]:box[3],
                    np.arange(box[0], box[2])*num_band+band-1]

    elif interleave == 'BSQ':
        data = np.fromfile(fname,
                           dtype=data_type,
                           count=(box[3]+length*(band-1))*width).reshape(-1, width)
        data = data[length*(band-1)+box[1]:length*(band-1)+box[3],
                    box[0]:box[2]]
    else:
        raise ValueError('unrecognized band interleaving:', interleave)

    # adjust output band for complex data
    if data_type.replace('>', '').startswith('c'):
        if   cpx_band.startswith('real'):  data = data.real
        elif cpx_band.startswith('imag'):  data = data.imag
        elif cpx_band.startswith('pha'):   data = np.angle(data)
        elif cpx_band.startswith('mag'):   data = np.absolute(data)
        elif cpx_band.startswith('c'):     pass
        else:  raise ValueError('unrecognized complex band:', cpx_band)

    # skipping/multilooking
    if xstep * ystep > 1:
        # output size if x/ystep > 1
        xsize = int((box[2] - box[0]) / xstep)
        ysize = int((box[3] - box[1]) / ystep)

        # sampling
        data = data[int(ystep/2)::ystep,
                    int(xstep/2)::xstep]
        data = data[:ysize, :xsize]

    return data



def rms(x, axis=None):
    return np.sqrt(np.mean(x**2, axis=axis))


if __name__ == '__main__':

    shape=(396,658)  ##gdalinfo Igrams/20090919_20091220_exp17/filt_20090919_20091220.int
    os.system('rm rms.txt')
    expDirs = sorted(glob.glob(os.path.join(os.path.abspath('Igrams_100-500/'), '20090919_20091220_exp*/filt_20090919_20091220.int')))
    
    n=1
    for iexp in expDirs:
        data=read_binary(iexp,shape,data_type='complex64',cpx_band='phase')
        rmss=rms(data)
        os.system("echo {} {} >> rms.txt".format(n,rmss))
        n+=1
