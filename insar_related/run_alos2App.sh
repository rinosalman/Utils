#!/bin/bash 
#
# check the number of arguments
#
# load isce
#module load anaconda2020/python3
#eval "$(/usr/local/anaconda3-2019/bin/conda shell.bash hook)"
#conda activate isce2
#source /home/data/INSAR_processing/isce_conda.sh


# Run alos2
path=$1
cd $path
echo "Run alos2App.py in here: $path"

pwd

alos2App.py --steps 

