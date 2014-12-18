'''
The generator module implements random mathematical objects generators. It has
two separate public interfaces. The first is used internally by Jinja templates
at `alttex.template` in order to include random objects in TeX code. These are
defined in the `public_template` module inside this package and consists in the
``NN``, ``ZZ``, ``QQ``, ``RR``, ``CC`` and friends.

The second interface in the ``public`` module consists in functions that are 
meant to be used by Python scripts or libraries. These functions are exported 
to the public API. 

Note that functions in this package are not simple random number (or random
mathematical objects) generators. Objects are (randomly) created targeting some
specific complexity level. This should mitigate the possibility that simply by 
the virtue of the randomly selected values a specific realization of a 
mathematical problem becomes much easier or much more difficult than the 
average. 

Internally all generators are implemented by the ``base.Generator`` class.
Generators create objects using a Monte Carlo search similar to a genetic
algorithm. Each mathematical object has an internal representation that can be
modified by many different forms of mutations. These mutations can be selected 
to occur either in the direction of increasing or of decreasing the current 
complexity. The mutations occur until an object of a suitable complexity level
is found. 
'''
from .util import *
from .gentypes import *
from .proxy import *
