#!/bin/bash

# renaming file names
mkdir temp
cd temp
mv ../lower*int* .
mv ../lower*phsig* .
mv ../upper*int* .
mv ../upper*phsig* .

#lower
for i in `ls lower*`;do
    basename=`echo $i | awk -F. '{print $1}'`
    ext1=`echo $i | awk -F. '{print $2}'`
    ext2=`echo $i | awk -F. '{print $3}'`
    if [ -z "$ext2" ];then
       mv $i $basename".ori."$ext1
    else
       mv $i $basename".ori."$ext1"."$ext2
    fi
done

#upper
for i in `ls upper*`;do
    basename=`echo $i | awk -F. '{print $1}'`
    ext1=`echo $i | awk -F. '{print $2}'`
    ext2=`echo $i | awk -F. '{print $3}'`
    if [ -z "$ext2" ];then
       mv $i $basename".ori."$ext1
    else
       mv $i $basename".ori."$ext1"."$ext2
    fi
done

mv lower* ../
mv upper* ../
cd ../
rm -r temp

# masking the phase
inp='lower_80rlks_448alks.ori.int'
outlower='lower_80rlks_448alks.int'
imageMath.py -e='a*(b!=0)' --a=${inp} --b=flag.float -o ${outlower} -t cfloat
inp='upper_80rlks_448alks.ori.int'
outupper='upper_80rlks_448alks.int'
imageMath.py -e='a*(b!=0)' --a=${inp} --b=flag.float -o ${outupper} -t cfloat


# masking the phsig
inp='lower_80rlks_448alks.ori.phsig'
outlower='lower_80rlks_448alks.phsig'
imageMath.py -e='a*(b!=0);a*(b!=0)' --a=${inp} --b=flag.float -o ${outlower} -t float -s BIL
inp='upper_80rlks_448alks.ori.phsig'
outupper='upper_80rlks_448alks.phsig'
imageMath.py -e='a*(b!=0);a*(b!=0)' --a=${inp} --b=flag.float -o ${outupper} -t float -s BIL
