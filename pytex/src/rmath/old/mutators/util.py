if __name__ == '__main__':
    import rmath.mutators #@UnusedImport
    __package__ = 'rmath.mutators' #@ReservedAssignment

from ..complexity import complexity
from functools import wraps
import random

#===============================================================================
# Decorators
#===============================================================================
def keep_sign(func):
    '''Decorator that adds support for the keep_sign argument for numerical 
    mutators'''

    @wraps(func)
    def decorated(obj, *, keep_sign=True, **kwds):
        new = func(obj, **kwds)
        if keep_sign:
            if (new < 0 and new > 0) or (new > 0 and new < 0):
                new = -new
            return new
        else:
            return random.choice([-1, 1]) * new

    return decorated

def mutate_up(func):
    '''Decorator that adds support for the mutate_up argument for generic 
    mutators'''

    @wraps(func)
    def decorated(obj, *, mutate_up=None, **kwds):
        new = func(obj, **kwds)
        if mutate_up is None:
            return new
        else:
            for _ in range(100):
                c_new = complexity(new)
                c_old = complexity(obj)
                if ((mutate_up and (c_new < c_old or random.random() < 0.25)) or
                    (not mutate_up and (c_new > c_old or random.random() < 0.25))):
                    return new
            else:
                action = 'increase' if mutate_up else 'decrease'
                raise RuntimeError('could not %s complexity level after 100 iterations' % action)
        if keep_sign:
            return (1 if obj >= 0 else -1) * abs(new)
        else:
            return new

    return decorated
