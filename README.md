# raintype_python V1.0

Authors: Scott W. Powell and Stacy Brodzik, University of Washington
Date: May 2016
Email: spowell@atmos.uw.edu, brodzik@atmos.uw.edu
This is the rainfall type categorization (formerly known as convective/stratiform classification) of Powell et al. (2016, JTECH). It is an update to the Steiner et al. (1995) method of classifying convective and stratiform echoes of tropical and subtropical precipitation.

----------------------------------------------------------------

Setting up and using the code:

To install, run

>> python setup.py install --user

This will create a build directory, and the code can be accessed by including
          from uw_raintype import raintype
in your code. If you do this, you will need to input the appropriate user parameters when you call the function raintype. See raintype.py for the order of entering the parameters when calling this function.



Many users will probably wish to run the code directly from within uw_raintype. Inside uw_raintype, there are five .py files. Other than the ALGORITHM USER-INPUT PARAMETER section in runraintype.py, do not alter these files unless you know what you are doing. 

runraintype.py: This is the driver/wrapper code. This is the code that should be modified by the user. User input parameters are listed and described at the top of this code.

raintype.py: Called by runraintype and runs the algorithm.

rtfunctions.py: Contains a variety of functions for implementing algorithm.

algorithm.py: The rain-type classification algorithm.
 
netcdf_io.py: Deals with input and output of NetCDF data.

After the user input is tuned appropriately (see below), the code can be executed by entering

>> python -W ignore runraintype.py

The -W ignore flag suppresses warnings that will otherwise pop up because numpy is trying to compare NaNs to real numbers. Don't worry about these warnings when running the code. You'll want to suppress them so they don't keep displaying to the terminal and slowing down your code.

----------------------------------------------------------------

Tuning the user input:

Furthermore, and I cannot stress this enough, the values that are included as "default" in the code provided are probably not appropriate for your purposes. They need to be tuned based on the radar platform used, the beam width used, the convective regime sampled, etc. The "default" parameters in the code were appropriate for maritime tropical convection observed with an S-band (10 cm wavelength) radar with 0.91 deg beam width (S-PolKa during DYNAMO 2011 in the Central Eq. Indian Ocean).

The classification is *most* sensitive to the selection of the convective threshold, truncZconvthres. For radars with larger wavelengths (like C-band), or for radars using larger beam widths, the value of truncZconvthres will probably need to be reduced. I recommend keeping dBZformaxconvradius within 5 dBZ of truncZconvthres.

----------------------------------------------------------------

Output:

The output is in NetCDF format and is written on the same grid as the reflectivity data used as input. 
