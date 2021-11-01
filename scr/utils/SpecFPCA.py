import os
import numpy as np
import os.path as pa
from tempfile import mkdtemp
from astropy.table import Table

# * Load default FPCA Basis
HDIR = pa.join(pa.dirname(__file__), 'helper')
FPCA_DIR = pa.join(HDIR, 'fpca_basis')
BASIS_Lst, MEAN_Lst = [], []
for b in range(2):
    Ast_SEFunc = Table.read(FPCA_DIR + '/B%d_SoEfunc.csv' %b)
    B = [np.array([e for e in Ast_SEFunc[k]]) for k in range(len(Ast_SEFunc))]
    BASIS_Lst.append(B)
    Ast_SFM = Table.read(FPCA_DIR + '/B%d_SoFittedMean.csv' %b)
    MEAN_Lst.append(np.array(Ast_SFM['x']))

def FPCA_Parameterize(WAVE, FLUX, R_PATH):
    
    Dim = 90
    RCut0, RCut1 = 3800, 7200
    _WAVE = np.arange(RCut0, RCut1, 2)
    assert np.allclose(WAVE, _WAVE)
    assert np.allclose(np.mean(FLUX), 1.0)
    
    # * divide into two sections (blue & red)
    SECE = []
    for b in range(2):
        W = WAVE[850*b: 850*(b+1)]
        F = FLUX[850*b: 850*(b+1)]
        photcolor = np.mean(F)
        F = F - photcolor
        varcolor = np.std(F)
        F = F / varcolor
        SECE.append([photcolor, varcolor, W, F])
    
    # * place FPCA input in a temp-dir
    TDIR = mkdtemp(suffix=None, prefix='4fpca', dir=None)
    for b in range(2):
        WAV = SECE[b][2].copy()
        FL = SECE[b][3].copy()
        L = 1698
        WAV = WAV-(RCut0+1700*b)
        WAV = WAV/(L/0.998)
        WAV = WAV+0.001
        IDX = np.zeros(len(WAV)).astype(int)
        AST = Table([IDX, FL, WAV], names=['IDX', 'FL', 'WAV'])
        AST.write(TDIR + '/B%d_CataApply.csv' %b, format='ascii.csv', overwrite=True)
    
    # * run FPCA in R
    for b in range(2):
        command1 = 'cd %s/ && %s --slave --no-restore --file=B%d_FPCA_Application.R ' %(FPCA_DIR, R_PATH, b)
        command2 = '--args %s/B%d_CataApply.csv %s/B%d_ApplyScore.csv' %(TDIR, b, TDIR, b)
        os.system(command1 + command2)
    
    # * collect the parameters
    CArray = np.zeros((2, 2)).astype(float)
    for b in range(2):
        photcolor, varcolor = SECE[b][:2]
        CArray[b, 0] = photcolor
        CArray[b, 1] = varcolor
    
    ScoreArray = np.zeros((2, Dim)).astype(float)
    for b in range(2):
        ast = Table.read(TDIR + '/B%d_ApplyScore.csv' %b)
        for k in range(Dim): 
            ScoreArray[b, k] = ast['V%d' %(k+1)][0]
    
    FPCA_PARAM = np.concatenate((CArray, ScoreArray), axis=1)
    os.system('rm -rf %s' %TDIR)
    
    return FPCA_PARAM

def FPCA_Reconstruct(FPCA_PARAM):
        
    Dim = 90
    RCut0, RCut1 = 3800, 7200
    WRec, FRec = [], []
    for b in range(2):
        BASIS = BASIS_Lst[b].copy()
        MEAN = MEAN_Lst[b].copy()
        photcolor, varcolor = FPCA_PARAM[b, :2]
        scores = FPCA_PARAM[b, 2:]
        
        ReSpec = MEAN
        for i in range(Dim):
            ReSpec += scores[i] * BASIS[i]  
        ReSpec *= varcolor
        ReSpec += photcolor
        
        B0, B1 = RCut0+1700*b, RCut0+1700*(b+1)-2
        wav = np.linspace(B0, B1, 1001)
        WRec += list(wav)
        FRec += list(ReSpec)

    WRec = np.array(WRec)
    FRec = np.array(FRec)
    RecSpecDict = {'wavelength': WRec, 'flux': FRec}

    return RecSpecDict
