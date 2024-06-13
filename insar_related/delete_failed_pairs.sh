for i in `cat intf_batch_failed.in | awk '{print $3}' | awk '{ print substr($1,11,15)}'`;do
    echo "Delete $i"
    rm -r intf/$i &
done
