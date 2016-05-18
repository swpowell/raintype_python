"""
UW Rain Type
"""

import os
import sys

from numpy.distutils.core import setup

# Pull the header into a variable
doclines = __doc__.split("\n")

VERSION = '3.1'

# Set variables for setup
PACKAGES = ['uw_raintype']

# Run setup
setup(
      name='uw_raintype',
      version=VERSION,
      url='http://www.atmos.washington.edu/MG/PDFs/JTECH16_Powell-etal_RainCat.pdf',
      author='Scott Powell, Stacy Brodzik',
      author_email='spowell@atmos.uw.edu',
      description=doclines[0],
      license='LICENSE',
      packages=PACKAGES,
      classifiers=["""
          Development Status :: Beta,
          Programming Language :: Python",
          Topic :: Scientific/Engineering
          Topic :: Scientific/Engineering :: Atmospheric Science
          Operating System :: Unix
          Operating System :: POSIX :: Linux
          Operating System :: MacOS
          """],
      long_description="""
          Python tool for rain type classification.
          To access, use the following in your analysis code:
          from uw_raintype import raintype
          """,
      )
