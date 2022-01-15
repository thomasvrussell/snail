import numpy as np
from scipy.interpolate import interp1d
from snail.utils.SpecFPCA import FPCA_Parameterize, FPCA_Reconstruct

class SNAIL_Predict_Deep:
    @staticmethod
    def SPD(FPCA_PARAM_o, phase_o, FPCA_PARAM_t, phase_t, phases_out, lstm_model, num_forward_pass=64):

        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)

        # ** construct LSTM input
        XDATA = []
        #phase_o, phase_t = phase_in1, phase_in2
        cff_o = np.array(FPCA_PARAM_o).flatten()
        cff_t = np.array(FPCA_PARAM_t).flatten()
        for phase_d in phases_out:
            xd = np.array([[phase_d, phase_o] + list(cff_o), \
                           [phase_d, phase_t] + list(cff_t)])
            XDATA.append(xd)
        XDATA = np.array(XDATA)
    
        # ** perform LSTM prediction
        def walkthrough():
            YDATA = lstm_model.predict(XDATA)
            #*#*#*# + Adjust form [back to single-layer] #*#*#*#
            YDATA = np.array([np.mean(YDATA[k], axis=0) for k in range(YDATA.shape[0])])

            Surface = []
            for i, phase_d in enumerate(phases_out):
                cff_pred = YDATA[i]
                cf_pred = cff_pred.reshape((2, -1))
                RecSpecDict = FPCA_Reconstruct(FPCA_PARAM=cf_pred)
                WReC_pred, FReC_pred = RecSpecDict['wavelength'], RecSpecDict['flux']
                imodel = interp1d(WReC_pred, FReC_pred, fill_value='extrapolate')
                F_pred = imodel(WAVE)               # NOTE resampling on wavelength
                FLUX_pred = F_pred / np.mean(F_pred)     # NOTE Normalization [subtle change expected]
                Surface.append(FLUX_pred)
            Surface = np.array(Surface)
            return Surface
    
        SurfacePile = []
        for _idx in range(num_forward_pass):
            Surface = walkthrough() 
            SurfacePile.append(Surface)
        SurfacePile = np.array(SurfacePile)
        
        ESurface = np.mean(SurfacePile, axis=0)
        VSurface = np.var(SurfacePile, axis=0)
        
        PredSpecDict = {}
        for idx, phase_d in enumerate(phases_out):
            PredSpecDict[phase_d] = {'wavelength': WAVE, \
                                     'flux': ESurface[idx], \
                                     'fluxerr': np.sqrt(VSurface[idx])}

        return PredSpecDict

class SNAIL_Predict:
    @staticmethod
    def SLP(Wave_in1, Flux_in1, phase_in1, Wave_in2, Flux_in2, phase_in2, \
        phases_out, lstm_model, PATH_R, num_forward_pass=64):

        # ** verify inputs (standard wavelength and normalized flux)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        assert np.allclose(Wave_in1, WAVE)
        assert np.allclose(Wave_in2, WAVE)
        assert np.allclose(np.mean(Flux_in1), 1.0)
        assert np.allclose(np.mean(Flux_in2), 1.0)
        assert phase_in1 <= phase_in2
        assert isinstance(phases_out, np.ndarray)
        FLUX_o, FLUX_t = Flux_in1.copy(), Flux_in2.copy()

        # ** fpca parameterization
        FPCA_PARAM_o = FPCA_Parameterize(WAVE, FLUX_o, PATH_R)
        if np.sum(~np.equal(FLUX_o, FLUX_t)) > 0:
            FPCA_PARAM_t = FPCA_Parameterize(WAVE, FLUX_t, PATH_R)
        else: FPCA_PARAM_t = FPCA_PARAM_o.copy()

        # ** predict
        PredSpecDict = SNAIL_Predict_Deep.SPD(FPCA_PARAM_o=FPCA_PARAM_o, phase_o=phase_in1, \
                                               FPCA_PARAM_t=FPCA_PARAM_t, phase_t=phase_in2, \
                                               phases_out=phases_out, lstm_model=lstm_model, \
                                               num_forward_pass=num_forward_pass)
        
        return PredSpecDict
