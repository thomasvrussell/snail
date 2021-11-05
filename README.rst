Package Description
-------------------

The difficulties in acquiring spectroscopic data have been a major challenge for supernova surveys. snlstm is developed to provide a data-driven solution. Based on a dataset including 3091 spectra from 361 individual SNe Ia, we trained LSTM neural networks to learn from the spectroscopic time-series data of type Ia supernovae. The model enables the construction of spectral sequences from spectroscopic observations with very limited time coverage. 

This repository is associated to the paper *Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, ApJ, under review)*.

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.5637790.svg
    :target: https://doi.org/10.5281/zenodo.5637790
    :alt: archival-database v1.1
.. image:: https://img.shields.io/badge/License-MIT-red.svg
    :target: https://opensource.org/licenses/MIT
.. image:: https://img.shields.io/badge/python-3.7-green.svg
    :target: https://www.python.org/downloads/release/python-370/

Installation
-----------
One can install any desired version of snlstm from the Github repository `<https://github.com/thomasvrussell/snlstm>`_: ::

    python setup.py install

Additional Dependencies
-----------

- `R <https://www.r-project.org>`_: In order to reduce the data dimension, we use Functional Principal Component Analysis (FPCA) to parameterize supernova spectra before feeding them into neural networks. The FPCA parameterization and FPCA reconstruction are achieved by the `fpca <https://CRAN.R-project.org/package=fpca>`_ package in R programming language. One can install them, e.g., on CentOS ::

    $ yum install R
    R > install.packages("fpca")

- `tensorflow <https://github.com/tensorflow/tensorflow>`_: tensorflow is required to load a given LSTM model and make the spectral predictions. The default LSTM model in this repository is trained on an enviornment with tensorflow 1.14.0. To avoid potential incompatiability issues casued by different tensorflow versions, we recommend users to install the same version via Conda ::

    conda install -c anaconda tensorflow=1.14.0

- `pyphot <https://github.com/mfouesneau/pyphot>`_ (optional): pyphot is a portable package to compute synthetic photometry of a spectrum with given filter. In our work, the tool was used to correct the continuum component of a supernova spectrum so that its synthetic photometry could be in line with the observed light curves. One may consider to install the package if such color calibration is necessary. We recommend users to install the latest version from Github (pyphot 1.1) ::

    pip install git+https://github.com/mfouesneau/pyphot

Downloading archival datasets
-----------






The archival datasets are available on `zenodo <https://zenodo.org>`_, please download via the link https://doi.org/10.5281/zenodo.5637790

Quick start guide
-----------

Jupyter notebooks.

Common issues
-----------

TBD

Development
-----------
The latest source code can be obtained from
`<https://github.com/thomasvrussell/snlstm>`_.

When submitting bug reports or questions via the `issue tracker 
<https://github.com/thomasvrussell/snlstm/issues>`_, please include the following 
information:

- OS platform.
- Python version.
- Tensorflow version.
- Version of snlstm.

Citing
------
Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, in press)










a data-driven method based on LSTM neural networks for spectroscopic studies of type Ia supernovae. 
We trained a LSTM model based on a dataset includes 3091 spectra from 361 individual SNe Ia. The model enables the construction of spectral sequences from spectroscopic observations with limited time coverage. This repository is associated to the paper *Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, ApJ, under review)*. 

and for future time-domain surveys. 
The empolyed dataset includes 3091 spectra from 361 individual SNe Ia. 
Although the real spectroscopic observations of SNe Ia (in most cases) are sparsely and irregularly time-sampled, the 
Spectroscopic observations of SNe Ia are sparsely and irregularly time-sampled. 

This method os proposed by the paper *Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, ApJ, under review)*.
This companion repository contains the code associated to 
