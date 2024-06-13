#!/bin/csh

# Do tropospheric correction based on GACOS
# 18 March 2020, Rino Salman

#GMT defaults
gmt gmtset FONT_LABEL 15
gmt gmtset FONT_TITLE 15
gmt gmtset FONT_ANNOT_PRIMARY 96
gmt gmtset MAP_FRAME_WIDTH 0.1c
gmt gmtset MAP_FRAME_PEN 1.076p
gmt gmtset FONT_LABEL Helvetica
gmt gmtset MAP_ORIGIN_X 1i
gmt gmtset MAP_ORIGIN_Y 1i
gmt gmtset MAP_FRAME_TYPE plain
gmt gmtset MAP_TICK_LENGTH_PRIMARY 0.1c
gmt gmtset MAP_TICK_LENGTH_SECONDARY 0.1c
gmt gmtset MAP_ANNOT_OFFSET_PRIMARY 0.1i
gmt gmtset MAP_TITLE_OFFSET 0.1i
gmt gmtset FORMAT_GEO_MAP D
gmt gmtset PS_MEDIA A4

set GACOS_folder = ../../gacos
set cDir = `pwd`
set ref_lon = 107.493906
set ref_lat = -7.104391
set los = los_ll.grd
set los_ref = los_ll_ref.grd
set los_gacos_corrected = los_ll_gacos_corrected.grd
set gacos_intf = gacos_intf.grd
set gacos_intf_cut = gacos_intf_cut.grd
set gacos_intf_cut_ref = gacos_intf_cut_ref.grd
set proj = -JM10c
set clip = clip_437_7040.kml.gmt
set make_los_products = /home/share/insarscripts2/automate/make_los_products.csh
set sat = ALOS
set phase = phasefilt_mask_ll.grd

#foreach line (`awk '{print $1}' intf.in_2007215_2007261`)
foreach line (`awk '{print $1}' intf.in`)

    #IDs
    set ref = `echo $line | awk -F: '{print $1}'`
    set rep = `echo $line | awk -F: '{print $2}'`
    set ref_id  = `grep SC_clock_start ./raw/$ref.PRM | awk '{printf("%d",int($3))}' `
    set rep_id  = `grep SC_clock_start ./raw/$rep.PRM | awk '{printf("%d",int($3))}' `
    set mas_ztd  = `grep date ./raw/$ref.PRM | awk '{print "20"$3}' `
    set slv_ztd  = `grep date ./raw/$rep.PRM | awk '{print "20"$3}' `
    set msdate = $mas_ztd"_"$slv_ztd
    set mztd = $mas_ztd".ztd"
    set sztd = $slv_ztd".ztd"
    set mztdgrd = $mas_ztd".ztd.grd"
    set sztdgrd = $slv_ztd".ztd.grd"
    set folder = $ref_id"_"$rep_id
    set psFile = "gacos_correction_"$folder".ps"
    set psFile2 = "gacos_correction_intf_"$folder".ps"

    #convert *.ztd to .grd format
    cd intf/$folder
    set inc = `grdinfo $los -I`
    set reg = `grdinfo $los -I-`
    set titleloc = `gmt grdinfo $los -C | awk '{print ($2+$3)/2,$5+0.13}'`
    set j = 1
    while ($j < 3)
       if ($j == 1) then
          set ztd = $mztd
          set ztdgrd = $mztdgrd
       else
          set ztd = $sztd
          set ztdgrd = $sztdgrd
       endif
       set M_LON_MIN = `cat $cDir/$GACOS_folder/$ztd.rsc | grep X_FIRST | awk '{print $2}'`
       set M_LAT_MAX = `cat $cDir/$GACOS_folder/$ztd.rsc | grep Y_FIRST | awk '{print $2}'`
       set M_WIDTH = `cat $cDir/$GACOS_folder/$ztd.rsc | grep WIDTH | awk '{print $2}'`
       set M_LENGTH = `cat $cDir/$GACOS_folder/$ztd.rsc | grep FILE_LENGTH | awk '{print $2}'`
       set M_X_STEP = `cat $cDir/$GACOS_folder/$ztd.rsc | grep X_STEP | awk '{print $2}'`
       set M_Y_STEP = `cat $cDir/$GACOS_folder/$ztd.rsc | grep X_STEP | awk '{print $2}'`
       gmt xyz2grd $cDir/$GACOS_folder/$ztd -G$cDir/$GACOS_folder/$ztdgrd -RLT$M_LON_MIN/$M_LAT_MAX/$M_WIDTH/$M_LENGTH -I$M_X_STEP/$M_Y_STEP -di0 -ZTLf
    @ j++ 
    end

    #time differencing for ztd and convert from m to mm (because los_ll.grd is in mm)
    #gacos interferogram = master-slave
    gmt grdmath $cDir/$GACOS_folder/$mztdgrd $cDir/$GACOS_folder/$sztdgrd SUB 1000 MUL = temp.grd

    #sample the gacos intergerogram to the interferogram region
    gmt grdsample temp.grd $reg $inc -G$gacos_intf_cut -T

    #compute look_u
    set prm = `ls *PRM | head -1`
    $make_los_products $los $prm $sat 
   
    #convert cutted gacos interferogram from zenith direction to InSAR LOS
    gmt grdmath $gacos_intf_cut look_u.grd DIV = $gacos_intf

    #space differencing, set reference point
    echo $ref_lon $ref_lat > ref_lonlat.txt
    set pval = `gmt grdtrack ref_lonlat.txt -G$los -Z -T1000m`
    gmt grdmath $los $pval SUB = $los_ref
    set dval = `gmt grdtrack ref_lonlat.txt -G$gacos_intf -Z -T1000m`
    #gmt grdmath $gacos_intf $dval SUB = $gacos_intf_cut_ref
    gmt grdmath $gacos_intf $dval ADD = $gacos_intf_cut_ref

    #make correction
    #corrected los = los-gacos
    gmt grdmath $los_ref $gacos_intf_cut_ref SUB = $los_gacos_corrected

    #plot the results without interferogram
    #los_ll
    set tmp = `gmt grdinfo -C -L2 $los_ref`
    set caxmin = `echo $tmp | awk '{printf("%5.2f",$12-2*$13)}'`
    set caxmax = `echo $tmp | awk '{printf("%5.2f",$12+2*$13)}'`
    gmt grdgradient $los_ref -Nt.9 -A0. -Gtmp_grad_los.grd
    gmt makecpt -Cpolar -Z -T$caxmin/$caxmax/0.05 -D > temp.cpt
    gmt pscoast $reg $proj -K -X1.2i -Yc -Df -Wthin -Bxa.25f.125 -Byaf -BwSne -Sazure -Gdarkgray > $psFile
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile
    gmt grdimage $los_ref -J -R -Itmp_grad_los.grd -Ctemp.cpt -Bxa.25f.125 -Bya.25f.125 -BWSne+t"Original los" -O -K > $psFile
    gmt psclip -R -J -K -O -C >> $psFile

    #gacos interferogram
    gmt grdgradient $gacos_intf_cut_ref -Nt.9 -A0. -Gtmp_grad_gacos.grd
    gmt pscoast -R -J -K -O -X4.5i -Df -Wthin -Bxa.25f.125 -Byaf -BwSne -Sazure -Gdarkgray >> $psFile
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile
    gmt grdimage $gacos_intf_cut_ref -R -J -Itmp_grad_gacos.grd -Ctemp.cpt -Bxa.25f.125 -Byaf -BwSne+t"GACOS correction" -K -O >> $psFile
    gmt psclip -R -J -K -O -C >> $psFile

    #corrected los
    gmt grdgradient $los_gacos_corrected -Nt.9 -A0. -Gtmp_grad_corrected_los.grd
    gmt pscoast -J -R -K -O -X4.5i -Df -Wthin -Bxa.25f.125 -Byaf -BwSne -Sazure -Gdarkgray >> $psFile
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile
    gmt grdimage $los_gacos_corrected -R -J -Itmp_grad_corrected_los.grd -Ctemp.cpt -Bxa.25f.125 -Byaf -BwSne+t"Corrected los" -O -K >> $psFile
    gmt psclip -R -J -K -O -C >> $psFile
    gmt psscale -R -J -D-4.04i/-0.68i+w3i/0.12i+h+e -Ctemp.cpt -Baf+l"(mm)" -K -O >> $psFile

    #plot the results with interferogram
    #interferograms
    gmt pscoast $reg $proj -K -X1.9i -Y5.94i -Df -Wthin -Bxa.25f.125 -Bya.25f.125 -BWSne -Sazure -Gdarkgray > $psFile2
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile2
    gmt grdimage $phase -R -J -Cphase.cpt -Bxa.25f.125 -Bya.25f.125 -BWSne+t"Phasefilt ($folder/$msdate)" -O -K >> $psFile2
    gmt psclip -R -J -K -O -C >> $psFile2
    gmt pscoast -R -J -K -Df -Wthin -Sazure -O >> $psFile2
    echo $titleloc | awk '{print $1,$2,"Interferogram"}' | gmt pstext -J -R -K -O -N -F+f13,Helvetica >> $psFile2
    set intf_date = `echo "$titleloc $folder $msdate"`
    echo $intf_date | awk '{print $1,($2-0.06),$3"/"$4}' | gmt pstext -J -R -K -O -N -F+f13,Helvetica >> $psFile2

    #los_ll
    gmt pscoast -R -J -K -O -Y-5.2i -Df -Wthin -Bxa.25f.125 -Bya.25f.125 -BWSne -Sazure -Gdarkgray >> $psFile2
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile2
    gmt grdimage $los_ref -J -R -Itmp_grad_los.grd -Ctemp.cpt -Bxa.25f.125 -Bya.25f.125 -BWSne+t"Original los" -K -O >> $psFile2
    gmt psclip -R -J -K -O -C >> $psFile2
    gmt psbasemap -R -J -K -O -BWSne+t"Original los" >> $psFile
    gmt pscoast -R -J -K -Df -Wthin -Sazure -O >> $psFile2
    echo $titleloc | awk '{print $1,($2-0.05),"Original LOS"}' | gmt pstext -J -R -K -O -N -F+f13,Helvetica >> $psFile2

    #gacos interferogram
    gmt pscoast -R -J -K -O -X4.5i -Df -Wthin -Bxa.25f.125 -Byaf -BwSne -Sazure -Gdarkgray >> $psFile2
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile2
    gmt grdimage $gacos_intf_cut_ref -R -J -Itmp_grad_gacos.grd -Ctemp.cpt -Bxa.25f.125 -Byaf -BwSne+t"GACOS correction" -K -O >> $psFile2
    gmt psclip -R -J -K -O -C >> $psFile2
    gmt pscoast -R -J -K -Df -Wthin -Sazure -O >> $psFile2
    echo $titleloc | awk '{print $1,($2-0.05),"GACOS delay"}' | gmt pstext -J -R -K -O -N -F+f13,Helvetica >> $psFile2

    #corrected los
    gmt pscoast -R -J -K -O -X4.5i -Df -Wthin -Bxa.25f.125 -Byaf -BwSne -Sazure -Gdarkgray >> $psFile2
    cat $cDir/$clip | gmt psclip -R -J -K -O >> $psFile2
    gmt grdimage $los_gacos_corrected -J -R -Itmp_grad_corrected_los.grd -Ctemp.cpt -Bxa.25f.125 -Byaf -BwSne+t"Corrected los" -O -K >> $psFile2
    gmt psclip -R -J -K -O -C >> $psFile2
    gmt pscoast -R -J -K -Df -Wthin -Sazure -O >> $psFile2
    echo $titleloc | awk '{print $1,($2-0.05),"Corrected LOS"}' | gmt pstext -J -R -K -O -N -F+f13,Helvetica >> $psFile2
    gmt psscale -R -J -D+4.34i/+0.38i+w3i/0.14i+e -Ctemp.cpt -Baf+l"(mm)" -K -O >> $psFile2


    rm -f temp.grd tmp_grad_los.grd tmp_grd_gacos.grd tmp_grd_corrected_los.grd temp.cpt
    cd $cDir

end

