cd logs_intf
for i in `ls *_*.in`;do
    yyM=`echo $i | awk '{print substr($1,1,4)}'`
    doyM=`echo $i | awk '{print substr($1,5,3)}'`
    yyS=`echo $i | awk '{print substr($1,9,4)}'`
    doyS=`echo $i | awk '{print substr($1,13,3)}'`
    
    #count pairs less or greater than 1 year
    yearLap=`echo $yyS-$yyM | bc`
    yearDoy=`echo 365-$doyM+$doyS | bc`
    
    if [ "$yearLap" -eq "0" ]; then
       echo "cat $i >> intf.in_lt1y" | sh
    elif [ "$yearLap" -eq "1" ] && [ "$yearDoy" -lt "366" ]; then
       echo "cat $i >> intf.in_lt1y" | sh
    elif [ "$yearLap" -eq "1" ] && [ "$yearDoy" -gt "365" ]; then
       echo "cat $i >> intf.in_gt1y" | sh
    elif [ "$yearLap" -eq "2" ];then
       echo "cat $i >> intf.in_gt1y" | sh
    fi
done
mv intf.in_* ../
cd ../

