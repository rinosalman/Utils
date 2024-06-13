#!/bin/bash

for i in {1..170};do
   jobn=`cat jobs.txt | awk -v jn=$i 'NR==jn{print $0}'`
   echo $jobn
   qdel $jobn
done
