#!/bin/bash

for i in `grep -v "#" error_libXmu.xo.6`;do
   cDir=`pwd`
   cd intf/$i
   log=`ls *hpc*log`
   mv $log first_submission.log
   cd $cDir
done
