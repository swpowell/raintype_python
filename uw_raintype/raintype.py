"""
Rain-type Classification code of Powell et al. (2016, JTECH)
Author: Scott Powell and Stacy Brodzik, University of Washington
Date: April 11, 2016

Amendments by
Stacy Brodzik (brodzik@uw.edu)
rev 3 5/2/2016 - added missing value mask to match input reflectivity file

""" 

from __future__ import division  #For python2 only. Alternatively, run interpreter with -Q flag. 
import numpy as np
import os
from uw_raintype import algorithm as alg
from uw_raintype import rtfunctions as rtf
from uw_raintype import netcdf_io as net
import logging as log

def raintype(fname, fileDir, refl=None, refl_missing_val=-9999, refl_dx=1, minZdiff=20, 
             deepcoszero=40, shallowconvmin=28, truncZconvthres=43, dBZformaxconvradius=46, 
             weakechothres=7, backgrndradius=5, maxConvRadius=10, minsize=8, startslope=50, 
             maxsize=2000):
    #Values above are default values for S-band over tropical marine region. Code will use 
    #what is designated in runraintype.py first and will use these only if no value(s) is/are given.

  """
  Description: This is the driver code for the updated version of Steiner et al. (1995)
  convective/stratiform classification code for use with Cartesian gridded datasets. Adds new
  categories for echoes of uncertain rain-type near convective cores and correctly identifies
  isolated, often shallow, convection as convective instead of stratiform. For details, see
  Powell, S.W., R.A. Houze, JR., and S.R. Brodzik, 2016: Rainfall-type categorization of radar
  echoes using polar coordinate reflectivity data, J. Atmos. Oceanic Technol., 17, 523-538 
  (http://www.atmos.washington.edu/MG/PDFs/JTECH16_Powell-etal_RainCat.pdf).

  The variables listed in the left column immediately below are those in the user-input
  parameters farther below. The variables listed in the right column below are the
  corresponding variable names in Table 1 of Powell et al. (2016).

  Variable name in this code          Variable name in Powell et al.
  --------------------------          ------------------------------
  minZdiff                            a
  deepcoszero                         b
  shallowconvmin                      Z_shallow
  truncZconvthres                     Z_th
  dBZformaxconvradius                 Z_conv
  weakechothres                       Z_weak
  backgrndradius                      R_bg
  maxconvRadius                       R_conv
  minsize                             A_low
  startslope                          A_med
  maxsize                             A_high

  Inputs:
  refl = Reflectivity
  refl_missing_val = missing value in reflectivity data
  refl_dx (km) = horizontal spacing of grid
  minZdiff = factor for comparing echo to background reflectivity; see equation (1) in journal 
     article referenced above
  deepcoszero = see equation (1) in journal article referenced above
  shallowconvmin = minimum dBZ for classification as convective for objects with area less than 
     startslope
  truncZconvthres = reflectivity threshold at or above which echos are classified as convective;  
     The value in Powell et al. (2016) was used for an S-band radar with a beam width of 0.91 degrees. 
     For C-band and/or larger beam width, this value will probably need to be decreased.  Rain
     type classification is most sensitive to this input.
  dBZformaxconvradius = minimum dBZ required for max_conv_radius to apply; should be somewhere close 
     to truncZconvthres
  weakechothres = minimum dBZ for classification as not weak echo; don't change this without a good 
     reason.  7 is about as low as we can go without getting into Bragg scatter territory.
  backgrndradius (km) = radius within which background reflectivity is computed
  maxConvRadius (km) = maximum radius around convective core for possible uncertain classification; 
     Powell et al. (2016) tested 5, and showed that too much convection was included 
     in stratiform region.  Don't lower this number without a good reason.
  minsize (km^2) = minimum areal coverage a contiguous echo can cover and still receive an ISO_CONV
     classification (See dBZcluster for use)
  startslope (km^2) = any contiguous echo object with areal coverage greater than this but less than 
     maxsize gets a new convective threshold that is linearly interpolated between shallowconvmin and 
     truncZconvthres depending on where between startslope and maxsize its area is (See makedBZcluster)
  maxsize (km^2) = any contiguous echo object greater than this size gets a convective threshold of 
     truncZconvthres (See makedBZcluster)

  Outputs:
  rain_type = rain type classification
  types = dict of rain types and their values
  
  """
  
  global bgmask
  global maskcell

  ## *****************  BEGIN OUTPUT CONSTANTS *****************
  
  # Output constants: Do not change these without a good reason!
  types = {'NO_SFC_ECHO':0,'STRATIFORM':1,'CONVECTIVE':2,'UNCERTAIN':3,'ISO_CONV_CORE':4,
           'ISO_CONV_FRINGE':5,'WEAK_ECHO':6,'CS_CORE':8,'ISO_CS_CORE':9}
  #Many users may want to set ISO_CONV_CORE and ISO_CONV_FRINGE to the same value because the core and
  #fringe categories are closely related. Or such users can leave this code as-is and process the output
  #as if the two categories were the same category.
  
  ## ***************** END OUTPUT CONSTANTS   ******************

  log.basicConfig(format='%(levelname)s:%(message)s',level=log.INFO)

  #Check inputs
  if refl is None:
    log.info( "No reflectivity provided to raintype module.  Exiting ..." )
    rtout = None
    return rtout, types
  
  #Create missing value mask and turn refl missing values into NaN's
  mask = np.zeros(refl.shape)
  mask[(refl == refl_missing_val)] = 1
  refl[(mask == 1)] = np.nan

  #Convert dBZ to Z
  Z = rtf.DBZtoZ(refl)

  #If this is the first file in a batch, create a background reflectivity mask and
  #a mask for identifying regions around convective cores.
  if fname == os.listdir(fileDir)[0]:
    bgmask = rtf.makebgmask(backgrndradius,refl_dx)
    maskcell = rtf.makeconvmask(maxConvRadius,refl_dx) 

  #Now determine the background reflectivity at each grid point.
  background = rtf.get_background_refl(Z,bgmask)

  #Convert Z to dBZ
  background = rtf.ZtoDBZ(background)

  #Run convectivecore.
  rtout = alg.convectivecore(background,refl,minZdiff,types,dBZformaxconvradius,
                                maxConvRadius,weakechothres,deepcoszero,minsize,maxsize,
                                startslope,shallowconvmin,truncZconvthres,refl_dx,maskcell)

  #Apply missing value mask to raintype array
  rtout[mask == 1] = refl_missing_val

  return rtout, types
