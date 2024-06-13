#!/usr/bin/env python
# python script to view baselines of interferograms finished unwrapping, and create a new list of ones left to do

import os.path
import numpy as np
import matplotlib.pyplot as plt
import time
import shutil
#import argparse
#import itertools

# get command line arguments, eg.  make_ifg_list.py -t 300  (makes all intfs with a b_perp less than 300m)

#parser = argparse.ArgumentParser(description='View baseline plot of intfs finished unwrapping, and  create a new GMTSAR-readable intf.in list from those unfinished')
#parser.add_argument('track',type=str,help='track directory name')
#parser.add_argument('-n','--nlimit',type=int,help='maximum number of interferograms to return (default:all)')
#parser.add_argument('-b','--baselinethreshold',type=int,help='maximum perpendicular baseline of interferograms to return (default:all)')
#parser.add_argument('-t','--timethreshold',type=int,help='maximum temporal baseline of interferograms to return (default:all)')
#parser.add_argument('-s','--scale',type=float,default=1.0,help='scaling ratio between temporal/spatial baselines in weeding to meet maximum number requirement (default: 1 day/meter)')
#parser.add_argument('-m','--min',type=int,default=2,help='minimum number of interferograms to make per date (default: 2)')
#args = parser.parse_args()

#track='t306'
track='F2'


# load baseline table
fname=track + '/raw/baseline_table.dat'
#fname=track + '/raw/baseline_table.dat_editted'
if os.path.isfile(fname):
    table=np.loadtxt(fname,usecols=(0,1,2,4),dtype={'names': ('orbit','yearday','day','bperp'), 'formats': ('S5','f16', 'f4', 'f16')})
else:
    print('did not find baseline table!')
    exit()


# load corresponding data.in
#fname=track + '/raw/data.inthebest'
fname=track + '/raw/data.in'
if os.path.isfile(fname):
    dat=np.loadtxt(fname,dtype={'names': ('stem',),'formats': ('S21',)})
else:
    print('did not find data.in!')
    exit()

#load intf.in
fname=track + '/intf.in'
if os.path.isfile(fname):
    intf_in=np.loadtxt(fname,delimiter=':',dtype={'names': ('stem1','stem2'),'formats': ('S21','S21')})
else:
    print('did not find intf.in!')
    exit()

# create lists from data.in
names=[]
stems=[]
days=[]
years=[]
baselines=[]
dirstems=[]
sardict={}
idd=[]
for i in range(len(table)):
    idd.append('%.0f'%np.floor((table[i][1])))
    names.append(table[i][0])
    days.append(table[i][2])
    years.append(table[i][2]/365+2014.5)
    baselines.append(table[i][3])
    stems.append(dat[i][0])
    dirstems.append( '%.0f' % np.floor(table[i][1]) )
    #alternate method using a dictionary: key=stem, values=[orbitnum,integer day,decimal year,baseline,dirstem]
    sardict[dat[i][0]]=[ table[i][0], table[i][2], table[i][2]/365+2014.5, table[i][3], '%.0f' % np.floor(table[i][1]) ]

fig=plt.plot()

ax=plt.subplot(111)
ax.plot(years,baselines,'r.')

# iterate over intf.in
for ifg in intf_in:
    ifg_dir = sardict[ifg[0]][4] + '_' + sardict[ifg[1]][4]
    unwfile=track + '/intf/' + ifg_dir + '/unwrap.grd'
    # plot if finished 
    if os.path.isfile(unwfile):
        ax.plot([sardict[ifg[0]][2],sardict[ifg[1]][2]],[sardict[ifg[0]][3],sardict[ifg[1]][3]],'b')
        print(ifg_dir + 'finished')
    else:
        #ax.plot([sardict[ifg[0]][2],sardict[ifg[1]][2]],[sardict[ifg[0]][3],sardict[ifg[1]][3]],'r')
        print(ifg_dir + 'not finished')

plt.show()
plt.savefig(track+'/figure1.png')
exit()


# create a list of all possible combinations of interferograms (that meet the threshold criterion),
# and compute their weights
intflist=[]
weights=[]
it=itertools.combinations(range(len(stems)),2)
for el in it:
    if (np.abs(baselines[el[0]] - baselines[el[1]]) < baselinethreshold) and (np.abs(days[el[0]] - days[el[1]]) < timethreshold):
        intflist.append(el)
        weights.append(np.sqrt((days[el[0]]-days[el[1]])**2/scale + (baselines[el[0]]-baselines[el[1]])**2))

print('found %d possible igrams' %len(intflist))

# optionally, weed interferograms by removing the worst one iteratively
if nlimit:
    while len(intflist) > nlimit:
        #sort igrams by weight
        #for each bad igram in order, check whether each scene appears in the overall list enough times
        imax=weights.index(max(weights))
        weights.pop(imax)
        intflist.pop(imax)

intf_fname=track + '/intf.in'
# make a backup copy of intf.in if it exists
if os.path.isfile(intf_fname):
    backup_fname=track + '/intf.in.bak.' + time.strftime("%m_%d_%Y-%H_%M_%S")
    shutil.copy2(intf_fname,backup_fname)

# open intf.in for writing
f = open(intf_fname,'w')

fig=plt.plot()

ax=plt.subplot(111)
ax.plot(years,baselines,'b.')
for i in range(len(intflist)):
    #write 'stem:stem' to file track/intf.in
    stemstem='%s:%s\n'%(stems[intflist[i][0]],stems[intflist[i][1]])
    f.write(stemstem)
    #plot ifg
    ax.plot([years[intflist[i][0]],years[intflist[i][1]]],[baselines[intflist[i][0]],baselines[intflist[i][1]]],'b')

#close file
f.close()
#draw figure
plt.show()

#save figure
plt.savefig('figure2.png')

## END ##
