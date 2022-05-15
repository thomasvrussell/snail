from setuptools import setup, find_packages

DESCRIPTION = "SuperNova Artificial Inference by Lstm neural networks (SNAIL)"
LONG_DESCRIPTION = open('README.rst').read()
NAME = "snail"
AUTHOR = "Lei Hu"
AUTHOR_EMAIL = "hulei@pmo.ac.cn"
MAINTAINER = "Lei Hu"
MAINTAINER_EMAIL = "hulei@pmo.ac.cn"
DOWNLOAD_URL = 'https://github.com/thomasvrussell/snail'
LICENSE = 'MIT Licence'
VERSION = '1.1.2'

install_reqs = ['scipy>=1.5.2',
                'astropy>=4.0.2',
                'scikit-learn>=0.23.2',
                'packaging>=20.4',
                'extinction==0.4.2']

setup(name = NAME,
      version = VERSION,
      description = DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      setup_requires = ['numpy'],
      install_requires = install_reqs,
      author = AUTHOR,
      author_email = AUTHOR_EMAIL,
      maintainer = MAINTAINER,
      maintainer_email = MAINTAINER_EMAIL,
      download_url = DOWNLOAD_URL,
      license = LICENSE,
      packages = find_packages(),
      include_package_data = True,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Astronomy'],
     )
