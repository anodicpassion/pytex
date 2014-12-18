from .errors import *
from . import tokens
from .context import Context
from .textypes import *
from .package import *
from .job import TeXJob, TeX
from .util import *

#===============================================================================
# Register modules
#===============================================================================
from .types import argspec as _argspec
from . import textypes as _textypes
_argspec.tex = _textypes

#===============================================================================
# Register special LaTeX and TeX packages
#===============================================================================
register_package('@LaTeX', Package.from_module('pytex.lib.latex'))
register_package('@TeX', Package.from_module('pytex.lib.tex'))