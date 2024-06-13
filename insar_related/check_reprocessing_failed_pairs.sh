cat intf_batch_failed.in | awk '{print $3}' | awk '{ print "ls intf/"substr($1,11,15)"/unwrap_ll.grd"}' | sh
