#!/bin/bash

cDir=`pwd`
for i in `grep "libXmu.so.6" intf/20*/*hpc*log | awk '{print $1}' | awk -F/ '{print $2}'`;do
#  if [[ -f "intf/$i/first_submission.log" ]]; then
#     cd intf/$i
#     log=`ls *hpc*log`
#     mv $log second_submission.log
#     cd $cDir
#     echo $i >> libXmu_error_first_submission_exist
#  fi

  if [[ ! -f "intf/$i/first_submission.log" ]]; then
     cd intf/$i
     log=`ls *hpc*log`
     rm $log
     cd $cDir
     echo $i >> libXmu_error_pairs_unprocessed
  fi
done 
