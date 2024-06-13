#!/bin/bash

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
