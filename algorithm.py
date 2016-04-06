from __future__ import division     #For python2 users only.

def convectivecore(background,refl,minZdiff,CS_CORE,ISO_CS_CORE,CONVECTIVE,STRATIFORM,UNCERTAIN,WEAK_ECHO,ISO_CONV_CORE,ISO_CONV_FRINGE,NO_SFC_ECHO,dBZformaxconvradius,maxConvRadius,weakechothres,deepcoszero,minsize,maxsize,startslope,shallowconvmin,truncZconvthres,dx):
   
  import numpy as np
  import rtfunctions as rt

  #Allocate isCore, a matrix that contains whether a grid point contains a convective core
  #and convsfmat, what will ultimately be the final rain-type classification.
  isCore = np.ones(background.shape)
  convsfmat = 10*np.ones((refl.shape),dtype=np.int)

  #Allocate zDiff, the variable representing the excess over the background dBZ
  #an echo must achieve to be considered a convective core.
  zDiff = np.empty(refl.shape)
  zDiff[:] = np.nan

  #Compute zDiff
  zDiff = 2.5 + minZdiff * (np.cos((np.pi)*background*0.5/deepcoszero))
  zDiff[(background < 0)] = minZdiff 

  #If reflectivity exceeds background dBZ by zDiff, then echo is convective core.
  isCore[(refl-background >= zDiff)] = CS_CORE;

  #No chance of weak echoes being convective cores.
  isCore[(refl < weakechothres)] = 0

  #Run the shallow, isolated convective core algorithm to detect small echoes that were
  #often identified as STRATIFORM by Steiner et al. (1995)
  (convsfmat,isCore) = rt.makedBZcluster(refl,isCore,convsfmat,weakechothres,minsize,maxsize,startslope,shallowconvmin,truncZconvthres,ISO_CONV_FRINGE,WEAK_ECHO,ISO_CS_CORE,CS_CORE,dx)
 
  #Make initial guesses of classifications. There may be some redundancy in this code,
  #later, but these operations are fast, I think. Better safe than sorry.
  convsfmat[(isCore == CS_CORE)] = CONVECTIVE
  convsfmat[(isCore == ISO_CS_CORE)] = ISO_CONV_CORE
  convsfmat[(isCore == 0)] = WEAK_ECHO
  convsfmat[(convsfmat == 10)] = STRATIFORM
  convsfmat[(np.isnan(refl) == True)] = NO_SFC_ECHO
  convsfmat[(refl < weakechothres)] = WEAK_ECHO

  #Now assign UNCERTAIN radius to each core. Currently assumes all echoes within 
  #maxConvRadius - 4 km are UNCERTAIN classification. Stronger echoes have larger 
  #uncertain radius. Uncertain radii of 6-10 km appear to be supported by algorithm 
  #testing on WRF output as seen in Powell et al. (2016). 

  #Compute what the uncertain radius is as a function of echo intensity.
  convRadiuskm = np.empty(refl.shape)
  convRadiuskm[:] = np.nan
  convRadiuskm[(background <= dBZformaxconvradius - 15 )] = maxConvRadius - 4
  convRadiuskm[(background > dBZformaxconvradius - 15 )] = maxConvRadius - 3 
  convRadiuskm[(background > dBZformaxconvradius - 10 )] = maxConvRadius - 2
  convRadiuskm[(background > dBZformaxconvradius - 5 )] = maxConvRadius - 1
  convRadiuskm[(background >= dBZformaxconvradius)] = maxConvRadius

  ##Assign UNCERTAIN classification to pixels near convective cores.

  #Create a mask, maskcell. Different indices for maskcell are for masks of different sizes.
  d = list(range(maxConvRadius-4,maxConvRadius+1))	#The 4 in this line assumes minimum radius in section above is 6 km.
  n = [int(np.round(x/dx)) for x in d]
  a = [2*x+1 for x in n]
  maskcell = [np.zeros([x,x]) for x in a]
  for k in range(0,len(d)):
    mask = np.zeros([int(2*n[k]+1),int(2*n[k]+1)])
    for i in range(-n[k],n[k]+1):
      for j in range(-n[k],n[k]+1):
        dm = np.sqrt((i*dx)**2 + (j*dx)**2)
        if dm <= d[k]:
          mask[i+n[k],j+n[k]] = 1
    maskcell[k] = mask  

  #Find 2D indices of convective cores.
  (I,J) = (isCore==CS_CORE).nonzero()

  #Allocate mask
  maskind = np.zeros((refl.shape),dtype=np.int)
  for k in range(0,len(I)):
    #dummy saves that result so far. Initialize as a bunch of zeroes.
    dummy = np.zeros((refl.shape),dtype=np.int)
 
    #Make mask for convective cores close to the edge of the domain
    nlow = n[int(convRadiuskm[I[k],J[k]]-6)]
    nhigh = refl.shape[0]-nlow-1      #This assumes domain is a square.
    Ilow = I[k]-nlow
    Ihigh = I[k]+nlow
    Jlow = J[k]-nlow
    Jhigh = J[k]+nlow
    
    #If the data point is close to any edge, then determine how much of the mask to cut off.
    if Ilow < 0 or Ihigh > refl.shape[0]-1 or Jlow < 0 or Jhigh > refl.shape[1]-1:
      if Ilow < 0:
        Ilow = 0
      if Jlow < 0:
        Jlow = 0
      if Ihigh > refl.shape[0]-1:
        Ihigh = refl.shape[0]-1
      if Jhigh > refl.shape[1]-1:
        Jhigh = refl.shape[1]-1
      leftchop = abs(I[k]-nlow-Ilow)
      rightchop = abs(I[k]+nlow-Ihigh)
      topchop = abs(J[k]-nlow-Jlow)
      btmchop = abs(J[k]+nlow-Jhigh)

      #Trim the mask. Return trimmed mask as dummy.
      if convRadiuskm[I[k],J[k]] == maxConvRadius - 4:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = rt.chopmask(maskcell[0],topchop,rightchop,btmchop,leftchop)
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 3:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = rt.chopmask(maskcell[1],topchop,rightchop,btmchop,leftchop)
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 2:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = rt.chopmask(maskcell[2],topchop,rightchop,btmchop,leftchop)
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 1:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = rt.chopmask(maskcell[3],topchop,rightchop,btmchop,leftchop)
      elif convRadiuskm[I[k],J[k]] == maxConvRadius:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = rt.chopmask(maskcell[4],topchop,rightchop,btmchop,leftchop)
    #If the data point isn't close to an edge, proceed normally, using maskcell as created above.
    else:
      if convRadiuskm[I[k],J[k]] == maxConvRadius - 4:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = maskcell[0]
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 3:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = maskcell[1]
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 2:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = maskcell[2]
      elif convRadiuskm[I[k],J[k]] == maxConvRadius - 1:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = maskcell[3]
      elif convRadiuskm[I[k],J[k]] == maxConvRadius:
        dummy[Ilow:Ihigh+1,Jlow:Jhigh+1] = maskcell[4]
    #At each data point, add dummy (which is 1 or 0) to maskind.
    maskind = np.add(maskind,dummy)

  #At this point, anything that isn't STRATIFORM is either CONVECTIVE, WEAK ECHO, or ISOLATED CONVECTIVE.
  #Make sure none of these echoes get classified as UNCERTAIN.
  maskind[convsfmat != STRATIFORM] = 0

  #Any point that was masked at least once is an echo of uncertain classification.
  convsfmat[maskind!=0] = UNCERTAIN

  #Change original convective cores back to convective.
  convsfmat[isCore == CS_CORE] = CONVECTIVE
  convsfmat[isCore == ISO_CS_CORE] = ISO_CONV_CORE

  #If there is no data, classify as NO SURFACE ECHO.
  convsfmat[np.isnan(refl)==1] = NO_SFC_ECHO
  
  #Classify WEAK_ECHO
  convsfmat[refl < weakechothres] = WEAK_ECHO

  #Format the output as integers.
  convsfmat.astype(int)

  return convsfmat
