if __name__ == '__main__':
    import rmath; __package__ = 'rmath'  # @ReservedAssignment @UnusedImport

import sympy as sp
import numpy as np
from .util import Primes, multifunction
PRIMES = Primes([-1, 2])

#===============================================================================
# Generic complexity calculator --- uses multidispatch in order to delegate
# computation to actual implementations.
#===============================================================================
@multifunction(None)
def complexity(obj):
    '''Returns the algebraic complexity of the given object.'''

    tname = type(obj).__name__
    raise TypeError('Cannot compute complexity of %s objects' % tname)

#===============================================================================
# Integers
#===============================================================================
@complexity.dispatch(int)
@complexity.dispatch(sp.Integer)
def complexity_integer(N):
    r'''We formulate two notions of a integer number complexity: multiplication
    complexity tries to measure the difficulty of using the number in 
    multiplications and divisions and addition complexity measures the 
    difficulty of using this number in additions and subtractions.
    
    The final complexity is an arbitrary weighted mean of these numbers using 
    the formula:
    
        C = (3 * A + B) / 4,
    
    in which A is the largest of addition and multiplication complexity and B 
    is the smallest value.
    
    Examples
    --------
    
    >>> icomplexity_mul(20)
    5.056661498224149
    >>> icomplexity_add(20)
    4.446143157024303
    >>> complexity(20)
    4.904031912924188
    
    As reference, consider the multiplication and addition complexity of the
    first 10 numbers:
    
    >>> show = lambda x: '%.2f' % icomplexity_mul(x)
    >>> print(*(show(n) for n in range(1, 11)))
    1.00 1.66 2.35 2.84 3.05 4.01 5.58 4.03 4.04 3.40
    
    >>> show = lambda x: '%.2f' % icomplexity_add(x)
    >>> print(*(show(n) for n in range(1, 11)))
    1.00 2.59 2.96 3.33 3.70 4.06 4.43 4.43 3.70 4.08
    
    The notion of complexity makes some numbers being preferable (in terms of
    being easier to work with) than other more or less independently from its 
    actual value. For instance, the first 20 numbers can be ordered by complexity
    value as follows
    
    >>> L = sorted((complexity(n), n) for n in range(1, 21))
    >>> [ n for (c, n) in L ]
    [1, 2, 3, 4, 5, 10, 9, 6, 8, 20, 7, 12, 15, 16, 18, 11, 14, 13, 17, 19]
    '''

    m, a = icomplexity_mul(N), icomplexity_add(N)
    A = max(m, a)
    B = min(m, a)
    return (3 * A + B) / 4

def icomplexity_mul(N, a=0.393521832648, b=0.0013387530885,
                       c=0.000464998636365, d=0.351562612214,
                       e=0.688371066173):
    '''
    Compute the multiplication complexity of the number from its list of 
    factors.
    
    The multiplication complexity tries to capture the difficulty of using
    the given number in multiplication and division operations. 
    
    We use a pseudo prime factorization in which -1 and 10 are considered 
    atomic factors as the other regular prime numbers. The number -200, for 
    instance, is factorized as ``-200 = (-1)^1 * 10^2 * 2^1``, rather than using 
    the true prime factorization of ``-200 = (-1) * 2^3 * 5^2``. This captures
    the fact that powers of 10 are easier to handle in a base 10 system.
    
    A complexity value is assigned to each factor according to their 
    position in the list of prime numbers. The table shows the complexity 
    contribution of the first few factors
    
        +------------+----------+---------+----------+----------+---------+--------+--------+-----+
        | Factor     |   -1     |    10   |     2    |     3    |    5    |    7   |    11  | ... |  
        +------------+----------+---------+----------+----------+---------+--------+--------+-----+
        | C. contrib |  e + 1/2 | e + 3/2 |  e + 1/2 |  e + 2/2 | e + 3/2 |  b + 4 |  b + 5 | ... |
        +------------+----------+---------+----------+----------+---------+--------+--------+-----+
        
    Given the factorization, the multiplication complexity of the number is
    computed as the sum of `<factor complexity> * (<exponent> + a)` of each term 
    in the factorization minus `c` times the number of multiplication signs in 
    the full factorization.
    
    The numbers a, b, c where chosen so the numbers from 1 to 25 are ranked as 
    close as possible to the following somewhat arbitrary list:
    
        [1, 2, 3, 10, 4, 5, 6, 20, 8, 9, 12, 7, 15, 16, 25, 18, 24, 11, 14, 21, 13, 22, 17, 19, 23 ]
    
    Using the number ``-200`` as an example, we have a complexity of:: 
    
        C(-200) = C(-1) * (1 + a) + C(10) * (2 + a) + C(2) * (1 + a) - 2 * c
                =  (b + 1) * (1 + a)  +  (b + 1.5) * (2 + a) + (b + 1) * (1 + a) - 2 * c
                =  4*b + 3*b*a + 3.5*a + 5 - 2*c
    >>> icomplexity_mul(-200)
    8.94815778882515

    The multiplication complexity of 0 and 1 is choosen to be 1.0, while the
    complexity of -1 is set to 2.0.
    
    Observations
    ------------
    
    From the above formula, we see the multiplication complexity of prime
    numbers is twice the value of its complexity contribution.
    '''

    # Special cases 0, 1, -1
    if N in (0, 1):
        return 1.0
    elif N == -1:
        return 1.0 + b

    # Compute raw complexity from prime factors
    factors = sp.factorint(abs(N))

    # power 10 factorization
    try:
        e10 = min(factors[2], factors[5])

        factors[2] -= e10
        if not factors[2]:
            del factors[2]

        factors[5] -= e10
        if not factors[5]:
            del factors[5]

    except KeyError:
        e10 = 0

    # powers 2, 3 and 5 are special cases
    e2 = factors.pop(2, 0)
    e3 = factors.pop(3, 0)
    e5 = factors.pop(5, 0)

    # Compute raw factorization
    prime_index = PRIMES.index
    compl = sum((prime_index(p) + b) * (e + a) for (p, e) in factors.items())

    # Add contribution of bases 2, 3, 5, and 10
    compl += (e + 0.5) * (e2 + a) if e2 else 0.0
    compl += (e + 1.0) * (e3 + a) if e3 else 0.0
    compl += (e + 1.5) * (e5 + a) if e5 else 0.0
    compl += (e + 1.5) * (e10 + a) if e10 else 0.0

    # Extra complexity for negative numbers
    compl += 0.0 if N >= 0 else 1.0

    # Reduce complexity penalty of long numbers
    compl -= c * (bool(e2) + bool(e3) + bool(e5) + bool(e10) + sum(factors.values()) - 1)

    # Penalty for long numbers
    compl += d * (len(str(N)) - 1)

    # try:
    #    return 2 * compl / ((b + 1.5) * (1 + a) - d)
    # except ZeroDivisionError:
    #    return compl
    return compl

def icomplexity_add(N, a=0.36823199198, b=0.256962562686, c=1.76021775021):
    '''
    Compute the addition complexity of the number.
    
    The addition complexity tries to capture the difficulty of using
    the given number in addition and subtraction operations.
    
    It is computed digit by digit by summing a factor proportional to the 
    likelihood of the digit participates in a "+1" operation.
    '''

    # Special cases 0, 1, -1
    if N == 0:
        return 0.0
    elif N == 1:
        return 1.0
    elif N == -1:
        return 1.5

    # Compute complexity
    C = { str(x): (a * (x + b)) for x in range(10) }
    C['8'] = C['7']
    C['9'] = C['5']
    digits = str(abs(N))
    num_zeros = digits.count('0')

    # Add complexity of each digit
    compl = sum(C[x] for x in digits)

    # Add complexity for long numbers ...
    compl += c * (len(digits))

    # ... but bound it for numbers with lots of zeros
    compl -= c * max(num_zeros - 3, 0)

    # Negative numbers also have a complexity bonus
    if N < 0:
        compl += 0.5
    return compl

#===============================================================================
# Rational
#===============================================================================
@complexity.dispatch(sp.Rational)
def complexity_rat(N):
    '''
    Compute the complexity of a rational number.
    '''
    a, b = int(sp.numer(N)), int(sp.denom(N))
    C_A = complexity_integer(a)
    C_B = complexity_integer(b)
    C_M = max(a, b)
    return 0.5 * (C_A + C_B) + 0.5 * C_M

#===============================================================================
# Tests
#===============================================================================
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    L100 = sorted((icomplexity_mul(n), n) for n in range(1, 100001))
    print(np.array(L100, dtype=int)[:100, 1])
