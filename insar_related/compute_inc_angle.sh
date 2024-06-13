#!/bin/bash

e=look_e.grd
n=look_n.grd
u=look_u.grd

grdmath $u $e 2 POW $n 2 POW ADD SQRT DIV ATAN R2D = incAngle.grd
