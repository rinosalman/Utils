#!/bin/bash


# finished pairs
ls -d pairs_ion/*/ion | awk -F/ '{print $2}' > pairs_done

# all available pairs
ls -d pairs/* | awk -F/ '{print $2}' > pairs_all

# filter unfinished pairs
diff pairs_all pairs_done | grep "<" | cut -c 3- > pairs_undone_pbs3a
