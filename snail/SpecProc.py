import extinction
import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import least_squares
from scipy.interpolate import interp1d, splrep, splev
from snail.utils.SpecGSmooth import AutoGSmooth
from snail.utils.SyntheticPhot import SynPhot, Calculate_BmVoffset

class HomogenizeSpec:
    @staticmethod
    def HS(Wave_Raw, Flux_Raw, deredshift=True, redshift=None):

        # ** Define Standard Wavelength [3800, 3802, ..., 7198]
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        
        # ** Read Raw-Spec (sort wavelength)
        Wave, Flux = Wave_Raw.copy(), Flux_Raw.copy()
        WSORT = np.argsort(Wave)
        Wave, Flux = Wave[WSORT], Flux[WSORT]

        # ** Enter the rest-frame by deredshifting
        if deredshift: Wave /= (1.0+redshift)   # obs-frame to rest-frame
        else: print('WARNING: No deredshifting performed [make sure the raw spectrum already in rest-frame] !')
        
        if np.min(Wave) > RCut0 or np.max(Wave) < RCut1:
            print('ERROR: Spectrum in Rest-Frame [%.1f A - %.1f A] not fully covers ' %(np.min(Wave), np.max(Wave)) + \
                'the wavelength domain [%.1f A - %.1f A] required by our model !' %(RCut0, RCut1))
        
        # ** Spectrum trimming
        RangeMask = np.logical_and(Wave >= RCut0, Wave <= RCut1)
        tWave, tFlux = Wave[RangeMask], Flux[RangeMask]
        
        # * SG-Smooth in Log-Space (Then Back) with UpSampling
        window = 145    # 1000 km/s, np.log10(1+1000/300000)
        L = np.log10(tWave)
        LLog = np.arange(L.min(), L.max(), 0.00001)
        Lmodel = interp1d(L, tFlux, fill_value='extrapolate')
        stFlux = savgol_filter(Lmodel(LLog), window, 2)
        stWave = 10**LLog
        
        # * Resampling & Normalization
        model = interp1d(stWave, stFlux, fill_value='extrapolate')
        hFLUX = model(WAVE)
        hFLUX /= np.mean(hFLUX)
        
        HomoSpecDict = {'wavelength': WAVE, 'flux': hFLUX}  # in rest-frame

        return HomoSpecDict

class CorrectSpec:
    @staticmethod
    def CS(Wave_Homo, Flux_Homo, phase, redshift, \
        T7605=False, T6869=False, Halpha=False, Hbeta=False, \
        BmV_tar=None, filtname_B=None, filtname_V=None, phot_system=None):

        # ** verify inputs (standard wavelength and normalized flux)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        assert np.allclose(Wave_Homo, WAVE)
        assert np.allclose(np.mean(Flux_Homo), 1.0)
        hFLUX = Flux_Homo.copy()

        """
        # ************************** Remove Lines from the Spectrum ************************** #
        # i. Prominent Telluric Lines
        #    > Centred at 6869 [6845(-5) - 6915(+15)]
        #    > Centred at 7605 [7575 - 7680]
        # ii. Na-I D Lines
        #     > Centred at 5895.924 & 5889.950 [5870 - 5915]
        # iii. H_alpha & H_beta Lines
        #      > H_alpha: Centred at 6562.8 [6505(+10), 6635]  --- 6565
        #      > H_beta:  Centred at 4861.3 [4830(+15), 4895(-15)] --- 4861
        #
        """

        T7605_start, T7605_end = 7575, 7680  # in obs-frame
        T6869_start, T6869_end = 6840, 6930  # in obs-frame
        Ha_start, Ha_end = 6515-10, 6635+15  # in rest-frame, centred at 6562.8
        Hb_start, Hb_end = 4845, 4880        # in rest-frame, centred at 4861.3
        
        imFLUX = hFLUX.copy()
        GapMask = np.zeros(len(WAVE)).astype(bool)
        if T7605:
            w0, w1 = T7605_start/(1+redshift), T7605_end/(1+redshift)  # to rest-frame
            TAmask = np.logical_and(WAVE > w0, WAVE < w1)    
            GapMask[TAmask] = True
        if T6869:
            w0, w1 = T6869_start/(1+redshift), T6869_end/(1+redshift)  # to rest-frame
            TBmask = np.logical_and(WAVE > w0, WAVE < w1)
            GapMask[TBmask] = True
        if Halpha:
            Hamask = np.logical_and(WAVE > Ha_start, WAVE < Ha_end)
            GapMask[Hamask] = True
        if Hbeta:
            Hbmask = np.logical_and(WAVE > Hb_start, WAVE < Hb_end)
            GapMask[Hbmask] = True
        
        if np.sum(GapMask) > 0:
            # x. make auto-gaussian-smoothed spectrum (without spectrum variance here)
            # xx. remove data-points in these sections.
            # xxx. fill with 2-spline interpolation.
            
            smFLUX = AutoGSmooth(WAVE, hFLUX, None)
            m_spline = splrep(WAVE[~GapMask], smFLUX[~GapMask], w=None, k=2, s=None)
            spFLUX = splev(WAVE, m_spline)

            imFLUX[GapMask] = spFLUX[GapMask]   # UPDATE
            imFLUX /= np.mean(imFLUX)           # Re-Normalization

        # ************************** Perform Color Calibration ************************** #

        cFLUX = imFLUX.copy()
        if BmV_tar is not None:

            # ** Calculate B-V offset using Hsiao's template
            BmVoffset = Calculate_BmVoffset(phase, redshift, (RCut0, RCut1), filtname_B, filtname_V, phot_system)
            print('CheckPoint: Spectral SyntheticPhot B-V magnitude offset [%.3f mag]' %BmVoffset)
            
            # ** Define color calibration function by a structure-less extinction curve
            def func_cc(Wave, Flux, Ebv, Rv=3.1, normalize=True):
                ccFlux = Flux.copy()
                if Ebv is not None:
                    ExtRatio = 10**(extinction.ccm89(Wave.astype(float), Rv*Ebv, Rv)/-2.5)  # CCM89
                    ccFlux = Flux * ExtRatio    # apply extinction
                if normalize:
                    ccFlux = ccFlux / np.mean(ccFlux)  # Normalize
                return ccFlux
            
            def cmain(Ebv):
                # perform calibration with given Ebv
                if Ebv == 0.0: ccFLUX = imFLUX.copy()
                if Ebv != 0.0: ccFLUX = func_cc(WAVE, imFLUX, Ebv)    
                # zero padding in rest-frame
                PadWave = np.arange(1000, 10000, 2)
                PadFlux = np.zeros(len(PadWave)).astype(float)
                m = np.where(PadWave == RCut0)[0][0]
                n = np.where(PadWave == RCut1)[0][0]
                PadFlux[m: n] = ccFLUX
                # synthetic-photometry in obs-frame
                Bmag_sphot = SynPhot(PadWave*(1+redshift), PadFlux, filtname_B, phot_system)
                Vmag_sphot = SynPhot(PadWave*(1+redshift), PadFlux, filtname_V, phot_system)
                BmV_sphot = float(Bmag_sphot - Vmag_sphot)
                BmV_sphot += BmVoffset  # add offset
                return BmV_sphot
            
            costfunc = lambda Ebv: abs(cmain(Ebv) - BmV_tar)
            Ebv_fin = least_squares(costfunc, 0.0, bounds=([-1.0], [1.0])).x[0]
            cFLUX = func_cc(WAVE, imFLUX, Ebv_fin)
            print('CheckPoint: Spectral SyntheticPhot B-V magnitude [%.3f mag (input) >>> %.3f mag (output)]' \
                %(cmain(0.0), BmV_tar))
        
        CorrSpecDict = {'wavelength': WAVE, 'flux': cFLUX}  # in rest-frame

        return CorrSpecDict
