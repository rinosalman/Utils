#!/bin/bash

cDir=`pwd`
#for i in `grep -v "#" outout.log`;do
for i in `grep -v "#" outout2.log`;do
  cd intf/$i
  qsub runCommand.pbs
  cd $cDir
done
