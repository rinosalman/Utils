cat intf_batch_finished.in | awk '{print $3}' | awk '{ print "cat logs_intf/"substr($1,11,18)}' | sh > data.in
