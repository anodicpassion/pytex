from fractions import gcd as _gcd
from functools import reduce

__all__ = ['gcd', 'lcm']

def gcd(numbers):
    """Return the greatest common divisor of the given integers
    
    Examples
    --------
    
    >>> lcm([1, 2, 3, 4])
    12
    
    >>> gcd([2, 6, 12])
    2
    """
    return reduce(_gcd, numbers)

def lcm(numbers):
    """Return lowest common multiple."""

    def lcm(a, b):
        return (a * b) // gcd([a, b])
    return reduce(lcm, numbers, 1)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
