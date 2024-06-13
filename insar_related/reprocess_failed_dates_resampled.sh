#!/bin/bash

#resample to a common grid
#qsub -v sec_date=160521 pbs_1b.pbs

#for i in `cat pairs_undone`;do
#   qsub -v pair=$i pbs_2a.pbs
#done 


#geometrical offsets
#grep dates_resampled RectifyRangeOffsets.e* | awk '{print $5}' | awk -F/ '{print $2}' > geometrical_offsets_reprocess
#for i in `cat geometrical_offsets_reprocess`;do
#   qsub -v sec_date=$i pbs_1c.pbs
#done 
#qsub -v sec_date=160521 pbs_1c.pbs


#rectify range offsets
#for i in `cat geometrical_offsets_reprocess`;do
#   qsub -v date=$i pbs_2b.pbs
#done 
#qsub -v date=160521 pbs_2b.pbs

#ionospheric phase estimation
#qsub -v ionpair=160521-170114 pbs_3a.pbs
#for i in {150228-160521,150411-160521,160227-160521,160409-160521,160521-160702,160521-160730,160521-160910,160521-161022,160521-161203};do
#    qsub -v ionpair=$i pbs_3a.pbs
#done
