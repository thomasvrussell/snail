SuperNova Artificial Inference by Lstm neural networks (SNAIL)
=============================

Package Description
-------------------

The difficulties in acquiring spectroscopic data have been a major challenge for supernova surveys. SNAIL is developed to provide a data-driven solution. Based on an observation dataset including 3091 spectra from 361 individual SNe Ia, we trained LSTM neural networks to learn from the spectroscopic time-series data of type Ia supernovae. The model enables the construction of spectral sequences from spectroscopic observations with limited time coverage.

This repository is associated to the paper "*Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2022, ApJ)*".

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.5637790.svg
    :target: https://doi.org/10.5281/zenodo.5637790
.. image:: https://img.shields.io/badge/License-MIT-red.svg
    :target: https://opensource.org/licenses/MIT
.. image:: https://img.shields.io/badge/python-3.7-green.svg
    :target: https://www.python.org/downloads/release/python-370/

Installation
-----------
One can install any desired version of SNAIL from Github `<https://github.com/thomasvrussell/snail>`_: ::

    python setup.py install

Additional dependencies
-----------

- `R <https://www.r-project.org>`_ : In order to reduce the data dimension, we use Functional Principal Component Analysis (FPCA) to parameterize supernova spectra before feeding them into neural networks. The FPCA parameterization and FPCA reconstruction are achieved by the `fpca <https://CRAN.R-project.org/package=fpca>`_ package in R programming language. One can install them, e.g., on CentOS ::

    $ yum install R
    R > install.packages("fpca")

- `TensorFlow <https://github.com/tensorflow/tensorflow>`_ : tensorflow is required to load a given LSTM model and make the spectral predictions. The default LSTM model in this repository is trained on an enviornment with tensorflow 1.14.0. To avoid potential incompatiability issues casued by different tensorflow versions, we recommend users to install the same version via Conda ::

    conda install -c anaconda tensorflow=1.14.0

- `PYPHOT <https://github.com/mfouesneau/pyphot>`_ (optional) : pyphot is a portable package to compute synthetic photometry of a spectrum with given filter. In our work, the tool was used to correct the continuum component of a supernova spectrum so that its synthetic photometry could be in line with the observed light curves. One may consider to install the package if such color calibration is necessary. We recommend users to install the latest version from Github (pyphot 1.1) ::

    pip install git+https://github.com/mfouesneau/pyphot

Download archival datasets
-----------

SNAIL allows users to access to the following archival datasets 

.. [#] **A spectral-observation dataset** : it is comprised of 3091 observed spectra from 361 SNe Ia, largely contributed from CfA (Blondin et al. 2012), BSNIP (Silverman et al. 2012), CSP (Folatelli et al. 2013) and Supernova Polarimetry Program (Wang & Wheeler 2008; Cikota et al. 2019a; Yang et al. 2020).

.. [#] **A spectral-template dataset** : it includes 361 spectral templates, each of them (covering -15 to +33d with wavelength from 3800 to 7200 A) was generated from the available spectroscopic observations of an individual SN via a LSTM neural network model.

.. [#] **An auxiliary photometry dataset** : it provides the B & V light curves of these SNe (in total, 196 available), that were used to calibrate the synthetic B-V color of the observed spectra.

These datasets are stored on `Zenodo <https://zenodo.org>`_ platform, one can download the related files (~ 2GB) through the Zenodo page: `<https://doi.org/10.5281/zenodo.5637790>`_.

Quick start guide
-----------

We prepared several jupyter notebooks as quick tutorials to use our package in a friendly way.

.. [*] `1-Access_to_Archival_ObservationData.ipynb <https://github.com/thomasvrussell/snail/blob/main/notebooks/1-Access_to_Archival_ObservationData.ipynb>`_ : this notebook is to show how to access to the **spectral-observation dataset** and **the auxiliary photometry dataset**.  

.. [*] `2-Access_to_Archival_TemplateData.ipynb <https://github.com/thomasvrussell/snail/blob/main/notebooks/2-Access_to_Archival_TemplateData.ipynb>`_ : one can obtain the LSTM generated spectral time sequences in **the spectral-template dataset** following this notebook.

.. [*] `3-SpecData_Process_Example.ipynb <https://github.com/thomasvrussell/snail/blob/main/notebooks/3-SpecData_Process_Example.ipynb>`_ : the notebook demonstrates the pre-processing of the spectroscopic data described in our paper, including smooth, rebinning, lines removal and color calibration, etc.

.. [*] `4-LSTM_Predictions_on_New_SN.ipynb <https://github.com/thomasvrussell/snail/blob/main/notebooks/4-LSTM_Predictions_on_New_SN.ipynb>`_ : the notebook provides a guide for users who want apply our LSTM model on very limited spectroscopic data of newly discovered SNe Ia. In this notebook, we use SN 2016coj, a well-observed SN Ia from the latest BSNIP data release, as an example.

.. [*] `5-LSTM_Estimate_Spectral_Phase.ipynb <https://github.com/thomasvrussell/snail/blob/main/notebooks/5-LSTM_Estimate_Spectral_Phase.ipynb>`_ : although our neural network is trained based on the spectra with phase information as prior knownlege, it is still possible to apply the model to the phase-unknown spectral data. The underlying idea is that using incorrect phase of input spectrum can degrade the predictive performance of our method, that is to say, we may find the best-fit phase of input spectrum (spectra) by minimizing the predictive error(s). This notebook is to show how to do the estimates on spectral phase via the lstm model. In the specific case of SN 2016coj in the notebook, the estimation errors are around 0.5 - 2.0d.

Publications use our method
-----------

- *SN2018agk: A prototypical Type Ia Supernova with a smooth power-law rise in Kepler (K2) (Qinan Wang, et al., 2021, ApJ, see Figure 5 & 6)*.

Todo list
-----------

- Support spectral sequence with arbitrary timesteps as input. (current model only accepts spectral pair as input.)

- Support more flexible wavelength range for input spectra. (current model is trained on spectra with uniform wavelength range from 3800 to 7200 A.)

Common issues
-----------

TBD

Development
-----------
The latest source code can be obtained from
`<https://github.com/thomasvrussell/snail>`_.

When submitting bug reports or questions via the `issue tracker 
<https://github.com/thomasvrussell/snail/issues>`_, please include the following 
information:

- OS platform.
- Python version.
- Tensorflow version.
- Version of SNAIL.

Cite
------

*Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2022, ApJ)*. 

Arxiv link: `<https://arxiv.org/abs/2202.02498>`.

DOI: TBD
