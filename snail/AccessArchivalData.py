import sys
import numpy as np 
import os.path as pa
from astropy.io import fits
from astropy.table import Table

class AccessDB:
    def __init__(self, SN_name, DBDir):

        # ** load master catalogs in the database directory
        self.DBDir = DBDir
        Astab_ObjMa = Table.read(self.DBDir + '/ObjectMaster.csv', format='ascii.csv')
        Astab_SpecMa = Table.read(self.DBDir + '/SpecMaster.csv', format='ascii.csv')

        if SN_name is not None:
            # ** in the scope of the given SN
            self.SN_name = SN_name
            self.ObjRow = Astab_ObjMa[Astab_ObjMa['SN_name'] == SN_name][0]
            AstSpecMa_SN = Astab_SpecMa[Astab_SpecMa['SN_name'] == SN_name]
            self.AstSpecMa_SN = AstSpecMa_SN[np.argsort(AstSpecMa_SN['Phase'])]  # sorted by phase
        else:
            print('WARNING: No specific SN given, show the list of SNe in CSD')
            for row in Astab_ObjMa:
                print('%s %s | z=%.6f NumSpec=%d' %(row['SN_name'], row['Subtype'], \
                    row['Redshift'], row['Num_Spec']))
        
    def SN_Attributes(self):
        
        SNA_DICT = {}
        SNA_DICT['SN_name'] = self.SN_name
        SNA_DICT['RA_J2000'] = self.ObjRow['RA_J2000']          # sky coordinate of the SN 
        SNA_DICT['DEC_J2000'] = self.ObjRow['DEC_J2000']        # ~ 
        
        SNA_DICT['Subtype'] = self.ObjRow['Subtype']            # subtype: Ia-norm, Ia-91T, Ia-99aa-like, Ia-91bg, Iax
        SNA_DICT['Redshift'] = self.ObjRow['Redshift']          # host galaxy redshift
        SNA_DICT['MJD_Bmax'] = self.ObjRow['MJD_Bmax']          # MJD time of B band maximum
        
        SNA_DICT['Subtype_ref'] = self.ObjRow['Subtype_ref']    # reference source of subtype
        SNA_DICT['Redshift_ref'] = self.ObjRow['Redshift_ref']  # reference source of redshift
        SNA_DICT['MJD_Bmax_ref'] = self.ObjRow['MJD_Bmax_ref']  # reference source of maximum time
        SNA_DICT['Num_Spec'] = self.ObjRow['Num_Spec']          # number of spectra in CSD dataset
        
        return SNA_DICT
    
    def Spec_Attributes(self, Spec_ID):
        
        SPECA_DICT = {}
        SpecRow = self.AstSpecMa_SN[self.AstSpecMa_SN['Spec_ID'] == Spec_ID][0]
        assert self.SN_name == SpecRow['SN_name']
        
        SPECA_DICT['Spec_ID'] = Spec_ID                                 # unique id for the spectrum
        SPECA_DICT['SN_name'] = self.SN_name                            # SN name
        SPECA_DICT['MJD_OBS'] = SpecRow['MJD_OBS']                      # observation MJD time of the spectrum
        SPECA_DICT['Phase'] = SpecRow['Phase']                          # phase of the spectrum w.r.t MJD_Bmax
        SPECA_DICT['Tel_Inst'] = SpecRow['Tel_Inst']                    # telescope/instrument which observed the spectrum
        
        # ** Remarks
        #    1. RawSpec_DeRedshifted_Type: this is a label to describe if the raw spectrum has already been deredshifted.
        #       > certainly yes ('Yes,VI', 'Yes,CSP'): The former means the deredshifted spectra identified through visual inspection, 
        #         while the latter are the spectra which were already deredshifted in CSP public release.
        #       > probably no ('YN,VI', 'YN,VIlowz'): It is hard to tell whether the raw spectrum has 
        #         already been deredshift or not by visual inspection.
        #       > certainly no ('No,VI', 'No,Cfa'): The former means the non-deredshifted spectra identified through visual inspection, 
        #         while the latter were identified since they come from Cfa public release. 
        #
        #       P.S. visual inspection process includes observing the position of telluric features and 
        #            comparsion with other spectra taken at near phases, etc.
        #
        #    2. RawSpec_Median_SNR: the median SNR level estimated from the raw spectrum. 
        #       WARNING: since we cannot find the original flux variance for every raw spectrum in our data set,
        #                here the SNR is directly measured from the raw spectrum other than from original variance column.
        #     
        #    3. HomoSpec_ColorCorrectness_Sigma: it is a metric between the photometric B-V magnitude and 
        #       the synthetic B-V color measured from the homogenized spectrum. using the formula 
        #       ccsig = abs(BV_syn - BV_phot) / eBV_phot (please see the paper for more details) 
        #
        #       P.S. the corrected spectra in CSD are color calibrated using photometric data.
        #            however, the color correctness of the corrected spectra is limited by the oversimplied correction method.
        #            we simply presume the color correctness is negatively correlated to ccsig. 
        #            if a homogenized spectrum has a large ccsig, its corrected spectrum 
        #            is probably not very reliable in its color. 

        SPECA_DICT['RawSpec_DeRedshifted_Type'] = SpecRow['RawSpec_DeRedshifted_Type']
        SPECA_DICT['RawSpec_Median_SNR'] = SpecRow['RawSpec_Median_SNR']    
        SPECA_DICT['HomoSpec_ColorCorrectness_Sigma'] = SpecRow['HomoSpec_ColorCorrectness_Sigma']
        SPECA_DICT['RawSpec_ref'] = SpecRow['RawSpec_ref']    # reference source of the raw spectrum
            
        return SPECA_DICT
        
    def Search_SpecID(self, PhaseRange=None, verbose=False):
        
        if PhaseRange is None:
            SID_LST = list(self.AstSpecMa_SN['Spec_ID'])
            if verbose:
                for sid in SID_LST:
                    SPECA_DICT = self.Spec_Attributes(Spec_ID=sid)
                    print('Spec ID : %d (Phase : %.2f d) (Tel / Inst : %s)' \
                        %(sid, SPECA_DICT['Phase'], SPECA_DICT['Tel_Inst']))

        else:
            pmin, pmax = PhaseRange
            Avmask = np.logical_and(self.AstSpecMa_SN['Phase'] >= pmin, \
                self.AstSpecMa_SN['Phase'] <= pmax)
            SID_LST = list(self.AstSpecMa_SN['Spec_ID'][Avmask])

            if verbose:
                for sid in SID_LST:
                    SPECA_DICT = self.Spec_Attributes(Spec_ID=sid)
                    print('Spec ID : %d (Phase : %.2f d) (Tel / Inst : %s)' \
                        %(sid, SPECA_DICT['Phase'], SPECA_DICT['Tel_Inst']))
        
        return SID_LST
        
    def Retrieve_BVphot(self):
        
        # ** Remarks
        #    1. 'B(Bessell, CT)' & 'V(Bessell, CT)' indicate photometry in standard system from color-term correction.
        #    2. 'B(Bessell, Scorr)' & 'V(Bessell, Scorr)' indicate photometry in standard system from S-correction.
        #    3. others (e.g., 'B(kait2)') indicate photometry in natural systems.
        
        AstBVp_SN = None
        MDIR_BVp = pa.join(self.DBDir, 'BVPhotometry')
        assert pa.exists(MDIR_BVp)    # make sure that the phot dataset exists
        
        CSV_BVp = pa.join(MDIR_BVp, '%s.BVphot.csv' %self.SN_name)
        if pa.exists(CSV_BVp):
            AstBVp_SN = Table.read(CSV_BVp, format='ascii.csv')

            # ** present information about photometry systems
            HDIR = pa.join(pa.dirname(__file__), 'utils', 'helper')
            pba, pbb = list(set(AstBVp_SN['Passband']))
            if pba[0] == 'B': passband_B, passband_V = pba, pbb
            else: passband_B, passband_V = pbb, pba
            if passband_B == 'B(Bessell, CT)':
                print('>>> B band: standard system with color-term correction')
            elif passband_B == 'B(Bessell, Scorr)':
                print('>>> B band: standard system with S-correction')
            else: 
                print('>>> B band: natural system with filter %s' %passband_B)
                print('    (find transmission curves at %s/transmission_curves/%s.txt)' \
                    %(HDIR, passband_B))
            if passband_V == 'V(Bessell, CT)':
                print('>>> V band: standard system with color-term correction')
            elif passband_V == 'V(Bessell, Scorr)':
                print('>>> V band: standard system with S-correction')
            else: 
                print('>>> V band: natural system with filter %s' %passband_V)
                print('    (find transmission curves at %s/transmission_curves/%s.txt)' \
                    %(HDIR, passband_V))
        
        return AstBVp_SN
    
    def Retrieve_SpecObs(self, Spec_ID, data_type, deredshift_rawspec=True):
        
        assert Spec_ID in list(self.AstSpecMa_SN['Spec_ID'])
        assert data_type in ['Raw', 'Homogenized', 'Corrected']
        MDIR_SO = pa.join(self.DBDir, 'Observations')
        assert pa.exists(MDIR_SO)    # make sure that the spec-obs dataset exists

        if data_type == 'Raw':
            RawSpecFile = pa.join(MDIR_SO, 'Raw', '%d.%s.ascii' %(Spec_ID, self.SN_name))
            assert pa.exists(RawSpecFile)
            AstSpec = Table.read(RawSpecFile, format='ascii.csv')  # 'wavelength', 'flux'
            SPECA_DICT = self.Spec_Attributes(Spec_ID=Spec_ID)
            DRT = SPECA_DICT['RawSpec_DeRedshifted_Type']
            
            if deredshift_rawspec:
                print('WARNING: You are forcing the raw spectrum into the rest frame !')    
                if DRT in ['Yes,VI', 'Yes,CSP']:
                    print('WARNING: DeRedshifting SKIP (since the Raw spectrum has already been dereshifted) !')
                if DRT in ['No,VI', 'No,Cfa', 'YN,VI', 'YN,VIlowz']:
                    z = self.SN_Attributes()['Redshift']
                    AstSpec['wavelength'] = AstSpec['wavelength'] / (1.0+z)   # UPDATE
                    print('WARNING: DeRedshifting DONE (the column of wavelength updated) !')
            else:
                if DRT in ['Yes,VI', 'Yes,CSP']:
                    print('WARNING: The returned Raw spectrum is already in rest-frame as it is !')
                if DRT in ['No,VI', 'No,Cfa']:
                    print('WARNING: The returned Raw spectrum is in observer-frame as it is !')
                if DRT in ['YN,VI', 'YN,VIlowz']:
                    print('WARNING: The returned Raw spectrum is probably (not for sure) in observer-frame as it is !')
                print('WARNING: No DeRedshifting performed on the Raw spectrum !')
        
        if data_type == 'Homogenized':
            HomoSpecFile = pa.join(MDIR_SO, 'Homogenized', '%d.%s.st.ascii' %(Spec_ID, self.SN_name))
            assert pa.exists(HomoSpecFile)
            AstSpec = Table.read(HomoSpecFile, format='ascii.csv')  # 'RFwavelength', 'flux'
            AstSpec['RFwavelength'].name = 'wavelength'  
        
        if data_type == 'Corrected':
            CorrSpecFile = pa.join(MDIR_SO, 'Corrected', '%d.%s.stcal.ascii' %(Spec_ID, self.SN_name))
            assert pa.exists(CorrSpecFile)
            AstSpec = Table.read(CorrSpecFile, format='ascii.csv')  # 'RFwavelength', 'flux'
            AstSpec['RFwavelength'].name = 'wavelength'

        return AstSpec
    
    def Retrieve_SpecTemplate(self, evaluate_accuracy=False):
        
        # ** define template phase & wavelength resolution
        OpPcadence = 1/8.0
        OpPrange = (-15.00, 33.01)
        OpPHA = np.arange(OpPrange[0], OpPrange[1], OpPcadence)
        RCut0, RCut1 = 3800, 7200
        WAVE = np.arange(RCut0, RCut1, 2)
        
        MDIR_ST = pa.join(self.DBDir, 'Templates')
        assert pa.exists(MDIR_ST)   # make sure that the spec-temp dataset exists
        
        FITS_TEMP = pa.join(MDIR_ST, 'ESurface-%s.fits' %self.SN_name)
        LstmData = fits.getdata(FITS_TEMP, ext=0).T

        COL0, COL1, COL2, COL3 = [], [], [], []
        for idx, phase in enumerate(OpPHA):
            COL0 += [idx]*len(WAVE)
            COL1 += [phase]*len(WAVE)
            COL2 += list(WAVE)
            COL3 += list(LstmData[idx, :])
        AstSpec = Table([COL0, COL1, COL2, COL3], names=['index', 'phase', 'wavelength', 'flux'])

        if evaluate_accuracy:
            CSV_TRec = pa.join(MDIR_ST, 'TrainingRecord.csv')
            AstTRec = Table.read(CSV_TRec, format='ascii.csv')
            AstTRec_SN = AstTRec[AstTRec['SN_name'] == self.SN_name]
            AstTRec_SN = AstTRec_SN[np.argsort(AstTRec_SN['Phase'])]
            print('SN name | Obs. Spec_ID | Obs. Phase | Trained | Template MAPE error')
            for line in AstTRec_SN:
                # ** retreive observation data (corrected)
                Fobs = np.array(self.Retrieve_SpecObs(Spec_ID=line['Spec_ID'], data_type='Corrected')['flux'])
                # ** extract template data at nearest phase
                Ftemp = LstmData[np.argmin(np.abs(OpPHA - line['Phase'])), :]
                # ** calculate mape error
                ape = np.abs((Fobs - Ftemp) / np.clip(np.abs(Fobs), a_min=1e-7, a_max=None))
                mape = 100.0 * np.mean(ape, axis=-1)
                print('[%s] | %d | %.1f d | %s | %.1f %%' \
                    %(self.SN_name, line['Spec_ID'], line['Phase'], line['Training'], mape))
        
        return AstSpec
