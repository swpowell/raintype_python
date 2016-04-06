from __future__ import division     #For python2 users only.

def chopmask(inmask,topchop,rightchop,btmchop,leftchop):

  #Simply trims inmask so it fits data on edge of domain. Returns newmask. 
  newmask = 0
  masksize = inmask.shape[1]

  if topchop != 0:
      newmask = inmask[:,0:masksize-topchop] 
  if rightchop != 0:
      newmask = inmask[0:masksize-rightchop,:]
  if btmchop != 0:
      newmask = inmask[:,btmchop:]
  if leftchop != 0:
      newmask = inmask[leftchop:,:]

  return newmask

def makedBZcluster(refl,isCore,convsfmat,weakechothres,minsize,maxsize,startslope,shallowconvmin,truncZconvthres,ISO_CONV_FRINGE,WEAK_ECHO,ISO_CS_CORE,CS_CORE,dx):
  import numpy as np
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

  for i in range(0,numechoes):
    #Find 2D indices of echo object.
    (I,J) = (rain*(echoes==i+1)==1).nonzero()
    
    #Compute the total areal coverage of the echo object.
    clusterarea = (dx**2)*len(I)    #In km^2

    #Any echo object with a size between minsize and maxsize is considered 
    #ISOLATED CONVECTION. First, make all of it FRINGE.
    if clusterarea >= minsize and clusterarea <= maxsize:
      convsfmat[I,J] = ISO_CONV_FRINGE 

    #Very small echo objects are dismissed as WEAK ECHO.  
    if clusterarea < minsize:
      isCore[I,J] = 0
      convsfmat[I,J] = WEAK_ECHO
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
    isCore[refl >= truncvalue] = ISO_CS_CORE

    #But if reflectivity exceeds original reflectivity threshold, classify as CONVECTIVE core.
    isCore[refl >= truncZconvthres] = CS_CORE

  return (convsfmat,isCore)
