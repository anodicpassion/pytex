from random import random
from rmath.generators.gentypes import *
from rmath.generators.proxy import SharedProxy as _SharedProxy

#===============================================================================
# Numerical types
#===============================================================================
# Create proxy variables for NN, ZZ, QQ, and friends
_globals = globals()
for _name in ['NN', 'ZZ', 'ZP', 'QQ', 'QP', 'FRAC', 'FRACP', 'RR', 'RP',
              'CC', 'CQ', 'CN', 'BOOL', 'SIGN']:
    _gen = _globals[_name].new
    _subclass = type(_name + 'Proxy', (_SharedProxy,),
                        {'_func': staticmethod(_gen),
                         '_kwds': {'register': False}})
    for c in 'abcdefghijklmnopqrstuvwxyz':
        _globals[_name + c] = _subclass()

if __name__ == '__main__':
    for k, v in sorted(globals().items()):
        print('%s: %s' % (k, v))
