"""

This is a test file for running the raintype module in your own code. 
If you run

>> python -W test.py

after installing the package and dependencies (see Readme file), then this file should run without problems (takes only a couple of seconds). The variable raintype will contain the classification. You can plot it if you want. 

If you don't include the -W, you'll get some benign warning messages.

"""

from uw_raintype import raintype
import netCDF4 as nc4
import numpy as np

#(A,B) = raintype.raintype('spolka.20111018_163032.nc','/local-scratch/raintype_install',-9999,1,20,40,28,43,46,7,5,10,8,50,2000)

refl_level = 5
refl_name = 'REFL'

fname = 'spolka.20111018_163032.nc'
fileDir = './'

ncid = nc4.Dataset(str(fileDir + fname),'r')

refl = np.array(np.squeeze(ncid.variables[refl_name][:,refl_level-1,:,:]))

(raintype,types) =  raintype.raintype(fname, fileDir, refl=refl, refl_missing_val=-9999, refl_dx=1, minZdiff=20,
                     deepcoszero=40, shallowconvmin=28, truncZconvthres=43, dBZformaxconvradius=46,
                     weakechothres=7, backgrndradius=5, maxConvRadius=10, minsize=8, startslope=50,
                     maxsize=2000)

