#!/bin/bash

##run_01_crop
#for i in {1..15};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_01_crop | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

##run_02_reference
cp cmd cmd_1.pbs
cat run_files/run_02_reference >> cmd_1.pbs
qsub cmd_1.pbs

#run_03_focus_split 
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_03_focus_split | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_04_geo2rdr_coarseResamp
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_04_geo2rdr_coarseResamp | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_05_refineSecondaryTiming
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_05_refineSecondaryTiming | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_06_invertMisreg
#cp cmd cmd_1.pbs
#cat run_files/run_06_invertMisreg >> cmd_1.pbs
#qsub cmd_1.pbs

#run_07a_fineResamp
#cp cmd cmd_7a
#cat run_files/run_07_fineResamp | awk 'NR==1{print $0}' >> cmd_7a
#qsub cmd_7a

#run_07b_fineResamp
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    grep -v "#" run_files/run_07_fineResamp | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_08_denseOffset
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_08_denseOffset | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_09_invertDenseOffsets
#cp cmd cmd_1.pbs
#cat run_files/run_09_invertDenseOffsets >> cmd_1.pbs
#qsub cmd_1.pbs

#run_10_resampleOffset 
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_10_resampleOffset | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_11_replaceOffsets
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_11_replaceOffsets | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_12a_fineResamp
#cp cmd cmd_12a
#cat run_files/run_12_fineResamp | awk 'NR==1{print $0}' >> cmd_12a
#qsub cmd_12a

#run_12b_fineResamp
#for i in {1..14};do
#    cp cmd cmd_$i".pbs"
#    grep -v "#" run_files/run_12_fineResamp | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_13_grid_baseline
#for i in {1..15};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_13_grid_baseline | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_14_igram
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_14_igram | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_15_igramLowBand
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_15_igramLowBand | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_16_igramHighBand
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_16_igramHighBand | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done

#run_17_iono
#for i in {1..100};do
#    cp cmd cmd_$i".pbs"
#    cat run_files/run_17_iono | awk -v nn=$i 'NR==nn{print $0}' >> cmd_$i".pbs"
#    qsub cmd_$i".pbs"
#done
