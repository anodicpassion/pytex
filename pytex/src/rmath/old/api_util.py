import sympy as _sp

def frac(a, b=1):
    '''Return a fraction with given numerator and denominators
    
    Exampĺes
    --------
    
    >>> frac(1, 2)
    1/2
    >>> frac(2) / 4
    1/2
    >>> frac(1.5)
    3/2
    '''

    return _sp.Rational(a) / b

import random as mrandom
_random = mrandom
from random import randint, uniform, random, sample, shuffle, choice  # @UnusedImport

def oneof(*args):
    """Return a random value from its arguments. 
    
    Can be called in two different ways:
        oneof(sequence) --> returns an element of the sequence
        oneof(arg1, arg2, ...) --> returns one of the arguments
        
    Examples
    --------
    
    >>> x = oneof(1, 2, 3)
    >>> x in [1, 2, 3] # x can be 1, 2 or 3
    True
    
    >>> nums = range(10)
    >>> x = oneof(nums)
    >>> 0 <= x < 10 # x can be 0, 1, ..., or 10
    True
    """

    if not args:
        raise TypeError('cannot be called with empty arguments!')
    elif len(args) == 1:
        try:
            return _random.choice(list(args[0]))
        except TypeError:
            raise TypeError("first argument must be a sequence or more than one argument must be given, got '%s'" % args)
    else:
        return _random.choice(args)

def shuffled(lst, inplace=False):
    '''
    Return a shuffled copy of a list or sequence.
    
    If 'inplace' is True, the argument is modified and the return value is the 
    list itself.
    '''

    if not inplace:
        lst = list(lst)
    _random.shuffle(lst)
    return lst


if __name__ == '__main__':
    import doctest
    doctest.testmod()
