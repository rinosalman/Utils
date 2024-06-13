#!/bin/bash

# renaming file names
mkdir temp
cd temp
mv ../filt*int* .
mv ../*phsig* .

#int
for i in `ls filt*`;do
    basename=`echo $i | awk -F. '{print $1}'`
    ext1=`echo $i | awk -F. '{print $2}'`
    ext2=`echo $i | awk -F. '{print $3}'`
    if [ -z "$ext2" ];then
       mv $i $basename".ori."$ext1
    else
       mv $i $basename".ori."$ext1"."$ext2
    fi
done

#phsig
for i in `ls *phsig*`;do
    basename=`echo $i | awk -F. '{print $1}'`
    ext1=`echo $i | awk -F. '{print $2}'`
    ext2=`echo $i | awk -F. '{print $3}'`
    if [ -z "$ext2" ];then
       mv $i $basename".ori."$ext1
    else
       mv $i $basename".ori."$ext1"."$ext2
    fi
done

mv * ../
cd ../
rm -r temp

## masking the phase
#inp='filt_190712-190726_5rlks_28alks.ori.int'
#out='filt_190712-190726_5rlks_28alks.int'
#imageMath.py -e='a*(b!=0)' --a=${inp} --b=flag.float -o ${out} -t cfloat
#
## masking the phsig
#inp='190712-190726_5rlks_28alks.ori.phsig'
#out='190712-190726_5rlks_28alks.phsig'
#imageMath.py -e='a*(b!=0);a*(b!=0)' --a=${inp} --b=flag.float -o ${out} -t float -s BIL
