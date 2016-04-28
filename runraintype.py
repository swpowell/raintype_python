## *****Rain-type Classification code of Powell et al. (2016, JTECH): Driver code in python*****#
#Author: Scott Powell and Stacy Brodzik, University of Washington
#Date: April 11, 2016
#Description: This is the driver code for the updated version of Steiner et al. (1995)
#   convective/stratiform classification code for use with Cartesian gridded datasets. Adds new
#   categories for echoes of uncertain rain-type near convective cores and correctly identifies
#   isolated, often shallow, convection as convective instead of stratiform. For details, see
#   Powell, S.W., R.A. Houze, JR., and S.R. Brodzik, 2016: Rainfall-type categorization of radar
#   echoes using polar coordinate reflectivity data, J. Atmos. Oceanic Technol., 17, 523-538.
#   The variables listed in the left column immediately below are those in the user-input
#   parameters farther below. The variables listed in the right column below are the
#   corresponding variable names in Table 1 of Powell et al. (2016).
#
#   Variable name in this code          Variable name in Powell et al.
#
#   minZdiff                            a
#   deepcoszero                         b
#   shallowconvmin                      Z_shallow
#   truncZconvthres                     Z_th
#   dBZformaxconvradius                 Z_conv
#   weakechothres                       Z_weak
#   backgrndradius                      R_bg
#   maxconvRadius                       R_conv
#   minsize                             A_low
#   startslope                          A_med
#   maxsize                             A_high
#### 

from __future__ import division  #For python2 only. Alternatively, run interpreter with -Q flag. 
import netCDF4 as nc4
import numpy as np
import os
import algorithm as alg
import netcdf_io as net
import logging as log

## ***************** ALGORITHM USER-INPUT PARAMETERS *****************

## reflectivity info
refl_name = 'REFL';
refl_level = 5;
refl_mv = -9999;   #Missing value of reflectivity field.  Only used if not in input file
refl_dx = 2;       #Grid spacing of Cartesian reflectivity data.  Only used if not in input file

## radar info - only use this if data not contained in input file
radar_lat = -0.630447;
radar_lon = 73.10277;

## preferred netcdf output format - one of 'basic', 'cf' (CF compliant) or 'zeb' (Zebra compliant)
## NOTE: if the input file does not contain the fields required for the preferred output format
## then the output format will be set to 'basic'; if you are unsure, leave this set to 'cf'
outputFormat = 'cf'

## variables required in input file for cf or zebra compliant output; these names may be spelled
## slightly differently from time to time so we include them as inputs
## ********** DO NOT REMOVE ANY ELEMENTS OR CHANGE THE ORDER OF THE ARRAYS **********
var_cf = ['time','x0','y0','lat0','lon0','grid_mapping_0']
var_zeb = ['base_time','time_offset','lat','lon','alt','x_spacing','y_spacing','z_spacing']

## rain type input parameters
minZdiff = 20; #SWP originally tested this as a function of radius, and no major changes were observed
               #in DYNAMO S-PolKa classifications.

deepcoszero = 40;
shallowconvmin = 28;

#Classification is most sensitive to truncZconvthres. Any dBZ value in excess of truncZconvthres will
#be classified as convective. The value in Powell et al. (2016) was used for an S-band radar with a
#beam width of 0.91 degrees. For C-band and/or larger beam width, this value will probably need to be
#decreased.
truncZconvthres = 43;

#This should be somewhere close to truncZconvthres. Tuning will probably be required.
dBZformaxconvradius = 46;

#Don't change this without a good reason. This is about as low as we can go without getting into Bragg
#scatter territory.
weakechothres = 7;

#The background reflectivity for each data point is calculated as the average reflectivity (Z)
#within this radius of the data point.
backgrndradius = 5;       #(in km)

#Powell et al. (2016) tested 5, and showed that too much convection was included in stratiform region.
#Don't lower this number without a good reason
maxConvRadius = 10;       #(in km)

#See dBZcluster for use.
#minsize is the minimum areal coverage a contiguous echo can cover and still receive a ISO_CONV
#type classification.
minsize = 8;              #(in km^2)

#Any contiguous echo object with areal coverage greater than this but less than maxsize gets a new
#convective threshold that is linearly interpolated between shallowconvmin and truncZconvthres
#depending on where between startslope and maxsize its area is. (See makedBZcluster.)
startslope = 50;          #(in km^2)

#Any contiguous echo object greater than this size gets a convective threshold of truncZconvthres
#(See makedBZcluster).
maxsize = 2000;           #(in km^2)

## Information about where the reflectivity data is located and where outputs should be written.
fileDir = '/home/disk/mjo/dynamo/data.server/zebra/QCed/spolka/sur_2km_legacy/20111016/';
fileDirOut = '/home/disk/mjo/dynamo/data.server/zebra/QCed/spolka/rain_type/sur_2km_legacy/';

## Information about output
title = 'Rain type classification of DYNAMO SPolKa radar data';
institution = 'University of Washington';
source = 'Code used https://github.com/swpowell/raintype_python';
references = 'http://www.atmos.uw.edu/MG/PDFs/JTECH16_Powell-etal_RainCat.pdf';
comment = 'Based on 2.5km level of interpolated reflectivity data';

## *****************  END USER INPUT PARAMETERS *****************

## *****************  BEGIN OUTPUT CONSTANTS *****************
# Output constants: Do not change these without a good reason!
CS_CORE = 8;          #For convective core scheme.
ISO_CS_CORE = 9;
NO_SFC_ECHO = 0;
STRATIFORM = 1;
CONVECTIVE = 2;
UNCERTAIN = 3;
#Many users may want to set ISO_CONV_CORE and ISO_CONV_FRINGE to the same value because the core and
#fringe categories are closely related. Or such users can leave this code as-is and process the output
#as if the two categories were the same category.
ISO_CONV_CORE = 4;
ISO_CONV_FRINGE = 5;
WEAK_ECHO = 6;

## ***************** END OUTPUT CONSTANTS   ******************

log.basicConfig(format='%(levelname)s:%(message)s',level=log.INFO)

for fname in os.listdir(fileDir):
  if fname.endswith('nc'):

    log.info( "file = {}".format(fname) )
  
    #Filename for output
    ncname = str(fileDirOut + 'raintype_' + fname)

    #Open input file
    ncid = nc4.Dataset(str(fileDir + fname),'r')

    #If check to make sure all vars necessary for output format are present in input file
    if outputFormat == 'zeb':
      for x in var_zeb:
        try:
          ncid.variables[x]
        except:
          outputFormat = 'basic'
          break
    elif outputFormat == 'cf':  
      for x in var_cf:
        try:
          ncid.variables[x]
        except:
          outputFormat = 'basic'
          break
      
    log.info( "outputFormat = {}".format(outputFormat) )
    
    #Make sure refl_name exists.
    try:
      ncid.variables[refl_name]
    except:
      raise SystemExit('Name of reflectivity variable is incorrect. See user input.')
   
    #If variables required by zebra netcdf files are present, read them
    if outputFormat == 'zeb':
      bt = ncid.variables[var_zeb[0]][:]
      toff = ncid.variables[var_zeb[1]][:]
      lat = ncid.variables[var_zeb[2]][:]
      lon = ncid.variables[var_zeb[3]][:]
      alt = ncid.variables[var_zeb[4]][:]
      dx = ncid.variables[var_zeb[5]][:]
      dy = ncid.variables[var_zeb[6]][:]
      dz = ncid.variables[var_zeb[7]][:]
      missing_value = ncid.variables[refl_name].missing_value
    #If variables required for cf-compliancy are present, read them
    elif outputFormat == 'cf':
      dx = refl_dx
      missing_value = refl_mv
      tim = ncid.variables[var_cf[0]][:]
      x = ncid.variables[var_cf[1]][:]
      y = ncid.variables[var_cf[2]][:]
      lat = ncid.variables[var_cf[3]][:]
      lon = ncid.variables[var_cf[4]][:]
      gm = ncid.variables[var_cf[5]][:]
      #gmAtts = ncid.variables[var_cf[5]]
      lat_origin = ncid.variables[var_cf[5]].latitude_of_projection_origin
      lon_origin = ncid.variables[var_cf[5]].longitude_of_projection_origin
    else:
      dx = refl_dx
      missing_value = refl_mv

    #Read in reflectivity
    refl = np.array(np.squeeze(ncid.variables[refl_name][:,refl_level-1,:,:]))
    refl[(refl == missing_value)] = np.nan

    #Close input file
    ncid.close()
  
    #Convert dBZ to Z
    Z = 10**(0.1*refl)

    #Create background variable.
    background = np.zeros(refl.shape)

    #How many grid boxes from the center of the grid box of interest does it take to get to a distance
    #backgrndradius from the center of the grid box of interest? This needs to be an integer.
    edgevalue = np.floor(backgrndradius/dx)-1-1		#Subtract 1 again for 0-indexing.
  
    bgrange = int(max(1,np.ceil(backgrndradius/dx)-1))

    #Now determine the background reflectivity at each grid point.
    for i in range(0,refl.shape[0]):
      for j in range(0,refl.shape[1]):
        #The normal case
        if i > edgevalue+1 and i < Z.shape[0]-edgevalue-2 and j > edgevalue+1 and j < Z.shape[1]-edgevalue-2:
          #This is a 10km X 10 km square for data with 2km grid spacing. It's not a circle with 5 km
          #radius, but it's good enough.
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:i+bgrange+1,j-bgrange:j+bgrange+1]));
        elif i <= edgevalue+1 and j <= edgevalue+1:   #Bottom left corner
          background[i,j] = np.nanmean(np.nanmean(Z[0:i+bgrange+1,0:j+bgrange+1]));
        elif i <= edgevalue+1 and j > edgevalue+1 and j < Z.shape[1]-edgevalue-2: #Left side
          background[i,j] = np.nanmean(np.nanmean(Z[0:i+bgrange+1,j-bgrange:j+bgrange+1]));
        elif i <= edgevalue+1 and j >= Z.shape[1]-edgevalue-2: #Top left corner
          background[i,j] = np.nanmean(np.nanmean(Z[0:i+bgrange+1,j-bgrange:Z.shape[1]+1]));
        elif i >= Z.shape[0]-edgevalue-2 and j >= Z.shape[1]-edgevalue-2:  #Top right corner
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:Z.shape[0]+1,j-bgrange:Z.shape[1]+1]));
        elif i >= Z.shape[0]-edgevalue-2 and j <= edgevalue+1:  #Bottom right corner
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:Z.shape[0]+1,0:j+bgrange+1]));
        elif i >= Z.shape[0]-edgevalue-2 and j > edgevalue+1 and j < Z.shape[1]-edgevalue-2:  #Right side
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:Z.shape[0]+1,j-bgrange:j+bgrange]+1));
        elif i > edgevalue+1 and i < Z.shape[0]-edgevalue-2 and j <= edgevalue+1: #Bottom side
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:i+bgrange+1,0:j+bgrange+1]));
        elif i > edgevalue+1 and i < Z.shape[0]-edgevalue-2 and j >= Z.shape[1]-edgevalue-2: #Top side
          background[i,j] = np.nanmean(np.nanmean(Z[i-bgrange:i+bgrange+1,j-bgrange:Z.shape[1]+1]));

    #Make sure non-existent values in background are NaN
    background[(background==0)] = np.nan

    #Convert Z to dBZ
    background = 10*np.log10(background)

    #Run convectivecore.
    raintype = alg.convectivecore(background,refl,minZdiff,CS_CORE,ISO_CS_CORE,CONVECTIVE,STRATIFORM,UNCERTAIN,  \
                                  WEAK_ECHO,ISO_CONV_CORE,ISO_CONV_FRINGE,NO_SFC_ECHO,dBZformaxconvradius,       \
                                  maxConvRadius,weakechothres,deepcoszero,minsize,maxsize,startslope,            \
                                  shallowconvmin,truncZconvthres,dx)

    if outputFormat == 'zeb':
      net.writeZebNetcdf(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE, \
                         ISO_CONV_FRINGE,WEAK_ECHO,deepcoszero,shallowconvmin,minZdiff,    \
                         truncZconvthres,dBZformaxconvradius,weakechothres,backgrndradius, \
                         maxConvRadius,minsize,startslope,maxsize,title,institution,source,\
                         references,comment,bt,toff,lat,lon,alt,dx,dy,dz,raintype)
    elif outputFormat == 'cf':
      net.writeCFnetcdf(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE, \
                        ISO_CONV_FRINGE,WEAK_ECHO,deepcoszero,shallowconvmin,minZdiff,    \
                        truncZconvthres,dBZformaxconvradius,weakechothres,backgrndradius, \
                        maxConvRadius,minsize,startslope,maxsize,title,institution,source,\
                        references,comment,tim,x,y,lat,lon,gm,lat_origin,lon_origin,raintype)
    else:
      net.writeBasicNetcdf(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE, \
                           ISO_CONV_FRINGE,WEAK_ECHO,deepcoszero,shallowconvmin,minZdiff,    \
                           truncZconvthres,dBZformaxconvradius,weakechothres,backgrndradius, \
                           maxConvRadius,minsize,startslope,maxsize,title,institution,source,\
                           references,comment,dx,radar_lat,radar_lon,raintype.shape[0],      \
                           raintype.shape[1],raintype)
