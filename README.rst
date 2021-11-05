Package Description
-------------------

The difficulties in acquiring spectroscopic data have been a major challenge for supernova surveys. snlstm is a data-driven method based on LSTM neural networks for spectroscopic studies of type Ia supernovae. We trained a LSTM model based on a dataset includes 3091 spectra from 361 individual SNe Ia. The model enables the construction of spectral sequences from spectroscopic observations with limited time coverage. This repository is associated to the paper *Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, ApJ, under review)*.




and for future time-domain surveys. 
The empolyed dataset includes 3091 spectra from 361 individual SNe Ia. 
Although the real spectroscopic observations of SNe Ia (in most cases) are sparsely and irregularly time-sampled, the 
Spectroscopic observations of SNe Ia are sparsely and irregularly time-sampled. 

This method os proposed by the paper *Spectroscopic Studies of Type Ia Supernovae Using LSTM Neural Networks (Hu et al. 2021, ApJ, under review)*.
This companion repository contains the code associated to 

.. image:: https://img.shields.io/badge/License-MIT-red.svg
    :target: https://opensource.org/licenses/MIT

Installation
-----------
One can install any desired version of snlstm from Github `<https://github.com/thomasvrussell/snlstm>`_: ::

    python setup.py install

Additional Dependencies
-----------

- `R <https://www.r-project.org>`_: R programming language is required for FPCA parameterization. To compress the high dimensions. `fpca <https://CRAN.R-project.org/package=fpca>`_ ::

    yum install R
    R > install.packages("fpca")

- `tensorflow <https://github.com/tensorflow/tensorflow>`_: tensorflow is required to make the spectral predictions with a given LSTM model or training or new model. The default LSTM model in this repository is trained with tensorflow 1.14.0. We recommend users to install the same version via conda: ::

    conda install -c anaconda tensorflow=1.14.0

- `pyphot <https://github.com/mfouesneau/pyphot>`_: pyphot is a useful package to compute synthetic photometry on a spectrum with given filter. We used it to calibrate the spectral color. We recommend users to install the latest Github version (pyphot 1.1).

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
