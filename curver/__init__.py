
''' Curver is a program for computations in the curve complex. '''

import curver.kernel
from curver.load import load
from numbers import Integral as IntegerType

import warnings

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	import pkg_resources  # Suppress 'UserWarning: Module curver was already imported from ...'
	__version__ = pkg_resources.require('curver')[0].version

# Set up really short names for the most commonly used classes and functions by users.
create_triangulation = curver.kernel.create_triangulation
norm = curver.kernel.norm

AbortError = curver.kernel.AbortError
AssumptionError = curver.kernel.AssumptionError

def show(showable):
	import curver.application
	curver.application.start(showable)
