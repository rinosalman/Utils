# to cm
gmt grdmath geo_velocity.grd 100 MUL = geo_velocity_cm.grd
gmt grdmath geo_velocity_ITRF14.grd 100 MUL = geo_velocity_ITRF14_cm.grd
gmt grdmath geo_velocity_ITRF14_vertical.grd 100 MUL = geo_velocity_ITRF14_vertical_cm.grd

# masking
gmt grdmath geo_maskTempCoh.grd 0.7 GE = temp.grd
gmt grdmath temp.grd 0 NAN = tempNaN.grd
gmt grdmath geo_velocity_cm.grd tempNaN.grd MUL = geo_velocity_cm_masked.grd
gmt grdmath geo_velocity_ITRF14_cm.grd tempNaN.grd MUL = geo_velocity_ITRF14_cm_masked.grd
gmt grdmath geo_velocity_ITRF14_vertical_cm.grd tempNaN.grd MUL = geo_velocity_ITRF14_vertical_cm_masked.grd
