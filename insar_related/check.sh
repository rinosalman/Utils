# check for which pairs failed to be processed
file2check=phasefilt.grd

cp intf.in intf_failed.in
cp intf.in intf_finished.in
cd intf
for i in `ls -d *`;do
    intfpair=`cat ../logs_intf/$i.in`
    if [ -f $i/$file2check ]; then
        sed "/$intfpair/d" ../intf_failed.in > temp && mv temp ../intf_failed.in
    elif [ ! -f $i/$file2check ]; then
        sed "/$intfpair/d" ../intf_finished.in > temp && mv temp ../intf_finished.in
    fi   
done
cd ../
