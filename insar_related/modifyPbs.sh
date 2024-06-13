#!/bin/bash

#for i in `grep -v "#" error_phase_estimation_area_not_correct`;do
for i in `grep -v "#" error_phase_estimation_area_not_correct2`;do
   cDir=`pwd`
   cd intf/$i
   log=`ls *hpc*log`
   mv $log first_submission.log
   cd $cDir
done
