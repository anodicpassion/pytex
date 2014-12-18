import random
import sympy as sp
from rmath.generators.stream import *

#===============================================================================
# Base class
#===============================================================================
class Generator:
    '''
    Implements objects that represent sets of arbitrary objects and generate 
    random elements from these sets.
    '''
    def __init__(self):
        self._names = {}
        self._created = []

    def reset(self):
        '''Reset generator state'''

        self.__init__()

    def new(self, *args, **kwds):
        '''Returns a new random element of the given set.'''

        register = kwds.pop('register', True)
        new = self._new(*args, **kwds)
        if register:
            self._created.append(new)
        return new

    def _new(self, *args, **kwds):
        '''Worker function for new(), must be implemented in child classes'''

        raise NotImplementedError('Must be implemented in child classes')

    def iter(self, size=None, *args, **kwds):
        '''Return an iterator over random objects.
        
        By generating multiple objects at once, it is possible to implement 
        additional constraints such as generating unique elements.'''

        if size == 0:
            return
        elif size < 0:
            raise ValueError("size can't be negative, got %s" % size)

        register = kwds.pop('register', True)
        new = self._iter(size, *args, **kwds)
        if not register:
            for obj in new:
                yield obj
        else:
            for obj in new:
                self._created.append(obj)
                yield obj

    def _iter(self, size, *args, **kwds):
        '''Worker function for iter(), must be implemented in child classes'''

        raise NotImplementedError('Must be implemented in child classes')

    def __call__(self, **kwds):
        if 'size' in kwds:
            return list(self.iter(**kwds))
        else:
            return self.new(**kwds)

    # Magical methods ----------------------------------------------------------
    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._created[idx]
        else:
            return self._names[idx]

#===============================================================================
# Numerical generators
#===============================================================================
class FiniteGen(Generator):
    OPTIONS = []
    NAME = None

    def _new(self):
        return random.choice(self.OPTIONS)

    def _iter(self, size=None, unique=False):
        size = (sp.oo if size is None else size)
        choice = random.choice
        options = self.OPTIONS
        N = len(options)
        if unique:
            if size > N:
                raise ValueError('impossible to create more than %s unique %s objects' % (N, self.NAME))
            else:
                opt_copy = list(options)
                random.shuffle(opt_copy)
                for obj in opt_copy[:size]:
                    yield obj
        else:
            while size >= 0:
                yield choice(options)
                size -= 1

class NumericGen(Generator):
    STREAM = None
    ONE = sp.Integer(1)
    ZERO = sp.Integer(0)
    def __init__(self, force_pos=True, zero=False):
        super(NumericGen, self).__init__()
        self._force_pos = force_pos
        self._zero = zero

    def _new(self, complexity=None, force_pos=None, zero=None):
        force_pos = (self._force_pos if force_pos is None else force_pos)
        zero = (self._zero if zero is None else zero)

        # 5% chance of creating zeros if zero is True
        if zero and 0.05 > random.random():
            return self.ZERO

        # Complexity can be a maximum value or a bound (when it is a 2-tuple)
        try:
            a, b = complexity
            new = self.STREAM.new_interval(a, b)
        except TypeError:
            new = self.STREAM.new(complexity)

        # Change sign, if necessary
        if not force_pos:
            new *= random.choice([-1, 1])
        return self.ONE * new

    def _iter(self, size=None, complexity=None, force_pos=None, zero=None,
                    init=None, unique=True):
        '''Return a random elements generator.
        
        Parameters
        ----------
        complexity, force_pos, zero:
            Works the same as `meth:new()`
        init: sequence
            A initial sequence of values to prepend to the generator.
        size: int
            Size of the generated sequence. If size=None, the sequence is 
            infinite
        unique: True
            If True, generates unique elements
        '''

        # Check if init values are unique and yield them
        idx = 0
        init = list(init or [])
        if unique and len(set(init)) != len(init):
            raise ValueError('Initial elements are not unique')
        if len(init) > size:
            for obj in init[:size]:
                yield obj
            return
        else:
            for obj in init:
                yield obj
            idx += len(init)

        # Generate non-unique values if unique=False
        if not unique:
            for _ in range(size - idx):
                yield self._new(complexity, force_pos, zero)
            return

        # Create a set of values to check uniqueness
        values = set(init)
        for _ in range(size - idx):
            # 100 attempts to create a unique value
            for _ in range(100):
                new = self._new(complexity, force_pos, zero)
                if new in values:
                    values.add(new)
                    yield new
                    break
            else:
                raise ValueError('too many failed attempts to generate a unique number')

#===============================================================================
# Public API
#===============================================================================
# Finite types -----------------------------------------------------------------
class BoolGen(FiniteGen):
    OPTIONS, NAME = (True, False), 'Boolean'

class SignGen(FiniteGen):
    OPTIONS, NAME = (-1, 1), 'Sign'

# Numerical types --------------------------------------------------------------
class ZZGen(NumericGen):
    STREAM = INTEGER

class QQGen(NumericGen):
    STREAM = RATIONAL

class RRGen(NumericGen):
    STREAM = REAL

class CCGen(NumericGen):
    STREAM = COMPLEX

# Instances --------------------------------------------------------------------
BOOL = BoolGen()
SIGN = SignGen()
ZZ = ZZGen(force_pos=False)
NN = ZP = ZZGen(force_pos=True)
QQ = FRAC = QQGen(force_pos=False)
QP = FRACP = QQGen(force_pos=True)
RR = RRGen(force_pos=False)
RP = RRGen(force_pos=True)
CC = CZ = CQ = CR = CN = CCGen()

__all__ = ['BOOL', 'SIGN', 'ZZ', 'NN', 'ZP', 'QQ', 'QP', 'FRAC', 'FRACP', 'RR',
           'RP', 'CC', 'CZ', 'CQ', 'CR', 'CN']

if __name__ == '__main__':
    gen = QQGen()
    print(gen(size=3, complexity=6, unique=False))
