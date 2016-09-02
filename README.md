# raintype_python V1.0 (for Cartesian grids)

Authors: Scott W. Powell and Stacy Brodzik, University of Washington
Date: September 2016
Email: spowell@atmos.colostate.edu, brodzik@atmos.uw.edu
This is the rainfall type categorization (formerly known as convective/stratiform classification) of Powell et al. (2016, JTECH). It is an update to the Steiner et al. (1995) method of classifying convective and stratiform echoes of tropical and subtropical precipitation.

----------------------------------------------------------------

Setting up and using the code:

Before you do anything, you'll need to make sure that you have numpy, scipy, and netcdf4-python (plus dependencies) installed on your machine. netcdf4-python can be found, as of 2016, here: https://github.com/Unidata/netcdf4-python

To install, run

>> python setup.py install --user

The installation will create a build directory and copy the code to somewhere beneath your ~/.local directory. 

There is a test file and script in subdirectory "example" that you can use to ensure the installation went smoothly. Just go to that subdirectory and run 

>> python -W ignore test.py 

If it runs without errors, then it works! Running runraintype.py by going to the uw_raintype folder and entering 

>> python -W ignore runraintype.py

will do the same thing, and in addition, it will create an NetCDF output file of rain-type classifications for the example file.

Basic users (particularly those who just want to write out NetCDF output with the raintype classifications for a bunch of radar reflectivity data) will probably wish to simply run or copy the code directly from within the uw_raintype subdirectory where the code is downloaded. Inside the directory uw_raintype, there are five .py files. Other than the ALGORITHM USER-INPUT PARAMETER section in runraintype.py, do not alter these files unless you know what you are doing. 

Alternatively, the module that runs the algorithm can be accessed in a python script (or in something like ipython) by including (or entering)
          from uw_raintype import raintype
in your code. This could be useful for doing, for example, operational real-time classification. If you do this, you will need to input the appropriate user parameters when you call the function raintype. See raintype.py for the order of entering the parameters when calling this function, also detailed below.

----------------------------------------------------------------

Description of files:

runraintype.py: This is the driver/wrapper code. This is the code that should be modified by the user. User input parameters are listed and described at the top of this code. You will alter and run this code (only in the ALGORITHM USER-INPUT PARAMETER section) if you are not writing your own code that calls the module raintype. If you wish to import and call the module raintype in your own code (see above), you can make a call to raintype() with the appropriate user input parameters.

raintype.py: Called by runraintype and runs the algorithm. If you choose to import raintype (see above) in your own code and not execute runraintype, then your input parameters must be entered in the following order:

   (rtout,types) = raintype.raintype(fname, fileDir, refl, refl_missing_val=missing_value,
                                   refl_dx=dx, minZdiff=minZdiff, deepcoszero=deepcoszero,
                                  shallowconvmin=shallowconvmin,truncZconvthres=truncZconvthres,
                                   dBZformaxconvradius=dBZformaxconvradius,
                                   weakechothres=weakechothres, backgrndradius=backgrndradius,
                                   maxConvRadius=maxConvRadius,minsize=minsize,
                                   startslope=startslope, maxsize=maxsize

in which rtout is the actual classification and types is an object that contains information about what values in raintype correspond to what category. You will also have to read in reflectivity (refl) from fname in your code before calling raintype.

rtfunctions.py: Contains a variety of functions for implementing algorithm.

algorithm.py: The rain-type classification algorithm.
 
netcdf_io.py: Deals with input and output of NetCDF data.

For basic users, after the user input is tuned appropriately (see below), the code can be executed by entering

>> python -W ignore runraintype.py

The -W ignore flag suppresses warnings that will otherwise pop up because numpy is trying to compare NaNs to real numbers. Don't worry about these warnings when running the code. You'll want to suppress them so they don't keep displaying to the terminal and slowing down your code.

----------------------------------------------------------------

Tuning the user input:

Furthermore, and I cannot stress this enough, the values that are included as "default" in the code (specifically in runraintype.py) are probably not appropriate for your purposes. They need to be tuned based on the radar platform used, the beam width used, the convective regime sampled, etc. The "default" parameters in the code were appropriate for maritime tropical convection observed with an S-band (10 cm wavelength) radar with 0.91 deg beam width (S-PolKa during DYNAMO 2011 in the Central Eq. Indian Ocean).

The classification is *most* sensitive to the selection of the convective threshold, truncZconvthres. For radars with larger wavelengths (like C-band), or for radars using larger beam widths, the value of truncZconvthres will probably need to be reduced. I recommend keeping dBZformaxconvradius within 5 dBZ of truncZconvthres.

----------------------------------------------------------------

Output:

The output is in NetCDF format and is written on the same grid as the reflectivity data used as input.

Values are as follows:

0 = No Echo or Discarded Clutter Echo
1 = Stratiform
2 = Convective
3 = Mixed
4 = Isolated Convective Core
5 = Isolated Convective Fringe
6 = Weak Echo 

For analysis, ignore everything classified as "0" or "6"  unless you have a good reason for specifically examining weak echo. 

The "Mixed" category represents echoes surrounding convective cores (Classification 2). In the old convective/stratiform classification algorithm, these echoes were considered convective, but Powell et al. (2016) shows that the heating profile near convective echoes cannot be distinctively classified as either convective or stratiform based on the distance from a convective core. 

The two isolated convective categories largely contain shallow convective elements. In the old algorithm, convective cores of such elements were usually classified as convective, but the echo surrounding the cores was erroneously classified as stratiform. What Steiner et al. (1995) classified as stratiform is mostly now considered Isolated Convective Fringe (Classification 5). The echoes have composite heating profiles that are consistent with shallow/weak convective echoes, but the shape of droplets (based on ZDR profiles in such echoes) are more stratiform in nature, consistent with the idea that hydrometeors in such echoes consist primarily of "fallout" from nearby convection.

If trying to estimate rainfall in mixed echoes with a method that depends on convective/stratiform classification, it is probably best to use a Z-R (or Z-ZDR-R, etc.) relationship that has been derived for all (convective + stratiform) echoes. If you wish to express a conservative range of potential estimates, you may treat the mixed region as all convective in one estimate and all stratiform in another. It is recommended that Isolated Convective Fringe echoes be treated with a Z-R, etc. relationship derived from stratiform regions. Convective and Isolated Convective Core may be treated with convective Z-R, etc. relationships, and Stratiform echoes, obviously, with a stratiform relationship.

----------------------------------------------------------------

Known Issues: 

**It is not recommended that this algorithm be used if the user cares about the high-frequency variability (time-scales of approximately less than or equal to 1 day) of convection in their radar domain.** Between two temporally consecutive radar volumes, sometimes echo objects will "flip/flop" between being classified as Convective+Stratiform to being classified as Isolated Convective Core+Fringe. This happens because echoes are only considered "Isolated" if the echo object they reside in is less than maxsize (set to 2000 km by default). If echo objects vary in size around this threshold, their classifications may change back and forth between radar volumes. This is only a problem if you care about the high-frequency evolution of convection in your radar domain. A similar, but less obvious issue exists for echoes with reflectivity that are very near truncZconvthres; such echoes may "flip-flop" between Convective and Stratiform or Mixed classifications. The latter was an issue even in Steiner et al. (1995). 

The algorithm is run on data at an altitude of 2.5 km after interpolation to a 3D grid. If you need detail about echoes below this height (particularly if you want to identify the most shallow precipitating elements), you should consider using the polar-coordinate version of this algorithm.
