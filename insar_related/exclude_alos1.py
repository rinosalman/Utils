#!/usr/bin/env python

'''
This code is used to exclude unwrap.png (with unwrapping errors noticed by manual inspection)
from intf.in
'''


import numpy as np
import re

def grab_yearDoy(scene):
    for line in open(scene):
       if "SC_clock_start" in line:
           temp=int(str(re.split(r'\n',line.split("=")[-1])[0]).split('.')[0])
    return temp



if __name__ == '__main__':
    
    inputFile=np.genfromtxt('intf.in',dtype='str')
    unwrappingError=np.genfromtxt('exclude_intfs',dtype='str')

    for i in range(len(inputFile)):
    	 print i
	 master1=inputFile[i][0:30]
	 slave1=inputFile[i][31::]

	 doymaster1=grab_yearDoy('raw/'+master1+'.PRM')
	 doyslave1=grab_yearDoy('raw/'+slave1+'.PRM')

	 for j in range(len(unwrappingError)):
	      doymaster2=unwrappingError[j][0:7]
	      doyslave2=unwrappingError[j][8:15]

	      if int(doymaster1) == int(doymaster2) and int(doyslave1) == int(doyslave2):
		  inputFile[i]='delete'
 	      else:
		  #intflist=np.append(intflist,'%s:%s'%(master1,slave1))
		  message='continue'


    print inputFile
    np.savetxt('intf.in2',inputFile,fmt='%s')
