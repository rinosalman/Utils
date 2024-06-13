cat intf.in | awk '{ print "gt intf/"substr($1,23,6)"_" substr($1,66,6)}'
