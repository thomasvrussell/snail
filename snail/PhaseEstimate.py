import numpy as np
from snail.Predict import SNAIL_Predict_Deep
from snail.utils.SpecFPCA import FPCA_Parameterize
from snail.utils.GPLightCurve import GP_Interpolator

class FitSingleSpecPhase:
    @staticmethod
    def FSSP(Wave_in, Flux_in, lstm_model, PATH_R, BadWaveMask_in=None, num_forward_pass=64, FAKE_MAPE_ERROR=0.2):
        # **** this function only support a single spectrum as input **** #

        # ** verify inputs (standard wavelength and normalized flux)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        assert np.allclose(Wave_in, WAVE)
        assert np.allclose(np.mean(Flux_in), 1.0)

        # ** fpca parameterization
        FPCA_PARAM = FPCA_Parameterize(WAVE, Flux_in, PATH_R)

        # ** define auto-prediction function
        def auto_predict(phase_hypo):
            PredSpecDict = SNAIL_Predict_Deep.SPD(FPCA_PARAM_o=FPCA_PARAM, phase_o=phase_hypo, \
                                                   FPCA_PARAM_t=FPCA_PARAM, phase_t=phase_hypo, \
                                                   phases_out=np.array([phase_hypo]), lstm_model=lstm_model, \
                                                   num_forward_pass=num_forward_pass)
            Flstm = PredSpecDict[phase_hypo]['flux']
            ape = 100.0*np.abs((Flux_in-Flstm)/np.clip(np.abs(Flux_in), a_min=1e-7, a_max=None))
            if BadWaveMask_in is None: mape = np.mean(ape)    # MAPE over all wavelength
            else: mape = np.mean(ape[~BadWaveMask_in])        # MAPE over valid wavelength
            return mape
        
        # ** define a modified np.arange always including the endpoint
        def myrange(start, stop, step, rtol=1e-05, atol=0.001):
            # NOTE: a evenly separated sequence (except the last interval) always including endpoint
            #       default atol is 0.001 day ~ 1.4 min.
            SEQ = np.arange(start, stop, step)
            if not np.isclose(SEQ[-1], stop, rtol=rtol, atol=atol):
                """
                # criterion of np.isclose:
                # absolute(`a` - `b`) <= (`atol` + `rtol` * absolute(`b`))
                """
                SEQ = np.append(SEQ, stop)
            return SEQ        

        AutoDICT = {}
        PLBound, PUBound = -15.0, +33.0
        # ** initial grid guess with 2 days resolution, phase in full range [-15.0, +33.0]
        PGuess1 = myrange(PLBound, PUBound, 2.0)
        for phase_hypo in PGuess1:
            mape = auto_predict(phase_hypo)
            AutoDICT[phase_hypo] = mape

        # ** second grid guess with 0.5 days resolution, phase in narrow range: previous best +/- 4 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess2 = myrange(max(_pbest-4.0, PLBound), min(_pbest+4.0, PUBound), 0.5)
        for phase_hypo in PGuess2:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
                
        # ** third grid guess with 0.1 days resolution, phase in narrow range: previous best +/- 1 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess3 = myrange(max(_pbest-1.0, PLBound), min(_pbest+1.0, PUBound), 0.1)
        for phase_hypo in PGuess3:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
        
        # ** leverage GP to fit a smooth curve
        PHA_HP = np.array([phase_hypo for phase_hypo in AutoDICT])
        MAPE_HP = np.array([AutoDICT[phase_hypo] for phase_hypo in AutoDICT])
        SORT = np.argsort(PHA_HP)
        PHA_HP, MAPE_HP = PHA_HP[SORT], MAPE_HP[SORT]
        GPHA_HP = np.arange(PLBound, PUBound, 0.05)
        GMAPE_HP, eGMAPE_HP = GP_Interpolator(PHA_HP, MAPE_HP, \
            np.nan*np.ones(len(MAPE_HP)), GPHA_HP, NaN_fill=FAKE_MAPE_ERROR)

        return PHA_HP, MAPE_HP, GPHA_HP, GMAPE_HP, eGMAPE_HP


class FitDoubleSpecPhase:
    @staticmethod
    def FDSP(Wave_in1, Flux_in1, Wave_in2, Flux_in2, delta_phase, lstm_model, PATH_R, \
        BadWaveMask_in1=None, BadWaveMask_in2=None, num_forward_pass=64, FAKE_MAPE_ERROR=0.2):
        # **** this function support a pair of phase-unknown spectra as input (with certain delta phase) **** #

        # ** verify inputs (standard wavelength and normalized flux)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        assert np.allclose(Wave_in1, WAVE)
        assert np.allclose(Wave_in2, WAVE)
        assert np.allclose(np.mean(Flux_in1), 1.0)
        assert np.allclose(np.mean(Flux_in2), 1.0)

        # ** fpca parameterizations
        FPCA_PARAM_o = FPCA_Parameterize(WAVE, Flux_in1, PATH_R)
        FPCA_PARAM_t = FPCA_Parameterize(WAVE, Flux_in2, PATH_R)

        # ** define auto-prediction function
        #    NOTE: In our convention, phase_hypo is the hypothesized phase of the first spectrum.
        def auto_predict(phase_hypo):
            phase_o, phase_t = phase_hypo, phase_hypo + delta_phase
            PredSpecDict = SNAIL_Predict_Deep.SPD(FPCA_PARAM_o=FPCA_PARAM_o, phase_o=phase_o, \
                                                FPCA_PARAM_t=FPCA_PARAM_t, phase_t=phase_t, \
                                                phases_out=np.array([phase_o, phase_t]), \
                                                lstm_model=lstm_model, num_forward_pass=num_forward_pass)
            mape = []
            for phase, Flux_in, BadWaveMask_in in zip([phase_o, phase_t], \
                [Flux_in1, Flux_in2], [BadWaveMask_in1, BadWaveMask_in2]):
                Flstm = PredSpecDict[phase]['flux']
                _ape = 100.0*np.abs((Flux_in-Flstm)/np.clip(np.abs(Flux_in), a_min=1e-7, a_max=None))
                if BadWaveMask_in is None: _mape = np.mean(_ape)    # MAPE over all wavelength
                else: _mape = np.mean(_ape[~BadWaveMask_in])        # MAPE over valid wavelength
                mape.append(_mape)
            mape = np.mean(mape)     # NOTE use the average
            return mape
        
        # ** define a modified np.arange always including the endpoint
        def myrange(start, stop, step, rtol=1e-05, atol=0.001):
            # NOTE: a evenly separated sequence (except the last interval) always including endpoint
            #       default atol is 0.001 day ~ 1.4 min.
            SEQ = np.arange(start, stop, step)
            if not np.isclose(SEQ[-1], stop, rtol=rtol, atol=atol):
                """
                # criterion of np.isclose:
                # absolute(`a` - `b`) <= (`atol` + `rtol` * absolute(`b`))
                """
                SEQ = np.append(SEQ, stop)
            return SEQ        

        AutoDICT = {}
        PLBound, PUBound = -15.0, 33.01-delta_phase
        # ** initial grid guess with 2 days resolution, phase in full range [-15.0, +33.0-delta_phase]
        PGuess1 = myrange(PLBound, PUBound, 2.0)
        for phase_hypo in PGuess1:
            mape = auto_predict(phase_hypo)
            AutoDICT[phase_hypo] = mape

        # ** second grid guess with 0.5 days resolution, phase in narrow range: previous best +/- 4 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess2 = myrange(max(_pbest-4.0, PLBound), min(_pbest+4.0, PUBound), 0.5)
        for phase_hypo in PGuess2:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
                
        # ** third grid guess with 0.1 days resolution, phase in narrow range: previous best +/- 1 days
        _pbest = min(AutoDICT, key=AutoDICT.get)
        PGuess3 = myrange(max(_pbest-1.0, PLBound), min(_pbest+1.0, PUBound), 0.1)
        for phase_hypo in PGuess3:
            if phase_hypo not in AutoDICT:
                mape = auto_predict(phase_hypo)
                AutoDICT[phase_hypo] = mape
        
        # ** leverage GP to fit a smooth curve
        PHA_HP = np.array([phase_hypo for phase_hypo in AutoDICT])
        MAPE_HP = np.array([AutoDICT[phase_hypo] for phase_hypo in AutoDICT])
        SORT = np.argsort(PHA_HP)
        PHA_HP, MAPE_HP = PHA_HP[SORT], MAPE_HP[SORT]
        GPHA_HP = np.arange(PLBound, PUBound, 0.05)
        GMAPE_HP, eGMAPE_HP = GP_Interpolator(PHA_HP, MAPE_HP, \
            np.nan*np.ones(len(MAPE_HP)), GPHA_HP, NaN_fill=FAKE_MAPE_ERROR)

        return PHA_HP, MAPE_HP, GPHA_HP, GMAPE_HP, eGMAPE_HP
