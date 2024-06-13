#!/usr/bin/env python3
#Parallel processing in python

import sys, subprocess, os
import numpy as np
from multiprocessing import Pool


def runCommand(command, logging=True):
    """
    Use subprocess.call to run a command.
    Default assumes last argument is the log file, and removes it from the command (danger!).
    """
    print('running', command)
    if logging:
        #remove last argument and open it as log file
        logfile=command.split()[-1]
        cmd=' '.join(command.split()[0:-1])
        print('cdmddddd: %s'%cmd)
        with open(logfile,'w') as outFile:
            status=subprocess.call(cmd, shell=True, stdout=outFile, stderr=outFile)
    else:
        #no logging, just run command as-is
        status=subprocess.call(command, shell=True)
    if status != 0:
        print('Python encountered an error in the command:')
        print(command)
        print('error code:', status)
        sys.exit(1)



if __name__ == '__main__':


     # getting inputs
     intfDotIn = sys.argv[1]
     numproc = int(sys.argv[2])


     # create commands
     intfs = np.genfromtxt(intfDotIn,str,usecols=(0,1))
     commandList = []
     for i in range(len(intfs)):
         commandList = np.append(commandList,'/home/rino/scripts/insarscripts/run_alos2App.sh %s %s'%(intfs[i][0],intfs[i][1]))
   

     # submit to pool 
     with Pool(processes=numproc) as pool:
         pool.map(runCommand, commandList)
