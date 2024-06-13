#!/bin/csh -f
#       $Id$
# RS, 07/03/2019


  if ($#argv != 2) then
    echo ""
    echo "Usage: create_merge_list.csh intf.in baseline_table.dat"
    echo ""
    echo "  outputs: "
    echo "    merge_list"
    echo ""
    exit 1
  endif

  set file = $1
  set table = $2
  set intf = "intf"
  rm merge_list
  
  foreach line (`awk '{print $0}' $1`) 
    set ref1 = `echo $line | awk -F: '{print $1}'`
    set rep1 = `echo $line | awk -F: '{print $2}'`
    set ref2 = `echo $line | awk -F: '{ print substr ($1,1,length($1)-2)"F2"}'`
    set rep2 = `echo $line | awk -F: '{ print substr ($2,1,length($2)-2)"F2"}'`
    set ref_id  = `grep $ref1 $table | awk '{printf("%d",int($2))}' `
    set rep_id  = `grep $rep1 $table | awk '{printf("%d",int($2))}' `
    echo "../F1/$intf/$ref_id"_"$rep_id"/:"$ref1".PRM:"$rep1".PRM",../F2/$intf/$ref_id"_"$rep_id"/:"$ref2".PRM:"$rep2".PRM" ">> merge_list
  end
