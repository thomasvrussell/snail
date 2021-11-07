import numpy as np
from snlstm.Predict import SNLSTM_Predict
from snlstm.utils.GPLightCurve import GP_Interpolator

class FitSingleSpecPhase:
    @staticmethod
    def FSSP(Wave_in, Flux_in, lstm_model, PATH_R, num_forward_pass=64, FAKE_MAPE_ERROR=0.2):
        # ** NOTE: this function only support a single spectrum as input.

        def auto_predict(phase_hypo):
            PredSpecDict = SNLSTM_Predict.SLP(Wave_in1=Wave_in, Flux_in1=Flux_in, phase_in1=phase_hypo, \
                Wave_in2=Wave_in, Flux_in2=Flux_in, phase_in2=phase_hypo, phases_out=np.array([phase_hypo]), \
                lstm_model=lstm_model, PATH_R=PATH_R, num_forward_pass=num_forward_pass)
            Flstm = PredSpecDict[phase_hypo]['flux']
            mape = 100.0*np.mean(np.abs((Flux_in-Flstm)/np.clip(np.abs(Flux_in), a_min=1e-7, a_max=None)), axis=-1)
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
