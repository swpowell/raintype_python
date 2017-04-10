import netCDF4 as nc4
import numpy as np
import time as tm
import datetime as dt

def writeBasicNetcdf(ncname,types,deepcoszero,shallowconvmin,minZdiff,truncZconvthres,
                     dBZformaxconvradius,weakechothres,backgrndradius,maxConvRadius,
                     minsize,startslope,maxsize,title,institution,source,references1,
                     references2,comment,dx,radar_lat,radar_lon,raintype,missing_value):

    # get current time
    currentTime = tm.strftime("%m/%d/%Y %H:%M:%S");

    # open a new netcdf file
    ncid = nc4.Dataset(ncname,'w',format='NETCDF4')

    # create dimensions
    time = ncid.createDimension('time',None) # None implies UNLIMITED
    y = ncid.createDimension('y',raintype.shape[1])
    x = ncid.createDimension('x',raintype.shape[0])

    # create variables
    xspVar = ncid.createVariable('x_spacing',np.float32,zlib=True )
    yspVar = ncid.createVariable('y_spacing',np.float32,zlib=True )
    zthVar = ncid.createVariable('rt_Z_th',np.float32,zlib=True )
    rbgVar = ncid.createVariable('rt_R_bg',np.float32,zlib=True )
    aVar = ncid.createVariable('rt_a',np.float32,zlib=True )
    bVar = ncid.createVariable('rt_b',np.float32,zlib=True )
    rcVar = ncid.createVariable('rt_R_conv',np.float32,zlib=True )
    zcVar = ncid.createVariable('rt_Z_conv',np.float32,zlib=True )
    zwVar = ncid.createVariable('rt_Z_weak',np.float32,zlib=True )
    zsVar = ncid.createVariable('rt_Z_shallow',np.float32,zlib=True )
    alVar = ncid.createVariable('rt_A_low',np.float32,zlib=True )
    amVar = ncid.createVariable('rt_A_med',np.float32,zlib=True )
    ahVar = ncid.createVariable('rt_A_high',np.float32,zlib=True )
    rt = ncid.createVariable('rain_type',np.int32,('time','y','x'),zlib=True,fill_value=missing_value )

    # create variable attributes

    xspVar.units = 'km'
    yspVar.units = 'km'
    
    # Z_th
    zthVar.units = 'dBZ'
    zthVar.long_name = 'trunc_Z_conv_thres'
    zthVar.comment = 'reflectivity threshold at or above which echos are classified as convective'

    # R_bg
    rbgVar.units = 'km'
    rbgVar.long_name = 'backgrnd_radius'
    rbgVar.comment = 'radius within which background reflectivity is computed'

    # a
    aVar.units = 'dBZ'
    aVar.long_name = 'min_Z_diff'
    aVar.comment = 'factor for comparing echo to background reflectivity; see equation (1) in journal article referenced in "references1" general attribute'

    # b
    bVar.units = 'dBZ'
    bVar.long_name = 'deep_cos_zero'
    bVar.comment = 'see equation (1) in journal article referenced in  "references1" general attribute'

    # R_conv
    rcVar.units = 'km'
    rcVar.long_name = 'max_conv_radius'
    rcVar.comment = 'maximum radius around convective core for possible uncertain classification'

    # Z_conv
    zcVar.units = 'dBZ'
    zcVar.long_name = 'dbz_for_max_conv_radius'
    zcVar.comment = 'minimum dBZ required for max_conv_radius to apply'

    # Z_weak
    zwVar.units = 'dBZ'
    zwVar.long_name = 'weak_echo_thres'
    zwVar.comment = 'minimum dBZ for classification as not weak echo'

    # Z_shallow
    zsVar.units = 'dBZ'
    zsVar.long_name = 'shallow_conv_min'
    zsVar.comment = 'minimum dBZ for classification as convective for objects with area less than A-med'

    # A_low
    alVar.units = 'km^2'
    alVar.long_name = 'min_size'
    alVar.comment = 'minimum areal coverage a contiguous echo can cover and still receive an ISO_CONV classification'

    # A_med
    amVar.units = 'km^2'
    amVar.long_name = 'start_slope'
    amVar.comment = 'any contiguous echo object with areal coverage greater than this but less than A_high gets a new Z_th that is linearly interpolated between Z_shallow and Z_th depending on where area is between A_med and A_high'

    # A_high
    ahVar.units = 'km^2'
    ahVar.long_name = 'max_size'
    ahVar.comment = 'any contiguous echo object greater than this size gets a convective threshold of truncZconvthres'

    # rain_type
    rt.units = 'none'
    rt.long_name = 'rain_type_classification'
    #rt.flag_values = np.array((types['NO_ECHO'],types['STRATIFORM'],types['CONVECTIVE'],
    #                           types['UNCERTAIN'],types['ISO_CONV_CORE'],types['ISO_CONV_FRINGE'],
    #                           types['WEAK_ECHO']))
    #rt.flag_meanings = np.array(['NO_ECHO   STRATIFORM   CONVECTIVE   UNCERTAIN   ISO_CONV_CORE   ISO_CONV_FRINGE   WEAK_ECHO'])
    #TRY THIS:
    #rt.flag_meanings = "NO_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO"
    rt.NO_ECHO = types['NO_ECHO']
    rt.STRATIFORM = types['STRATIFORM']
    rt.CONVECTIVE = types['CONVECTIVE']
    rt.UNCERTAIN = types['UNCERTAIN']
    rt.ISO_CONV_CORE = types['ISO_CONV_CORE']
    rt.ISO_CONV_FRINGE = types['ISO_CONV_FRINGE']
    rt.WEAK_ECHO = types['WEAK_ECHO']

    rt.ancillary_variables = 'rt_Z_th rt_R_bg rt_a rt_b rt_R_conv rt_Z_conv rt_Z_weak rt_Z_shallow rt_A_low rt_A_med rt_A_high'

    # create global attributes
    ncid.title = title
    ncid.institution = institution
    ncid.history = 'File created ' + currentTime
    ncid.source = source
    ncid.references1 = references1
    ncid.references2 = references2
    ncid.comment = comment
    ncid.radar_lat = radar_lat
    ncid.radar_lon = radar_lon

    # write variables to file
    xspVar[:] = dx
    yspVar[:] = dx
    zthVar[:] = truncZconvthres
    rbgVar[:] = backgrndradius
    aVar[:] = minZdiff
    bVar[:] = deepcoszero
    rcVar[:] = maxConvRadius
    zcVar[:] = dBZformaxconvradius
    zwVar[:] = weakechothres
    zsVar[:] = shallowconvmin
    alVar[:] = minsize
    amVar[:] = startslope
    ahVar[:] = maxsize
    rt[0,:,:] = raintype

    # close file
    ncid.close()

def writeCFnetcdf(ncname,types,deepcoszero,shallowconvmin,minZdiff,truncZconvthres,
                  dBZformaxconvradius,weakechothres,backgrndradius,maxConvRadius,
                  minsize,startslope,maxsize,title,institution,source,references1,
                  references2,comment,timeVal,xVal,yVal,latVal,lonVal,gmVal,
                  lat_origin,lon_origin,raintype,missing_value):

    # get current time
    currentTime = tm.strftime("%m/%d/%Y %H:%M:%S");

    # convert timeVal to date and time
    date = dt.datetime.utcfromtimestamp(timeVal[0])
    datetime = date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # open a new netcdf file (default is format = 'NETCDF4', not 'NETCDF4_CLASSIC')
    ncid = nc4.Dataset(ncname,'w',format='NETCDF4')

    # create dimensions
    time = ncid.createDimension('time',None) # None implies UNLIMITED
    y = ncid.createDimension('y',raintype.shape[1])
    x = ncid.createDimension('x',raintype.shape[0])

    # create variables
    timeVar = ncid.createVariable('time',np.float64,('time'),zlib=True )
    xVar = ncid.createVariable('x',np.float32,('x'),zlib=True )
    yVar = ncid.createVariable('y',np.float32,('y'),zlib=True )
    latVar = ncid.createVariable('lat',np.float32,('y','x'),zlib=True )
    lonVar = ncid.createVariable('lon',np.float32,('y','x'),zlib=True )
    gmVar = ncid.createVariable('grid_mapping',np.int32)
    #gmVar = ncid.createVariable('azimuthal_equidistant',np.int32)
    zthVar = ncid.createVariable('rt_Z_th',np.float32)
    rbgVar = ncid.createVariable('rt_R_bg',np.float32)
    aVar = ncid.createVariable('rt_a',np.float32)
    bVar = ncid.createVariable('rt_b',np.float32)
    rcVar = ncid.createVariable('rt_R_conv',np.float32)
    zcVar = ncid.createVariable('rt_Z_conv',np.float32)
    zwVar = ncid.createVariable('rt_Z_weak',np.float32)
    zsVar = ncid.createVariable('rt_Z_shallow',np.float32)
    alVar = ncid.createVariable('rt_A_low',np.float32)
    amVar = ncid.createVariable('rt_A_med',np.float32)
    ahVar = ncid.createVariable('rt_A_high',np.float32)
    rt = ncid.createVariable('rain_type',np.int32,('time','y','x'),zlib=True,fill_value=missing_value )

    # create variable attributes
    timeVar.standard_name = 'time'
    timeVar.long_name = 'Data time'
    timeVar.units = 'seconds since 1970-01-01T00:00:00Z'
    timeVar.calendar = 'standard'
    timeVar.axis = 'T'
    #timeVar.bounds = 'time_bounds'
    timeVar.comment = datetime
    
    xVar.standard_name = 'projection_x_coordinate'
    xVar.long_name = 'x distance on the projection plane from the origin'
    xVar.units = 'km'
    xVar.axis = 'X'
    
    yVar.standard_name = 'projection_y_coordinate'
    yVar.long_name = 'y distance on the projection plane from the origin'
    yVar.units = 'km'
    yVar.axis = 'Y'
    
    latVar.standard_name = 'latitude'
    latVar.units = 'degrees_north'
    
    lonVar.standard_name = 'longitude'
    lonVar.units = 'degrees_east'
    
    gmVar.grid_mapping_name = 'azimuthal_equidistant'
    gmVar.longitude_of_projection_origin = lon_origin
    gmVar.latitude_of_projection_origin = lat_origin
    gmVar.false_easting = 0
    gmVar.false_northing = 0
    
    # Z_th
    zthVar.units = 'dBZ'
    zthVar.long_name = 'trunc_Z_conv_thres'
    zthVar.comment = 'reflectivity threshold at or above which echos are classified as convective'

    # R_bg
    rbgVar.units = 'km'
    rbgVar.long_name = 'backgrnd_radius'
    rbgVar.comment = 'radius within which background reflectivity is computed'

    # a
    aVar.units = 'dBZ'
    aVar.long_name = 'min_Z_diff'
    aVar.comment = 'factor for comparing echo to background reflectivity; see equation (1) in journal article referenced in "references1" general attribute'

    # b
    bVar.units = 'dBZ'
    bVar.long_name = 'deep_cos_zero'
    bVar.comment = 'see equation (1) in journal article referenced in  "references1" general attribute'

    # R_conv
    rcVar.units = 'km'
    rcVar.long_name = 'max_conv_radius'
    rcVar.comment = 'maximum radius around convective core for possible uncertain classification'

    # Z_conv
    zcVar.units = 'dBZ'
    zcVar.long_name = 'dbz_for_max_conv_radius'
    zcVar.comment = 'minimum dBZ required for max_conv_radius to apply'

    # Z_weak
    zwVar.units = 'dBZ'
    zwVar.long_name = 'weak_echo_thres'
    zwVar.comment = 'minimum dBZ for classification as not weak echo'

    # Z_shallow
    zsVar.units = 'dBZ'
    zsVar.long_name = 'shallow_conv_min'
    zsVar.comment = 'minimum dBZ for classification as convective for objects with area less than A-med'

    # A_low
    alVar.units = 'km^2'
    alVar.long_name = 'min_size'
    #alVar.comment = 'minimum areal coverage of echo object for classification as convective or stratiform'
    alVar.comment = 'minimum areal coverage a contiguous echo can cover and still receive an ISO_CONV classification'

    # A_med
    amVar.units = 'km^2'
    amVar.long_name = 'start_slope'
    #amVar.comment = 'maximum areal coverage of echo object for allowing new Z_th equal to Z_shallow'
    amVar.comment = 'any contiguous echo object with areal coverage greater than this but less than A_high gets a new Z_th that is linearly interpolated between Z_shallow and Z_th depending on where area is between A_med and A_high'

    # A_high
    ahVar.units = 'km^2'
    ahVar.long_name = 'max_size'
    ahVar.comment = 'any contiguous echo object greater than this size gets a convective threshold of truncZconvthres'

    # raintype
    rt.units = 'none'
    rt.long_name = 'rain_type_classification'
    #rt.grid_mapping = 'azimuthal_equidistant'
    rt.coordinates = 'lon lat'
    rt.grid_mapping = 'grid_mapping'
    #rt.flag_values = np.array((types['NO_ECHO'],types['STRATIFORM'],types['CONVECTIVE'],
    #                           types['UNCERTAIN'],types['ISO_CONV_CORE'],types['ISO_CONV_FRINGE'],
    #                           types['WEAK_ECHO']))
    #rt.flag_meanings = np.array(['NO_ECHO   STRATIFORM   CONVECTIVE   UNCERTAIN   ISO_CONV_CORE   ISO_CONV_FRINGE   WEAK_ECHO'])
    #TRY THIS:
    #rt.flag_meanings = "NO_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO"
    rt.NO_ECHO = types['NO_ECHO']
    rt.STRATIFORM = types['STRATIFORM']
    rt.CONVECTIVE = types['CONVECTIVE']
    rt.UNCERTAIN = types['UNCERTAIN']
    rt.ISO_CONV_CORE = types['ISO_CONV_CORE']
    rt.ISO_CONV_FRINGE = types['ISO_CONV_FRINGE']
    rt.WEAK_ECHO = types['WEAK_ECHO']
    rt.ancillary_variables = 'rt_Z_th rt_R_bg rt_a rt_b rt_R_conv rt_Z_conv rt_Z_weak rt_Z_shallow rt_A_low rt_A_med rt_A_high'

    # create global attributes
    ncid.Conventions = "CF-1.0"
    ncid.institution = institution
    ncid.source = source
    ncid.title = title
    ncid.references1 = references1
    ncid.references2 = references2
    ncid.comment = comment
    ncid.history = 'File created ' + currentTime

    # write vars to file
    timeVar[:] = timeVal
    xVar[:] = xVal
    yVar[:] = yVal
    latVar[:] = latVal
    lonVar[:] = lonVal
    #gmVar[:] = gmVal
    zthVar[:] = truncZconvthres
    rbgVar[:] = backgrndradius
    aVar[:] = minZdiff
    bVar[:] = deepcoszero
    rcVar[:] = maxConvRadius
    zcVar[:] = dBZformaxconvradius
    zwVar[:] = weakechothres
    zsVar[:] = shallowconvmin
    alVar[:] = minsize
    amVar[:] = startslope
    ahVar[:] = maxsize
    rt[0,:,:] = raintype

    # close file
    ncid.close()

def writeZebNetcdf(ncname,types,deepcoszero,shallowconvmin,minZdiff,truncZconvthres,
                   dBZformaxconvradius,weakechothres,backgrndradius,maxConvRadius,
                   minsize,startslope,maxsize,title,institution,source,references1,
                   references2,comment,btVal,toVal,latVal,lonVal,altVal,
                   xspVal,yspVal,zspVal,rtVal,missing_value):

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
    zthVar = ncid.createVariable('rt_Z_th',np.float32)
    rbgVar = ncid.createVariable('rt_R_bg',np.float32)
    aVar = ncid.createVariable('rt_a',np.float32)
    bVar = ncid.createVariable('rt_b',np.float32)
    rcVar = ncid.createVariable('rt_R_conv',np.float32)
    zcVar = ncid.createVariable('rt_Z_conv',np.float32)
    zwVar = ncid.createVariable('rt_Z_weak',np.float32)
    zsVar = ncid.createVariable('rt_Z_shallow',np.float32)
    alVar = ncid.createVariable('rt_A_low',np.float32)
    amVar = ncid.createVariable('rt_A_med',np.float32)
    ahVar = ncid.createVariable('rt_A_high',np.float32)
    rt = ncid.createVariable('rain_type',np.float32,('time','z','y','x',),fill_value=missing_value )

    # create variable attributes
    bt.units = 'seconds since 1970-01-01 00:00:00 +0000'
    to.units = 'seconds since base_time'
    lat.units = 'degrees_north'
    lon.units = 'degrees_east'
    alt.units = 'km'
    xsp.units = 'km'
    ysp.units = 'km'
    zsp.units = 'km'
    # Z_th
    zthVar.units = 'dBZ'
    zthVar.long_name = 'trunc_Z_conv_thres'
    zthVar.comment = 'reflectivity threshold at or above which echos are classified as convective'

    # R_bg
    rbgVar.units = 'km'
    rbgVar.long_name = 'backgrnd_radius'
    rbgVar.comment = 'radius within which background reflectivity is computed'

    # a
    aVar.units = 'dBZ'
    aVar.long_name = 'min_Z_diff'
    aVar.comment = 'factor for comparing echo to background reflectivity; see equation (1) in journal article referenced in "references1" general attribute'

    # b
    bVar.units = 'dBZ'
    bVar.long_name = 'deep_cos_zero'
    bVar.comment = 'see equation (1) in journal article referenced in  "references1" general attribute'

    # R_conv
    rcVar.units = 'km'
    rcVar.long_name = 'max_conv_radius'
    rcVar.comment = 'maximum radius around convective core for possible uncertain classification'

    # Z_conv
    zcVar.units = 'dBZ'
    zcVar.long_name = 'dbz_for_max_conv_radius'
    zcVar.comment = 'minimum dBZ required for max_conv_radius to apply'

    # Z_weak
    zwVar.units = 'dBZ'
    zwVar.long_name = 'weak_echo_thres'
    zwVar.comment = 'minimum dBZ for classification as not weak echo'

    # Z_shallow
    zsVar.units = 'dBZ'
    zsVar.long_name = 'shallow_conv_min'
    zsVar.comment = 'minimum dBZ for classification as convective for objects with area less than A-med'

    # A_low
    alVar.units = 'km^2'
    alVar.long_name = 'min_size'
    #alVar.comment = 'minimum areal coverage of echo object for classification as convective or stratiform'
    alVar.comment = 'minimum areal coverage a contiguous echo can cover and still receive an ISO_CONV classification'

    # A_med
    amVar.units = 'km^2'
    amVar.long_name = 'start_slope'
    #amVar.comment = 'maximum areal coverage of echo object for allowing new Z_th equal to Z_shallow'
    amVar.comment = 'any contiguous echo object with areal coverage greater than this but less than A_high gets a new Z_th that is linearly interpolated between Z_shallow and Z_th depending on where area is between A_med and A_high'

    # A_high
    ahVar.units = 'km^2'
    ahVar.long_name = 'max_size'
    ahVar.comment = 'any contiguous echo object greater than this size gets a convective threshold of truncZconvthres'

    # rain_type
    rt.units = 'none'
    rt.long_name = 'rain_type_classification'
    #rt.flag_values = np.array((types['NO_ECHO'],types['STRATIFORM'],types['CONVECTIVE'],
    #                           types['UNCERTAIN'],types['ISO_CONV_CORE'],types['ISO_CONV_FRINGE'],
    #                           types['WEAK_ECHO']))
    #rt.flag_meanings = np.array(['NO_ECHO   STRATIFORM   CONVECTIVE   UNCERTAIN   ISO_CONV_CORE   ISO_CONV_FRINGE   WEAK_ECHO'])
    #TRY THIS:
    #rt.flag_meanings = "NO_ECHO,STRATIFORM,CONVECTIVE,UNCERTAIN,ISO_CONV_CORE,ISO_CONV_FRINGE,WEAK_ECHO"
    rt.NO_ECHO = types['NO_ECHO']
    rt.STRATIFORM = types['STRATIFORM']
    rt.CONVECTIVE = types['CONVECTIVE']
    rt.UNCERTAIN = types['UNCERTAIN']
    rt.ISO_CONV_CORE = types['ISO_CONV_CORE']
    rt.ISO_CONV_FRINGE = types['ISO_CONV_FRINGE']
    rt.WEAK_ECHO = types['WEAK_ECHO']
    rt.ancillary_variables = 'rt_Z_th rt_R_bg rt_a rt_b rt_R_conv rt_Z_conv rt_Z_weak rt_Z_shallow rt_A_low rt_A_med rt_A_high'

    # create global attributes
    ncid.title = title
    ncid.institution = institution
    ncid.history = 'File created ' + currentTime
    ncid.source = source
    ncid.references1 = references1
    ncid.references2 = references2
    ncid.comment = comment

    # write vars to file
    bt[:] = btVal
    to[:] = toVal
    lat[:] = latVal
    lon[:] = lonVal
    alt[:] = altVal
    xsp[:] = xspVal
    ysp[:] = yspVal
    zsp[:] = zspVal
    zthVar[:] = truncZconvthres
    rbgVar[:] = backgrndradius
    aVar[:] = minZdiff
    bVar[:] = deepcoszero
    rcVar[:] = maxConvRadius
    zcVar[:] = dBZformaxconvradius
    zwVar[:] = weakechothres
    zsVar[:] = shallowconvmin
    alVar[:] = minsize
    amVar[:] = startslope
    ahVar[:] = maxsize
    rt[0,0,:,:] = rtVal

    #close file
    ncid.close()
