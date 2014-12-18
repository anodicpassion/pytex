import random as _random
from random import randint, uniform, random, sample, shuffle, choice  # @UnusedImport
from sympy import Integer as _
from sympy import sympify as _sympify

__all__ = ['oneof', 'shuffled', 'randint', 'uniform', 'random', 'sample',
           'shuffle', 'choice', 'rfrac', 'rint', 'rsign']

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

def shuffled(*args, inplace=False):
    '''
    Return a shuffled copy of a list or sequence.
    
    If 'inplace' is True, the argument is modified and the return value is the 
    list itself.
    '''

    if len(args) == 1:
        L = args[0]
        if not inplace:
            L = list(L)
        _random.shuffle(L)
    else:
        L = list(args)
        _random.shuffle(L)
    return L

#===============================================================================
# Rmath randomizers: TODO: reimplement properly in rmath
#===============================================================================
def rsign():
    return oneof(_(1), _(-1))

def rint():
    return _(oneof(1, 2, 3, 4, 5, 6, 12))

def rfrac():
    return _sympify(oneof('1/2 1/3 1/4 2/3 3/2 3/4 1/5 2/5 3/5 5/2 5/3'.split(' '))) + oneof(0, 0, 1)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
