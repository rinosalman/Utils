#!/usr/bin/perl
### grd2dem.pl
#use lib "/Users/insar/insarscripts/roipac/Geo-Distance-0.20/lib";
use lib "/home/rino/scripts/insarscripts/Geo-Distance-0.20/lib";
use Geo::Distance;

###Usage info/check
sub Usage{
  print STDERR <<END;

Usage: grd2dem.pl name
grdfile is name.grd

Function: Creates name.dem from name.grd
Routines called: 

***Rowena Lohman, Mar 9, 1998***
***Brian Savage Mar 25, 2002***
END
    exit 1;
}


@ARGV == 1 or Usage();
$name = shift;
$grd  = "$name.grd";
$dem  = "$name.dem";
$dir  = `pwd`;

#################
print "Reading grdfile\n";
#################
@output = split /\n/, `gmt grdinfo $grd`;
@xinfo  = split /\s+/, @output[5];
@yinfo  = split /\s+/, @output[6];
@info   = split /\s+/, @output[8];

for ($i=0; $foundx != 4; $i++){
  if ($xinfo[$i] eq "x_min:"){
    $x_min = $xinfo[$i+1];
    $foundx ++;
  }
  if ($xinfo[$i] eq "x_max:"){
    $x_max = $xinfo[$i+1];
    $foundx ++;
  }
  #if ($xinfo[$i] eq "n_columns:"){
  if ($xinfo[$i] eq "n_columns:"){
    $width = $xinfo[$i+1];
    $foundx ++;
  }
  if ($xinfo[$i] eq "x_inc:"){
    $inc = $xinfo[$i+1];
    $foundx ++;
  }
  if ( $i > scalar @xinfo){
    print "Error: x info not found.\n";
    print $xinfo[1], "\n";
    exit 1;
  }
}

for ($i=0; $foundy != 3; $i++){
  if ($yinfo[$i] eq "y_min:"){
    $y_min = $yinfo[$i+1];
    $foundy ++;
  }
  if ($yinfo[$i] eq "y_max:"){
    $y_max = $yinfo[$i+1];
    $foundy ++;
  }
  #if ($yinfo[$i] eq "n_rows:"){
  if ($yinfo[$i] eq "n_rows:"){
    $length = $yinfo[$i+1];
    $foundy ++;
  }
  if ( $i > scalar @yinfo){
    print "Error: y info not found.\n";
    print @yinfo, "\n";
    exit 1;
  }
}

$offset = $info[4];
$scale  = $info[2];

$num1=$width-1;
$num2=$length-1;

$lon_central = ($x_min + $x_max)/2;
$lat_central = ($y_min + $y_max)/2;

my $geo = new Geo::Distance;
$x_dist = $geo->distance( 'meter', $x_min,$lat_central => $x_max,$lat_central );
$y_dist = $geo->distance( 'meter', $lon_central,$y_min => $lon_central,$y_max );
$az_pxlsz = int($y_dist/$length);
$rg_pxlsz = int($x_dist/$width);
print "az_pxlsz = $az_pxlsz\n";
print "rg_pxlsz = $rg_pxlsz\n";

#################
print "Writing $dem.rsc\n";
#################
open(RSC, ">$dem.rsc") or die "Error opening $dem.rsc";

print RSC "FILE_DIR      $dir";
print RSC "WIDTH         $width\n";
print RSC "FILE_LENGTH   $length\n";
print RSC "XMIN          0\n";
print RSC "XMAX          $num1\n";
print RSC "YMIN          0\n";
print RSC "YMAX          $num2\n";
print RSC "X_FIRST       $x_min\n";
print RSC "Y_FIRST       $y_max\n";
print RSC "X_STEP        $inc\n";
print RSC "Y_STEP        -$inc\n";
print RSC "X_UNIT        degrees\n";
print RSC "Y_UNIT        degrees\n";
print RSC "Z_OFFSET      $offset\n";
print RSC "Z_SCALE       $scale\n";
print RSC "PROJECTION    lat/lon\n";
print RSC "LAT_REF1      $y_max\n";
print RSC "LON_REF1      $x_min\n";
print RSC "LAT_REF2      $y_min\n";
print RSC "LON_REF2      $x_max\n";
print RSC "LAT_REF3      $y_max\n";
print RSC "LON_REF3      $x_min\n";
print RSC "LAT_REF4      $y_min\n";
print RSC "LON_REF4      $x_max\n";
print RSC "AZIMUTH_PIXEL_SIZE  $az_pxlsz\n"; 
print RSC "RANGE_PIXEL_SIZE    $rg_pxlsz\n"; 

close(RSC);
#The .00833333 is for 90m pixels

#`grd2xyz $grd -Z -b > junk.r4`;
`gmt grd2xyz $grd -ZTLh > junk.i2`;
#`$INT_BIN/r4dem_i2dem junk.r4 $width $length junk.i2`;
`mv junk.i2 $dem`;
#`rm junk.r4`;
exit 0;

