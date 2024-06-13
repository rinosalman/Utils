#!/bin/bash


# check finished processing folder
ls intf/20*/insar/*unw.geo | awk -F/ '{print $1"/"$2}' > processing_folder_done

# check all available folder
ls -d intf/20* > processing_folder_all

# isolate unfinished folder
diff processing_folder_all processing_folder_done | grep "<" | cut -c 3- > processing_folder_failed
