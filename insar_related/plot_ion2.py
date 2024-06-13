#!/usr/bin/env python3

import os
import sys
import glob
import ntpath
import argparse



def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='take looks')
    parser.add_argument('-d', dest='dir', type=str, required=True,
            help = 'data directory')
    parser.add_argument('-s', dest='svg', type=str, required=True,
            help = 'output svg filename')
    parser.add_argument('-i', dest='img', type=int, default=1,
            help = 'create images. 0: no. 1: yes (default)')

    if len(sys.argv) <= 1:
        print('')
        parser.print_help()
        sys.exit(1)
    else:
        return parser.parse_args()


def runCmd(cmd, silent=0):
    import os

    if silent == 0:
        print("{}".format(cmd))
    status = os.system(cmd)
    if status != 0:
        raise Exception('error when running:\n{}\n'.format(cmd))


def getWidth(xmlfile):
    from xml.etree.ElementTree import ElementTree
    xmlfp = None
    try:
        xmlfp = open(xmlfile,'r')
        print('reading file width from: {0}'.format(xmlfile))
        xmlx = ElementTree(file=xmlfp).getroot()
        #width = int(xmlx.find("component[@name='coordinate1']/property[@name='size']/value").text)
        tmp = xmlx.find("component[@name='coordinate1']/property[@name='size']/value")
        if tmp == None:
            tmp = xmlx.find("component[@name='Coordinate1']/property[@name='size']/value")
        width = int(tmp.text)
        print("file width: {0}".format(width))
    except (IOError, OSError) as strerr:
        print("IOError: %s" % strerr)
        return []
    finally:
        if xmlfp is not None:
            xmlfp.close()
    return width


if __name__ == '__main__':

    #get inputs
    inps = cmdLineParse()

    #define header
    hdr = '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="20cm" height="20cm" version="1.1"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
'''
    tlr = '''
</svg>'''
    svg = hdr


    #images per line
    ipl = 12
    imgdir = 'intf_tiff'
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)
    #pairs = sorted(glob.glob( os.path.join(inps.dir) ))
    pairs = sorted(glob.glob(os.path.join(inps.dir, '20*')))
    npair = len(pairs)
    for i in range(npair):

        pair = pairs[i].split('/')[-1]
        if not os.path.isfile(os.path.join(imgdir, pair + '.tiff')):

            mdate = pair.split('_')[0][2:]
            sdate = pair.split('_')[1][2:]
            pairv2 = mdate+'-'+sdate

            interf = os.path.join(pairs[i], 'insar/diff_{}_5rlks_28alks.int'.format(pairv2))

            if not os.path.isfile(interf):
                continue
            else:
                interf_ml = os.path.join(imgdir, pair + '_5rlks_28alks.int')
                cmd = 'looks.py -i {} -o {} -r 3 -a 3'.format(interf, interf_ml)
                runCmd(cmd)
                width = getWidth(interf_ml + '.xml')

            if inps.img:
                cmd = 'mdx {} -s {} -c8pha -cmap cmy -wrap 6.283185307179586 -addr -3.141592653589793 -P -workdir {}'.format(interf_ml, width, imgdir)
                runCmd(cmd)

                cmd = 'convert {} -resize 100% {}'.format(
                    os.path.join(imgdir, 'out.ppm'),
                    os.path.join(imgdir, pair + '.tiff'))
                runCmd(cmd)
                os.remove(os.path.join(imgdir, 'out.ppm'))


            #line and column indexes, indexes start from 1
            ii = int((i + 1 - 0.1) / ipl) + 1
            jj = i + 1 - (ii - 1) * ipl

            img = '''    <image xlink:href="{}" x="{}cm" y="{}cm"/>
    <text x="{}cm" y="{}cm" fill="white" style="font-family:'Times New Roman';font-weight:normal;font-style:normal;font-stretch:normal;font-variant:normal;font-size:19px">{}</text>
'''.format(os.path.join(imgdir, pair + '.tiff'),
                0+(jj-1)*(5.503323251814445+0.2),
                0+(ii-1)*(4.815407845337639+0.2),
                0+(jj-1)*(5.503323251814445+0.2)+0.2,
                0+(ii-1)*(4.815407845337639+0.2)+4.615407845337639,
                mdate+'-'+sdate
            )   

            svg += img


    svg += tlr


    with open(inps.svg, 'w') as f:
        f.write(svg)
