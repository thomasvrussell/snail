import numpy as np
from math import sqrt, pi
# NOTE: these are functions copied from Kaepora.

def GSmooth(Wave, Flux, varFlux=None, vexp=0.002, nsig=5.0):

    # NOTE: Kaepora Function gsmooth is an inverse variance weighted Gaussian smoothing of spectra
    #       Optional inputs are smoothing velocity (vexp) and number of sigma (nsig)

    # ** Check for zero variance points, and set to 1E-31
    if varFlux is None: varFlux = 1.e-31*np.ones(len(Flux))
    
    # ** Loop over Flux elements
    newFlux = np.zeros(len(Wave)).astype(float)
    for i in range(len(Wave)):
        
        # *** Construct a Gaussian of sigma = vexp*Wave[i]
        gaussian = np.zeros(len(Wave), float)
        sigma = vexp*Wave[i]
        
        # *** Restrict range to +/- nsig sigma
        sigrange = np.nonzero(abs(Wave-Wave[i]) <= nsig*sigma)
        gaussian[sigrange] = (1/(sigma*sqrt(2*pi)))*np.exp(-0.5*((Wave[sigrange]-Wave[i])/sigma)**2)
        
        # *** Multiply Gaussian by 1 / variance
        W_lambda = gaussian / varFlux
        
        # *** Perform a weighted sum to give smoothed y value at Wave[i]
        W0 = np.sum(W_lambda)
        W1 = np.sum(W_lambda*Flux)
        newFlux[i] = W1/W0

    return newFlux

def AutoGSmooth(Wave, Flux, varFlux=None, nsig=5.0):

    # NOTE There is an preliminary operation (eliminated here) called 'clip' before performing gsmooth,
    #      which is designed for interpolating over unwanted cosmic rays and emission lines.

    # ** Automatically determine vexp
    newFlux_init = GSmooth(Wave, Flux, varFlux, vexp=0.002, nsig=5.0)  # this smoothing should get in right ballpark
    if varFlux is not None:
        Error = np.sqrt(varFlux)
        mSNR = np.median(newFlux_init / Error)
    else:
        Error = np.absolute(Flux - newFlux_init)
        smError = GSmooth(Wave, Error, varFlux, vexp=0.008, nsig=5.0)
        mSNR = np.median(newFlux_init / smError)

    # TODO (Kaepora): interpolate a function of mSNR
    # vexp_line = np.polyfit([2.5, 80], [.0045, .001], 1)
    # coeff_0 = vexp_line[0]
    # coeff_1 = vexp_line[1]
    # results from above:
    coeff_0 = -4.51612903e-05
    coeff_1 = 4.61290323e-03
    vexp_auto = coeff_0*mSNR + coeff_1
    
    if mSNR < 2.5: vexp_auto = .0045
    if mSNR > 80: vexp_auto = .001

    # ** Run GaussianSmooth with vexp_auto
    newFlux = GSmooth(Wave, Flux, varFlux, vexp=vexp_auto, nsig=nsig)

    return newFlux
