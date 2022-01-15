import os
import glob
import contextlib
import numpy as np
import os.path as pa
from astropy.table import Table

# * Load transmission curves of popular filters (Natural System)
#   (see ./helper/transmission_curves/*.txt)

TCDICT = {}
HDIR = pa.join(pa.dirname(__file__), 'helper')
for file in glob.glob(HDIR + '/transmission_curves/*.txt'):
    filtname = pa.basename(file)[:-4]
    ast = Table.read(file, format='ascii')
    lamb_T, T = np.array(ast['col1']).astype(float), np.array(ast['col2']).astype(float)   
    TCDICT[filtname] = (lamb_T, T)

# * Calculate Synthetic Photometry
#   NOTE: make sure that input spectrum fully covers the transmission curve.
def SynPhot(Wave, Flux, filtname, phot_system):
    import pyphot
    assert phot_system in ['Vega', 'AB']
    assert (filtname in ['B(Standard)', 'V(Standard)']) or (filtname in TCDICT)

    if filtname == 'B(Standard)':
        pypfilt = pyphot.get_library()['GROUND_JOHNSON_B']
    if filtname == 'V(Standard)':
        pypfilt = pyphot.get_library()['GROUND_JOHNSON_V']
    if filtname in TCDICT:
        lamb_T, T = TCDICT[filtname]
        pypfilt = pyphot.Filter(lamb_T, T, name=filtname, dtype='photon', unit='Angstrom')
    
    # NOTE pyphot v1.0: fluxes = pypfilt.get_flux(Wave*u.AA, Flux, axis=-1)
    # NOTE pyphot v1.1: fluxes = pypfilt.get_flux(Wave, Flux, axis=-1)
    #      [v1.1 is the current version at https://github.com/mfouesneau/pyphot]
    #      WARNING: Please install pyphot via git clone other than pip install.
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        fluxes = pypfilt.get_flux(Wave, Flux, axis=-1)
        if not isinstance(fluxes, float): fluxes = fluxes.value

    if phot_system == 'Vega': 
        mag_sphot = -2.5 * np.log10(fluxes) - pypfilt.Vega_zero_mag
    if phot_system == 'AB': 
        mag_sphot = -2.5 * np.log10(fluxes) - pypfilt.AB_zero_mag
    return mag_sphot

# * Calculate Synthetic B-V offset due to too narrow wavelength coverage using Hsiao's template
AstHsiao = Table.read(HDIR + '/HsiaoTemplate.csv', format='ascii.csv')
def Calculate_BmVoffset(phase, redshift, WaveRange, filtname_B, filtname_V, phot_system):

    # ** read the full template spectrum
    Asth = AstHsiao[AstHsiao['Phase'] == round(phase)]
    Wave_h = np.array(Asth['Wavelength']).astype(float)  # in rest-frame
    Flux_h = np.array(Asth['Flux']).astype(float)

    # ** make truncated version of template spectrum
    TruncMask = np.logical_and(Wave_h >= WaveRange[0], Wave_h <= WaveRange[1])
    Wave_th, Flux_th = Wave_h.copy(), Flux_h.copy()
    Flux_th[~TruncMask] = 0.0  # zero-padding 

    # ** synthetic-photometry on the full template [Lab-Frame]
    MAGB_h = SynPhot(Wave_h*(1+redshift), Flux_h, filtname_B, phot_system)
    MAGV_h = SynPhot(Wave_h*(1+redshift), Flux_h, filtname_V, phot_system)
    BmV_h = MAGB_h - MAGV_h

    # ** synthetic-photometry on truncated template [Lab-Frame]
    MAGB_th = SynPhot(Wave_th*(1+redshift), Flux_th, filtname_B, phot_system)
    MAGV_th = SynPhot(Wave_th*(1+redshift), Flux_th, filtname_V, phot_system)
    BmV_th = MAGB_th - MAGV_th
    BmVoffset = float(BmV_h - BmV_th)  # mag

    return BmVoffset
