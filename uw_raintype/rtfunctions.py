from __future__ import division     #For python2 users only.
import numpy as np
import math

def ZtoDBZ(z):
  return 10*np.log10(z)

def DBZtoZ(dbz):
  return 10**(0.1*dbz)

def makebgmask(backgrndradius,dx):

  global bgmask

  bgrange = int(max(1,np.ceil(backgrndradius/dx)))

  bgmask = np.zeros((2*bgrange+1, 2*bgrange+1), dtype='float')
  for i in range(-bgrange,bgrange+1):
    for j in range(-bgrange,bgrange+1):
      if ( (i*dx)**2 + (j*dx)**2 ) <= backgrndradius**2:
        bgmask[i+bgrange,j+bgrange] = 1

  bgmask = bgmask/(sum(sum(bgmask)))

  return bgmask

def makeconvmask(maxConvRadius,dx):

  global maskcell

  #Create a mask, maskcell. Different indices for maskcell are for masks of different
  #sizes.
  d = list(range(maxConvRadius-4,maxConvRadius+1))
  #The 4 in above line assumes minimum radius in section above is 6 km.
  n = [np.int16(np.floor(x/dx)) for x in d]
  a = [2*x+1 for x in n]
  maskcell = [np.zeros([x,x]) for x in a]
  for k in range(0,len(d)):
    mask = np.zeros([int(2*n[k]+1),int(2*n[k]+1)])
    for i in range(-n[k],n[k]+1):
      for j in range(-n[k],n[k]+1):
        if ( (i*dx)**2 + (j*dx)**2 ) <= d[k]**2:
          mask[i+n[k],j+n[k]] = 1
    maskcell[k] = mask

  return maskcell

def get_background_refl(Z,bgmask):

  from scipy import signal as sg

  #Create background variable.
  background = np.zeros(Z.shape)
  Z[np.isnan(Z)] = 0

  #First convolve the mask with the reflectivity data. The result will be
  #a matrix that reports background reflectivity even where there is zero
  #reflectivity.
  bg1 = sg.convolve2d(Z,bgmask,mode='same',boundary='symm',fillvalue=0)
  Z[Z != 0] = 1
  #Next, convolve the mask with ones and zeros, where the ones are where
  #reflectivity is nonzero.
  bg2 = sg.convolve2d(Z,bgmask,mode='same',boundary='symm',fillvalue=0)
  #Normalize to determine the actual background reflectivity.
  background = bg1/bg2
  #Make sure non-existent values in background are NaN
  background[Z==0] = np.nan

  return background

def chopmask(inmask,topchop,rightchop,btmchop,leftchop):
  from copy import copy

  #Simply trims inmask so it fits data on edge of domain. Returns newmask. 
  newmask = copy(inmask)
  masksize = inmask.shape[1]

  if topchop != 0:
      newmask = newmask[:,0:masksize-topchop] 
  if rightchop != 0:
      newmask = newmask[0:masksize-rightchop,:]
  if btmchop != 0:
      newmask = newmask[:,btmchop:]
  if leftchop != 0:
      newmask = newmask[leftchop:,:]

  return newmask

#The following 2 functions are to speed up makedBZcluster. From https://stackoverflow.com/questions/33281957/faster-alternative-to-numpy-where

def compute_M(data):
  from scipy.sparse import csr_matrix
  import numpy as np
  cols = np.arange(data.size)
  return csr_matrix((cols, (data.ravel(), cols)),
                    shape=(data.max() + 1, data.size))

def get_indices_sparse(data):
  import numpy as np
  M = compute_M(data)
  return [np.unravel_index(row.data, data.shape) for row in M]

def makedBZcluster(refl,isCore,convsfmat,weakechothres,minsize,maxsize,startslope,
                   shallowconvmin,truncZconvthres,types,dx):

  from scipy import ndimage as nd

  #Allocate matrix indicating whether rain is occurring.
  rain = np.zeros((refl.shape),dtype=np.int)

  #If echo is strong enough, rain = 1.
  rain[refl>=weakechothres] = 1

  #Create truncvalue, which has same shape as reflectivity data. It indicates the 
  #reflectivity over which an echo is automatically classified as some sort of 
  #ISOLATED CONVECTIVE echo. See details below.
  truncvalue = np.ones((refl.shape),dtype=np.float64)*truncZconvthres

  #This is a blob detector. Detects contiguous areas of raining pixels. Diagonally
  #touching pixels that share a corner don't count. Edges must touch.
  #echoes contains the blob objects, numechoes is just a count of them.
  (echoes,numechoes) = nd.label(rain)

  #Get 2D indices of echo objects.
  K = get_indices_sparse(echoes)
  K = K[1:] #Exclude echoes==0.

  for i in np.arange(len(K)):
     
    I = K[i][0]
    J = K[i][1]
 
    #Compute the total areal coverage of the echo object.
    clusterarea = (dx**2)*len(I)    #In km^2

    #Any echo object with a size between minsize and maxsize is considered 
    #ISOLATED CONVECTION. First, make all of it FRINGE.
    if clusterarea >= minsize and clusterarea <= maxsize:
      convsfmat[I,J] = types['ISO_CONV_FRINGE'] 

    #Very small echo objects are dismissed as WEAK ECHO.  
    if clusterarea < minsize:
      isCore[I,J] = 0
      convsfmat[I,J] = types['WEAK_ECHO']
    #Echo objects with size between minsize and startslope get a small truncvalue
    #equal to shallowconvmin.
    elif clusterarea >= minsize and clusterarea < startslope:
      truncvalue[I,J] = shallowconvmin
    #Echo objects with size between startslope and maxsize get a truncvalue that 
    #is linearly interpolated between shallowconvmin and truncZconvthres depending
    #on the size relative to startslope and maxsize.
    elif clusterarea >= startslope and clusterarea <= maxsize:
      truncvalue[I,J] = shallowconvmin + float((clusterarea-startslope)/(maxsize-startslope))*(truncZconvthres-shallowconvmin)

    #Evaluate isCore with size of echo object accounted for.
    #First, if reflectivity exceeds truncvalue, classify it as ISOLATED CONVECTIVE CORE.
    isCore[refl >= truncvalue] = types['ISO_CS_CORE']

    #But if reflectivity exceeds original reflectivity threshold, classify as CONVECTIVE core.
    isCore[refl >= truncZconvthres] = types['CS_CORE']

  return (convsfmat,isCore)


def radial_distance_mask(min_radius, max_radius, xdim, ydim, x_spacing, y_spacing):

    """
    Description: Creates a radar coverage mask for a square grid

    Inputs:

    Outputs:

    """
    mask = np.zeros(shape=(ydim,xdim))

    center_y = int(math.floor(ydim/2.)) - 0.5
    center_x = int(math.floor(xdim/2.)) - 0.5
      
    for j in range(0,ydim):
        for i in range(0,xdim):
            y_range_sq = math.pow( ((center_y-j)*y_spacing), 2 )
            x_range_sq = math.pow( ((center_x-i)*x_spacing), 2 )
            dist = math.sqrt(x_range_sq+y_range_sq)
            if dist < max_radius and dist > min_radius:
                mask[j,i] = 1

    return mask
