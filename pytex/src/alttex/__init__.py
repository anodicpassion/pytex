# Register alttex.packages_lib in the pytex package path
from pytex import register_path
register_path('%s.packages_lib' % __package__)
del register_path

from .altsource import *
