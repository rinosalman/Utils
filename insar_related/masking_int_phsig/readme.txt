1. run create_outppm.py 
2. open the .ppm file in gimp on your local laptop
3. draw areas to be masked as black
4. File->Export->give the name as *.data and export image as raw image(RGB standard and palette type normal)
5. copy the *.data to the folder where you run no.1
6. run flag.py, the input are *.data and width,length (the other output you run no.1)
7. modify pixels in .phsig and .int files to zero using imageMath.py
   imageMath.py -e='a*(b!=0)' --a=yourFilt.int --b=flag.float -o yourFiltOutput.int -t cfloat
   #here we have converted coherence or phsig to a two-band file. The two bands are the same.
   imageMath.py -e='a*(b!=0);a*(b!=0)' --a=yourPhsig.phsig --b=flag.float -o yourPhsigOutput.phsig -t float -s BIL
8. the snaphu to do the unwrapping
