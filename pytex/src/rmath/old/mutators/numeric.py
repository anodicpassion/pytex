'''
This module defines a variety of functions that return mutated copies of its
arguments
'''
if __name__ == '__main__':
    import rmath.mutators #@UnusedImport
    __package__ = 'rmath.mutators' #@ReservedAssignment

import random
from functools import reduce
from operator import mul as mul_op
import sympy as sp
from ..primes import next_prime, prev_prime
from .util import keep_sign
#===============================================================================
# Numeric
#===============================================================================
@keep_sign
def mutate_int(value, mutate_up=None):
    '''Mutate an integer value. 
    
    If ``mutate_up=True``, mutation tends to increase the input's complexity.
    If ``mutate_up=False``, the tendency is to decrease the number's complexity.
    If it is not set, it will choose the behavior randomly.'''

    if mutate_up is None:
        mutate_up = random.choice([True, False])

    # Special cases
    if value == 1:
        return 2 if mutate_up else 1

    r = random.random()

    # +n increase in number _value
    if r > 0.9:
        delta = round(1 + random.expovariate(1))
        return abs(value + delta if mutate_up else value - delta) or 1

    # Factor manipulations -------------------------------------------------
    factors = sp.factorint(value)

    # Choose a random prime p at random 
    idx = random.randrange(len(factors))
    for p, _ in zip(factors, range(idx + 1)):
        pass
    # Increment/decrement the exponent with probability 45%
    if r > 0.45:
        factors[p] += (1 if mutate_up else -1)
    # Increment the next prime factor exponent  with probability 45%
    else:
        delta = random.randint(1, factors[p])
        factors[p] -= delta
        p = next_prime(p) if mutate_up else prev_prime(p)
        factors[p] = factors.setdefault(p, 0) + delta
    return reduce(mul_op, (p ** e for (p, e) in factors.items()))

def mutate_rat(value, *, keep_sign=True, mutate_up=None):
    '''Mutate rational number'''

    r = random.random()
    numer, denom = sp.numer(value), sp.denom(value)

    # swap numerator and denominator
    if r < 0.20:
        numer, denom = (mutate_int(denom, mutate_up=mutate_up, keep_sign=keep_sign),
                        mutate_int(numer, mutate_up=mutate_up))
    # mutate numerator
    elif r < 0.65:
        numer = mutate_int(numer, mutate_up=mutate_up, keep_sign=keep_sign)
    # mutate denominator
    else:
        denom = mutate_int(denom, mutate_up=mutate_up, keep_sign=keep_sign)

    return sp.Rational(numer, denom or 1)

