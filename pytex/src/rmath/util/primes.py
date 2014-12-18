import itertools
import sympy as sp

__all__ = ['Primes', 'PRIMES', 'next_prime', 'prev_prime']

class Primes(object):
    '''Iteration over prime factors
    
    Primes() instances behave as a list of primes. The list is computed 
    on-the-fly as higher prime numbers are requested.
    
    Parameters
    ----------
    
    head : sequence
        The 'head' argument can be used to modify Primes() to generate 
        pseudo-primes lists. This can be used to include zero, one, minus one 
        or even non-prime numbers.
        
    Examples
    --------
    
    >>> p = Primes(); p[0:10]
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    
    >>> p = Primes([-1, 0, 1, 2]); p[0:10]
    [-1, 0, 1, 2, 3, 5, 7, 11, 13, 17]
    
    >>> p = Primes([-1, 0, 1, 2, 10]); p[0:10]
    [-1, 0, 1, 2, 10, 3, 5, 7, 11, 13]
    '''
    def __init__(self, head=None):
        self._primes_iter = sp.primerange(0, 2 ** 500)
        head = ([2] if head is None else head)
        self._primes = list(head)
        self._primes_set = set(head)
        self._primes_set.add(None)

        self._order = {}
        for idx, v in enumerate(self._primes):
            self._order[v] = idx

    def __iter__(self):
        '''
        Iterate over Primes sequences.
        
        >>> it = iter(Primes([1, 2, 3]))
        >>> next(it); next(it); next(it); next(it)
        1
        2
        3
        5
        '''
        for i in itertools.count():
            yield self[i]

    def __getitem__(self, idx):
        '''x.__getitem__(i) <==> x[i]'''

        # Integer indices
        if isinstance(idx, int):
            if idx < 0:
                raise IndexError('negative indices not supported')

            next_prime = None
            while idx > len(self._primes) - 1:
                while next_prime in self._primes_set:
                    next_prime = next(self._primes_iter)
                else:
                    self._primes_set.add(next_prime)

                self._primes.append(next_prime)
                self._order[next_prime] = len(self._order)
            return self._primes[idx]

        # Slices
        else:
            a, b, c = idx.start, idx.stop, idx.step
            if a > b:
                raise IndexError('invalid index: %s > %s' % (a, b))
            elif (b < 0) or (a < 0):
                raise IndexError('negative indexes are not supported')
            else:
                if b > len(self._primes):
                    _aux_prime = self[b]
                return self._primes[a:b:c]

    def index(self, p):
        '''
        Return the index of the prime number in the sequence defined in Primes().
        Raises a ValueError for non-prime numbers.
        '''
        idx = len(self._primes)
        while p > self._primes[-1]:
            idx += 1
            self[idx]
        try:
            return self._order[p]
        except KeyError:
            raise ValueError('%s is not a prime number' % p)

#===============================================================================
# Utility functions
#===============================================================================
#
# Prime number control
# --------------------
#
# The list of prime is used internally to compute the integer complexity.
# The next_prime and prev_prime functions are used to mutate a given prime
# factor in an attempt to increase/decrease an integer complexity.
PRIMES = Primes()

def next_prime(p):
    '''Returns the prime following p.
    
    Example
    -------
    
    >>> next_prime(7)
    11
    >>> prev_prime(7)
    5
    
    See also
    --------
    
    prev_prime()
    '''

    return PRIMES[PRIMES.index(p) + 1]

def prev_prime(p):
    '''Returns the prime just before p.
    
    See also
    --------
    
    next_prime()
    '''

    return PRIMES[(PRIMES.index(p) or 1) - 1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
