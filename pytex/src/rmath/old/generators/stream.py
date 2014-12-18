if __name__ == '__main__':
    import rmath.generators #@UnusedImport
    __package__ = 'rmath.generators' #@ReservedAssignment

import random
import itertools
import sympy as sp
from ..complexity import read_complexity, complexity as complexity_f
from .. import mutators

#TODO: deprecate export and internal representation or do it properly
#===============================================================================
# Base class for all stream of random objects classes. 
#===============================================================================
# Implements much of the logic of random object complexity-based creation.
# 
# Objects are created and mutated randomly until a certain desired complexity
# level is achieved. Subclasses must implement functions that mutate some 
# given object with a high probability of increasing or decreasing its 
# complexity. This mutation process continues until an object with the desired
# complexity level is created.
#
# All objects are stored in dictionaries for cache. Hence the randomly created 
# objects (or their internal representation) must be hashable.
#
class RStream:
    '''
    RStream is an iterator over a random sequence of objects within given 
    complexity bounds.  
    
    Subclasses can implement iterators for random numbers, polynomials, 
    functions, etc.
    
    Attributes
    ----------
    min, max: int
        Minimum and maximum allowed complexity levels
    bounds: tuple
        A 2-tuple with (min_complexity, max_complexity)
    current: obj
        Current value in the RStream
    '''

    max_attempts = 25
    max_resets = 10
    max_level_size = 50
    min_level_size = 25
    complexity_worker = staticmethod(complexity_f)
    init_cache = []

    def __init__(self, current, min=1, max=3, *, mutator=None):
        self.current = current
        self.min = min
        self.max = max
        self._complexity_cache = {}
        self._bounds_cache = {}
        self._levels_cache = {}
        self._level_hits = {}
        self.mutator_f = mutator

        self._init_cache()

    def _init_cache(self):
        obj = self.current
        for _ in range(20):
            obj = self.mutate(obj)
            compl = self.complexity(obj)

        for obj in list(self._complexity_cache):
            for _ in range(15):
                obj = self.mutate(obj)
                compl = self.complexity(obj)

        for obj in self.init_cache:
            self.complexity(obj)

    #===========================================================================
    # Iterator protocol
    #===========================================================================
    def __iter__(self):
        return self

    def __next__(self):
        a, b = self.bounds

        # Try to read from bounds cache
        try:
            if len(self._bounds_cache[(a, b)]) >= self.min_level_size:
                raise KeyError
        except KeyError:
            pass
        else:
            return random.choice(objs)

        # Create caches
        for i in range(a, b):
            pass


        next = self.mutate(self.current)
        level = self.complexity(next)
        for _ in range(self.max_resets):
            for _ in range(self.max_attempts):
                if a <= level <= b:
                    _ = None
                    break
                if level < a:
                    next = self.mutate(self.current, direction= -1)
                else:
                    next = self.mutate(self.current, direction=1)
                level = self.complexity(next)
            if _ is not None:
                self._reset()
        else:
            raise RuntimeError('maximum number of attempts exceeded: %s' % self.max_attempts)

        self.current = next

        return random.choice(self._bounds_cache[(a, b)])


    @property
    def bounds(self):
        return (self.min, self.max)

    @bounds.setter
    def bounds(self, value):
        a, b = value
        self.min_complexity = a
        self.max_complexity = b

    def _get_bounds(self, a, b):
        try:
            return self._bounds_cache[(a, b)]
        except KeyError:
            objs = []
            for i in range(a, b):
                objs.extend(self._levels_cache.get(i, []))
            self._bounds_cache[(a, b)] = objs
            return objs

    def _reset(self):
        N = random.randrange(len(self._complexity_cache))
        for i, obj in enumerate(self._complexity_cache):
            if i == N:
                return obj
        raise RuntimeError

    #===========================================================================
    # Abstract methods
    #===========================================================================
    def mutate(self, obj, direction=None):
        '''Propose a new object from ``obj``. 
        
        The "direction" attribute controls the complexity of the new generated
        object: if it is positive, the new object will have a higher complexity
        than the original. If it is negative, the complexity will be lower, and
        "direction=0" preserves the complexity level. 
        '''
        if direction is None:
            return self.mutator_f(obj)
        elif direction > 0:
            return self.mutator_f(obj, mutate_up=True)
        elif direction < 0:
            return self.mutator_f(obj, mutate_up=False)
        elif direction == 0:
            raise NotImplementedError
        else:
            raise RuntimeError

    def complexity(self, obj):
        '''Computes the complexity of the object. 
        
        The default implementation just calls the generic "complexity" function.
        It can be overridden for optimization or in order to change the default
        behavior.'''

        try:
            return self._complexity_cache[obj]
        except KeyError:
            compl = self._complexity_cache[obj] = self.complexity_worker(obj)
            self._bounds_cache = {}
            self._levels_cache.setdefault(compl, []).append(obj)
            return compl

    def new(self, a=None, b=None, *, size=None):
        '''Return a new object with the given complexity level `a`.
        
        If ``force=True`` and too many failed attempts are made for creating the 
        desired object, it return an object of similar (but not the desired) 
        complexity. Otherwise a RuntimeError is raised.'''

        b = b if b is not None else a
        if b is not None and b < a:
            raise ValueError('invalid bound: b < a')
        if a != None:
            self.min, self.max = a, b

        # Return a single object if size is given
        if size is None:
            return next(self)
        # Or return a list of objects otherwise
        else:
            return [ next(self) for _ in range(size) ]

    #===========================================================================
    # Auxiliary/internal functions
    #===========================================================================
    def populate_level(self, level):
        '''Populate the given level with new objects'''

        self._target = level
        population = self._categories.setdefault(level, [])
        for _ in range(self.cache_size[1]):
            for _ in range(min(self.cache_size[0], 10)):
                self.update()
            if self._categories.get(level):
                self.set_current(random.choice(self._categories[level]))
        return population

    def build_cache(self, level):
        '''Build cache for the given level'''

        self._complexity_cache[level] = cache = list(self.populate_level(level))
        levels = [level, level]
        state = 0
        iter_n = 0
        while len(cache) < self.cache_size[0]:
            if state == 0:
                level = levels[0] - 1
                state += 1
            elif state == 1:
                level -= 1
                state += 1
                levels[0] = level
            else:
                level = levels[1] + 1
                state = 0
                levels[1] = level
            if level <= 0:
                continue
            iter_n += 1
            if iter_n > 10:
                print('error: maximum number of iterations exceeded')
                #raise RuntimeError('maximum number of iterations exceeded')
                population = self.populate_level(level)
                N = max(len(population) - len(cache), 1)
                cache.extend(population[:N])

            population = self.populate_level(level)
            N = max(len(population) - len(cache), 1)
            cache.extend(population[:N])

    def update(self):
        '''
        Suggest a new random object that is not necessarily in the target 
        complexity level, but tries to approach it 
        '''

        if self.target >= self._level:
            self.set_current(self.mutate_up(self._value))
        else:
            self.set_current(self.mutate_down(self._value))

    def _new_worker(self, level):
        '''
        Worker function for the new() method.
        '''

        # Try to use a cached value, if available
        if level in self._levels:
            # TODO: define conditions
            pass

        # 10/10 attempts to create the correct number
        for _ in range(10):
            yield self._find_valid_new(level, 10)

    def _find_valid_new(self, level, N=10):
        '''
        Calls ``update()`` up to N times trying to obtain a _value within
        the given level bounds.
        '''
        self._target = level
        for _ in range(N):
            self.update()
            if self._level == level:
                return self._value

class SimpleStream(RStream):
    '''Base class for stream that have mutators already implemented in the 
    rmath.mutators package'''


#===============================================================================
# Integer numbers generator
#===============================================================================
class IntegerStream(SimpleStream):
    '''
    Generates integers.
    
    Examples
    --------
    
    >>> random.seed(1)
    >>> [ INTEGER.new(4) for _ in range(10) ]
    [12, -12, 8, 6, 11, 7, -6, -7, -9, 11]
    '''
    MUTATOR_F = staticmethod(mutators.mutate_int)

    def __init__(self, start_value=None, target=3):
        start_value = int(start_value if start_value is not None else 2)
        super(IntegerStream, self).__init__(start_value, 1, target)
        #for i in range(1, 101):
        #    self.register_value(i)

#===============================================================================
# Rational numbers generator
#===============================================================================
class RationalStream(SimpleStream):
    '''
    Generates fractions.

    Examples
    --------
    
    >>> gen = RationalGen()
    >>> [ gen.new(4, 5) for _ in range(16) ]
    [3/2, 1/4, 3/2, 3/2, 3/2, 3, 4, 4, 4, 4]
    '''
    cache_size = (10, 40)
    mutate_worker = staticmethod(mutators.mutate_rat)

    def __init__(self, start_value=None, target=3):
        start_value = (start_value if start_value is not None else sp.Rational(1, 2))
        super(RationalStream, self).__init__(start_value, 1, target)

#===============================================================================
# Real number generator
#===============================================================================
class RealStream(RationalStream):
    def export(self, x):
        return float(sp.numer(x)) / sp.denom(x)

#===============================================================================
# Export global instances
#===============================================================================
# It is not necessary to create multiple instances of the Generator sub-classes 
# Hence we make one instance of each class and only export theses instances.
# Even these objects are not part part of the public API, but are used 
# internally by `new_object()` and NN, ZZ, QQ, RR and friends 
INTEGER = None #RStream(5, 2, 6, mutator=mutators.mutate_int)
RATIONAL = None# RationalStream()
REAL = None#RealStream()
COMPLEX = None#RealStream()

__all__ = ['INTEGER', 'RATIONAL', 'REAL', 'COMPLEX']

if __name__ == '__main__':
    from pprint import pprint
    print(sum(complexity_f(x) for x in range(1000)))

#    print('OK')
#    print(len(INTEGER._complexity_cache))
#    print(next(INTEGER))
#    #import doctest
#    #doctest.testmod()
#    for i in range(10):
#        print(INTEGER.new(size=20))
#    print([ next(INTEGER) for _ in range(10) ])
#    print([ next(RATIONAL) for _ in range(10) ])

