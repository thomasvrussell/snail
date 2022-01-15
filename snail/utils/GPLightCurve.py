import warnings
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as CK

def GP_Interpolator(X, Y, eY, X_q, NaN_fill=0.1):
    # * nan-correction
    Avmask = ~np.isnan(Y)
    X, Y, eY = X[Avmask], Y[Avmask], eY[Avmask]
    eY[np.isnan(eY)] = NaN_fill
    
    # * set GP configuration
    #   RBF: Radial-basis function kernel (aka squared-exponential kernel)
    #   k(x, x') = σ^2 * exp(- (x - x')^2 / 2*l^2)
    #   hyperparameters: σ (sigma) & l (length-scale)
    
    sig2 = 1.0
    length_scale = 10.0
    kernel = CK(sig2, (1e-3, 1e3)) * RBF(length_scale, (1e-2, 1e2))   # A very common configuration
    gp = GaussianProcessRegressor(kernel=kernel, alpha=eY**2, n_restarts_optimizer=10)
    
    # * fit to data by Maximum Likelihood Estimation
    X = np.atleast_2d(X).T
    gp.fit(X, Y)
    
    # * run prediction
    X_q = np.atleast_2d(X_q).T
    Y_q, eY_q = gp.predict(X_q, return_std=True)
    
    return Y_q, eY_q

def PhotGP(MJD_in, MAG_in, eMAG_in, MJD_Bmax, redshift, Phases_out):

    X_in = (MJD_in - MJD_Bmax) / (1+redshift)  # convert time to phase
    Y_in, eY_in = MAG_in.copy(), eMAG_in.copy()
    
    if np.sum(np.isnan(eMAG_in)) > 0:
        print('WARNING: Invalid MagErr Found, Simply Use 0.1 mag instead !')
        eY_in[np.isnan(eY_in)] = 0.1  # fill hypothesis magerr 0.1 mag
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        print('CheckPoint: Input Photometry [%.1fd - %.1fd] with [%d] datapoints' \
            %(np.min(X_in), np.max(X_in), len(X_in)))
        Y_out, eY_out = GP_Interpolator(X=X_in, Y=Y_in, eY=eY_in, X_q=Phases_out)
        MAG_out, eMAG_out = Y_out, eY_out
    
    return MAG_out, eMAG_out

def PhotBVColor(MJD_B, MAG_B, eMAG_B, MJD_V, MAG_V, eMAG_V, MJD_Bmax, redshift, Phases_out):
    
    MAG_GP_B, eMAG_GP_B = PhotGP(MJD_B, MAG_B, eMAG_B, MJD_Bmax, redshift, Phases_out)
    MAG_GP_V, eMAG_GP_V = PhotGP(MJD_V, MAG_V, eMAG_V, MJD_Bmax, redshift, Phases_out)
    MAG_GP_BmV = MAG_GP_B - MAG_GP_V
    eMAG_GP_BmV = np.sqrt(eMAG_GP_B**2 + eMAG_GP_V**2)
    
    return MAG_GP_BmV, eMAG_GP_BmV
