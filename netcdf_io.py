import netCDF4 as nc4
import numpy as np
import time as tm
import datetime as dt

#def read():

#def readZeb():

def writeBasicNetcdf(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO,   \
                     deepcoszero,shallowconvmin,minZdiff,truncZconvthres,dBZformaxconvradius,weakechothres,        \
                     backgrndradius,maxConvRadius,minsize,startslope,maxsize,title,institution,source,references,  \
                     comment,xdim,ydim,raintype):

    # get current time
    currentTime = tm.strftime("%m/%d/%Y %H:%M:%S");

    # open a new netcdf file
    ncid = nc4.Dataset(ncname,'w',format='NETCDF4')

    # create dimensions
    time = ncid.createDimension('time',None) # None implies UNLIMITED
    x = ncid.createDimension('x',raintype.shape[0])
    y = ncid.createDimension('y',raintype.shape[1])

    # create variables
    rt = ncid.createVariable('rain_type',np.int32,('time','y','x') )

    # create variable attributes
    rt.long_name = 'rain type: one of NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO'
    rt.units = 'none'
    #rt.values = np.array((0,1,2,3,4,5,6))
    #rt.meanings = np.array(['NO_SFC_ECHO','STRATIFORM','CONVECTIVE','UNCERTAIN','ISO_CONV_CORE','ISO_CONV_FRINGE','WEAK_ECHO'])
    rt.NO_SFC_ECHO = NO_SFC_ECHO
    rt.STRATIFORM = STRATIFORM
    rt.CONVECTIVE = CONVECTIVE
    rt.UNCERTAIN = UNCERTAIN
    rt.ISO_CONV_CORE = ISO_CONV_CORE
    rt.ISO_CONV_FRINGE = ISO_CONV_FRINGE
    rt.WEAK_ECHO = WEAK_ECHO
    rt.deepcoszero = deepcoszero
    rt.shallowconvmin = shallowconvmin
    rt.minZdiff = minZdiff
    rt.truncZconvthres = truncZconvthres
    rt.dBZformaxconvradius = dBZformaxconvradius
    rt.weakechothres = weakechothres
    rt.backgrndradius = backgrndradius
    rt.maxConvRadius = maxConvRadius
    rt.minsize = minsize
    rt.startslope = startslope
    rt.maxsize = maxsize

    # create global attributes
    ncid.Conventions = "CF-1.0"
    ncid.title = title
    ncid.institution = institution
    ncid.history = 'File created ' + currentTime
    ncid.source = source
    ncid.references = references
    ncid.comment = comment

    # write variables to file
    rt[0,:,:] = raintype

    # close file
    ncid.close()

def writeCF(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO,   \
            deepcoszero,shallowconvmin,minZdiff,truncZconvthres,dBZformaxconvradius,weakechothres,        \
            backgrndradius,maxConvRadius,minsize,startslope,maxsize,title,institution,source,references,  \
            comment,timeVal,xVal,yVal,gmVal,lat_origin,lon_origin,raintype):

    print ("lat and lon origin = " + lat_origin + lon_origin)
    
    # get current time
    currentTime = tm.strftime("%m/%d/%Y %H:%M:%S");

    # convert timeVal to date and time
    date = dt.datetime.fromtimestamp(timeVal[0])
    datetime = date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # open a new netcdf file (default is format = 'NETCDF4', not 'NETCDF4_CLASSIC')
    ncid = nc4.Dataset(ncname,'w',format='NETCDF4')

    # create dimensions
    time = ncid.createDimension('time',None) # None implies UNLIMITED
    x = ncid.createDimension('x',raintype.shape[0])
    y = ncid.createDimension('y',raintype.shape[1])

    # create variables
    timeVar = ncid.createVariable('time',np.int64q,('time') )
    xVar = ncid.createVariable('x',np.float32,('x') )
    yVar = ncid.createVariable('y',np.float32,('y') )
    gmVar = ncid.createVariable('grid_mapping',np.int32)
    rt = ncid.createVariable('rain_type',np.int32,('time','y','x') )

    # create variable attributes
    timeVar.standard_name = 'time'
    timeVar.long_name = 'Data time'
    timeVar.units = 'seconds since 1970-01-01T00:00:00Z'
    timeVar.axis = 'T'
    #timeVar.bounds = 'time_bounds'
    timeVar.comment = datetime
    xVar.standard_name = 'projection_x_coordinate'
    xVar.units = 'km'
    xVar.axis = 'X'
    yVar.standard_name = 'projection_y_coordinate'
    yVar.units = 'km'
    yVar.axis = 'Y'
    gmVar.grid_mapping_name = 'azimuthal_equidistant'
    gmVar.longitude_of_projection_origin = lon_origin
    gmVar.latitude_of_projection_origin = lat_origin
    gmVar.false_easting = 0
    gmVar.false_northing = 0
    rt.long_name = 'rain type: one of NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO'
    rt.units = 'none'
    #rt.values = np.array((0,1,2,3,4,5,6))
    #rt.meanings = np.array(['NO_SFC_ECHO','STRATIFORM','CONVECTIVE','UNCERTAIN','ISO_CONV_CORE','ISO_CONV_FRINGE','WEAK_ECHO'])
    rt.NO_SFC_ECHO = NO_SFC_ECHO
    rt.STRATIFORM = STRATIFORM
    rt.CONVECTIVE = CONVECTIVE
    rt.UNCERTAIN = UNCERTAIN
    rt.ISO_CONV_CORE = ISO_CONV_CORE
    rt.ISO_CONV_FRINGE = ISO_CONV_FRINGE
    rt.WEAK_ECHO = WEAK_ECHO
    rt.deepcoszero = deepcoszero
    rt.shallowconvmin = shallowconvmin
    rt.minZdiff = minZdiff
    rt.truncZconvthres = truncZconvthres
    rt.dBZformaxconvradius = dBZformaxconvradius
    rt.weakechothres = weakechothres
    rt.backgrndradius = backgrndradius
    rt.maxConvRadius = maxConvRadius
    rt.minsize = minsize
    rt.startslope = startslope
    rt.maxsize = maxsize

    # create global attributes
    ncid.Conventions = "CF-1.0"
    ncid.title = title
    ncid.institution = institution
    ncid.history = 'File created ' + currentTime
    ncid.source = source
    ncid.references = references
    ncid.comment = comment

    # write vars to file
    timeVar[:] = timeVal
    xVar[:] = xVal
    yVar[:] = yVal
    #gmVar[:] = gmVal
    rt[0,:,:] = raintype

    # close file
    ncid.close()

def writeZeb(ncname,NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO,  \
             deepcoszero,shallowconvmin,minZdiff,truncZconvthres,dBZformaxconvradius,weakechothres,       \
             backgrndradius,maxConvRadius,minsize,startslope,maxsize,title,institution,source,references,      \
             comment,btVal,toVal,latVal,lonVal,altVal,xspVal,yspVal,rtVal):

    # get current time
    currentTime = tm.strftime("%m/%d/%Y %H:%M:%S");

    # open a new netcdf file for writing (default is format = 'NETCDF4', not 'NETCDF4_CLASSIC')
    ncid = nc4.Dataset(ncname,'w',format='NETCDF4')

    # create dimensions
    time = ncid.createDimension('time',None) # None implies UNLIMITED
    z = ncid.createDimension('z',1)
    y = ncid.createDimension('y',rtVal.shape[1])
    x = ncid.createDimension('x',rtVal.shape[0])

    # create variables
    bt = ncid.createVariable('base_time',np.float64 )
    to = ncid.createVariable('time_offset',np.float32,('time',) )
    lat = ncid.createVariable('lat',np.float32 )
    lon = ncid.createVariable('lon',np.float32 )
    alt = ncid.createVariable('alt',np.float32 )
    xsp = ncid.createVariable('x_spacing',np.float32 )
    ysp = ncid.createVariable('y_spacing',np.float32 )
    zsp = ncid.createVariable('z_spacing',np.float32 )
    rt = ncid.createVariable('rain_type',np.float32,('time','z','y','x',) )

    # create variable attributes
    bt.units = 'seconds since 1970-01-01 00:00:00 +0000'
    to.units = 'seconds since base_time'
    lat.units = 'degrees_north'
    lon.units = 'degrees_east'
    alt.units = 'km'
    xsp.units = 'km'
    ysp.units = 'km'
    zsp.units = 'km'
    rt.long_name = 'rain type: one of NO_SFC_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO'
    rt.units = 'none'
    #rt.values = np.array((0,1,2,3,4,5,6))
    #rt.meanings = np.array(['NO_SFC_ECHO','STRATIFORM','CONVECTIVE','UNCERTAIN','ISO_CONV_CORE','ISO_CONV_FRINGE','WEAK_ECHO'])
    #rt.category_legend = "\n1: stratiform\n2: convective"
    rt.NO_SFC_ECHO = NO_SFC_ECHO
    rt.STRATIFORM = STRATIFORM
    rt.CONVECTIVE = CONVECTIVE
    rt.UNCERTAIN = UNCERTAIN
    rt.ISO_CONV_CORE = ISO_CONV_CORE
    rt.ISO_CONV_FRINGE = ISO_CONV_FRINGE
    rt.WEAK_ECHO = WEAK_ECHO
    rt.deepcoszero = deepcoszero
    rt.shallowconvmin = shallowconvmin
    rt.minZdiff = minZdiff
    rt.truncZconvthres = truncZconvthres
    rt.dBZformaxconvradius = dBZformaxconvradius
    rt.weakechothres = weakechothres
    rt.backgrndradius = backgrndradius
    rt.maxConvRadius = maxConvRadius
    rt.minsize = minsize
    rt.startslope = startslope
    rt.maxsize = maxsize

    # create global attributes
    ncid.title = title
    ncid.institution = institution
    ncid.history = 'File created ' + currentTime
    ncid.source = source
    ncid.references = references
    ncid.comment = comment

    # write vars to file
    bt[:] = btVal
    to[:] = toVal
    lat[:] = latVal
    lon[:] = lonVal
    alt[:] = altVal
    xsp[:] = xspVal
    ysp[:] = yspVal
    zsp[:] = 1
    rt[0,0,:,:] = rtVal

    #close file
    ncid.close()
