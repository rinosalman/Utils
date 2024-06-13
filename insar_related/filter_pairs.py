#!/usr/bin/env python3

import numpy as np
import datetime as dt
import glob,os

def date_to_nth_day(date, format='%Y%m%d'):
    date = datetime.datetime.strptime(date, format=format)
    new_year_day = datetime.datetime(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1

if __name__ == '__main__':

    #os.system('rm time_diff_exclude_pairs')
    #files=glob.glob('exclude_pairs')
    os.system('rm filtered_pairs excluded_pairs')
    files=glob.glob('pair')
    for i in range(len(files)):
        fil=files[i]
        dat=np.loadtxt(fil,str)
        listt=[]
        for j in range(len(dat)):
            
            # reference
            ref=dat[j].split('-')[0]
            year=int('20'+ref[0:2])
            month=int(ref[2:4])
            day=int(ref[4:6])
            doy=(dt.date(year, month, day) - dt.date(year,1,1)).days + 1
            doyy='%.2f'%(doy/365.25)
            yearDoyRef=year+float(doyy)

            # repeated
            rep=dat[j].split('-')[1]
            year=int('20'+rep[0:2])
            month=int(rep[2:4])
            day=int(rep[4:6])
            doy=(dt.date(year, month, day) - dt.date(year,1,1)).days + 1
            doyy='%.2f'%(doy/365.25)
            yearDoyRep=year+float(doyy)

            # calculate the difference
            diff=yearDoyRep-yearDoyRef
            if diff<1.2:
               os.system('echo %s >> filtered_pairs'%dat[j])
            if diff>=1.2:
               os.system('echo %s >> excluded_pairs'%dat[j])

            # save
            #os.system('echo %s %s %s %.2f >> time_diff_exclude_pairs'%(j,ref,rep,diff))
            #os.system('echo %s %s %s %.2f >> time_diff_worked_pairs'%(j,ref,rep,diff))



        #np.savetxt(fil+'.out',listt)
        #os.system('mv temp %s'%(fil+'.out'))
