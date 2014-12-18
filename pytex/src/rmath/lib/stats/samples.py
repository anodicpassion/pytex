'''
Created on 17/12/2014

@author: chips
'''
from sympy import sqrt, Integer as _
from random import randint, choice, shuffle, random

def iaccumulate(L):
    '''Iterates accumulating all values of L in a sum'''

    S = 0
    for x in L:
        S += x
        yield S

def accumulate(L):
    '''Returns a list accumulating all values from L'''

    return list(iaccumulate(L))

def roullete(probs, L):
    '''Pick an element from L at random with probabilities proportional to 
    `probs`'''

    cumprob = accumulate(probs)
    r = random() * cumprob[-1]

    for i, x in enumerate(cumprob):
        if x >= r:
            return L[i]
    return L[-1]

def mean(L):
    '''Return the mean value of the elements in the list L'''

    return _(sum(L)) / len(L)

def std(L, dof=0):
    '''Return the standard deviations of the elements in the list L'''

    return sqrt(var(L, dof=dof))

def var(L, dof=0):
    '''Return the variance the elements in the list L'''

    mu = mean(L)
    return sum((x - mu) ** 2 for x in L) / (len(L) - dof)

def sumsqr(L):
    '''Return the sum of squares of the elements in the list L'''

    return sum(x ** 2 for x in L)

class ZSample(list):
    '''Creates a sample from N integers with the given mean and variance.'''

    def __init__(self, size=5, mean=None, variance=None):
        self.size = size
        if mean is None:
            mean = randint(1, 20)
        if variance is None:
            variance = 9 * size

        # Select the delta values
        deltas = list(self._iter_deltas(size, 2 * variance))
        if len(deltas) == 1:
            raise ValueError
        else:
            del deltas[0]  # skip the [0, 0, 0, ...] element

        # Rank deltas
        ranks = [ self._rank(delta, variance) for delta in deltas ]

        # Select one delta respecting the rank probabilities
        delta = list(roullete(ranks, deltas))

        # Uses that delta in order to create the samples
        # Shuffle
        shuffle(delta)

        # 50% chance of flipping elements
        if choice([True, False]):
            delta = [ -x for x in delta ]

        # Adds the mean and populate list
        self.extend(x + _(mean) for x in delta)


    # Statistical properties ---------------------------------------------------
    @property
    def mean(self):
        return mean(self)

    @property
    def std(self):
        return std(self)

    @property
    def var(self):
        return var(self)

    @property
    def s_std(self):
        return std(self, 1)

    @property
    def s_var(self):
        return var(self, 1)

    @property
    def std_of_mean(self):
        return self.s_std / sqrt(len(self))

    # Auxiliary functions ------------------------------------------------------
    def _rank(self, deltas, variance):
        rank = 1
        rank *= variance / (variance + abs(variance - var(deltas)))
        rank *= sum(1 for x in deltas if x != 0) / len(deltas)
        return rank

    def _iter_deltas(self, size, max_variance):
        '''Iterates over all lists of deltas for a given size'''

        tsorted = lambda L: tuple(sorted(L))
        values = set()
        deltas = [0] * size
        value = tsorted(deltas)
        values.add(value)
        yield value

        for x in range(1, int(sqrt(max_variance))):
            deltas = [0] * size

            # Add in pairs of x, -x
            for i in range(size // 2):
                deltas[2 * i] = x
                deltas[2 * i + 1] = -x
                if sumsqr(deltas) <= max_variance:
                    value = tsorted(deltas)
                    if value not in values:
                        values.add(value)
                        yield value

            for i in range(size // 2):
                deltas[2 * i + 1] *= -1
                deltas[0] = -sum(deltas[1:])
                if sumsqr(deltas) <= max_variance:
                    value = tsorted(deltas)
                    if value not in values:
                        values.add(value)
                        yield value


if __name__ == '__main__':
    L = ZSample()
    print(L.std)
    print(L.s_std)
    print(L.std_of_mean)
    print(L.mean)

