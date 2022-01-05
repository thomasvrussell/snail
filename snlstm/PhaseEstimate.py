import numpy as np
from snlstm.Predict import SNLSTM_Predict_Deep
from snlstm.utils.SpecFPCA import FPCA_Parameterize
from snlstm.utils.GPLightCurve import GP_Interpolator

class FitSingleSpecPhase:
    @staticmethod
    def FSSP(Wave_in, Flux_in, lstm_model, PATH_R, BadWaveMask_in=None, num_forward_pass=64, FAKE_MAPE_ERROR=0.2):
        # ** NOTE: this function only support a single spectrum as input.

        # ** verify inputs (standard wavelength and normalized flux)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        assert np.allclose(Wave_in, WAVE)
        assert np.allclose(np.mean(Flux_in), 1.0)

        # ** fpca parameterization
        FPCA_PARAM = FPCA_Parameterize(WAVE, Flux_in, PATH_R)

        # ** define auto-prediction function
        def auto_predict(phase_hypo):
            PredSpecDict = SNLSTM_Predict_Deep.SPD(FPCA_PARAM_o=FPCA_PARAM, phase_o=phase_hypo, \
                                                   FPCA_PARAM_t=FPCA_PARAM, phase_t=phase_hypo, \
                                                   phases_out=np.array([phase_hypo]), lstm_model=lstm_model, \
                                                   num_forward_pass=num_forward_pass)
            Flstm = PredSpecDict[phase_hypo]['flux']
            ape = 100.0*np.abs((Flux_in-Flstm)/np.clip(np.abs(Flux_in), a_min=1e-7, a_max=None))
            if BadWaveMask_in is None: mape = np.mean(ape)    # MAPE over all wavelength
            else: mape = np.mean(ape[~BadWaveMask_in])        # MAPE over valid wavelength
            return mape
        
        AutoDICT = {}
        # ** initial grid guess with 2 days resolution, phase in full range [-15.0, +33.0]
        PGuess1 = np.arange(-15.0, +33.01, 2.0)
        for phase_hypo in PGuess1:
            mape = auto_predict(phase_hypo)
            AutoDICT[phase_hypo] = mape

        # ** second grid guess with 0.5 days resolution, phase in narrow range: previous best +/- 4 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess2 = np.arange(max(_pbest-4.0, -15.0), min(_pbest+4.0, +33.0), 0.5)
        for phase_hypo in PGuess2:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
                
        # ** third grid guess with 0.1 days resolution, phase in narrow range: previous best +/- 1 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess3 = np.arange(max(_pbest-1.0, -15.0), min(_pbest+1.0, +33.0), 0.1)
        for phase_hypo in PGuess3:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
        
        # ** use GP to fit a smooth curve
        PHA_HP = np.array([phase_hypo for phase_hypo in AutoDICT])
        MAPE_HP = np.array([AutoDICT[phase_hypo] for phase_hypo in AutoDICT])
        SORT = np.argsort(PHA_HP)
        PHA_HP, MAPE_HP = PHA_HP[SORT], MAPE_HP[SORT]
        GPHA_HP = np.arange(-15.0, +33.01, 0.05)
        GMAPE_HP, eGMAPE_HP = GP_Interpolator(PHA_HP, MAPE_HP, np.nan*np.ones(len(MAPE_HP)), GPHA_HP, NaN_fill=FAKE_MAPE_ERROR)

        return PHA_HP, MAPE_HP, GPHA_HP, GMAPE_HP, eGMAPE_HP
