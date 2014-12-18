if __name__ == '__main__' and __package__ is None:
    import pytex; __package__ = 'pytex.textypes'  # @UnusedImport @ReservedAssignment

from copy import deepcopy
from collections import MutableMapping, UserList, UserDict
from . import Masterlist, Element, TeXElement, Text

class EmptyArg(TeXElement):
    '''Type that represents an empty value in an Arguments list'''

    def __bool__(self):
        return False

    def source(self):
        return ''

class Arguments(Masterlist, TeXElement, MutableMapping):
    '''Represents a dictionary mapping argument names to values in a Macro or
    environment.'''

    #===========================================================================
    # Magic methods
    #===========================================================================
    def __init__(self, argspec, owner=None, data=None):
        self.owner = owner
        self._argspec = argspec
        Masterlist.__init__(self, [EmptyArg() for _ in self._argspec], owner)
        self.update(data or {})

    def __repr__(self):
        data = []
        for k, v in self.items():
            v = v.source() if isinstance(v, TeXElement) else str(v)
            data.append(''.join([k, '=', v]))
        data = ', '.join(data)
        return 'Arguments(%s)' % data

    def __len__(self):
        return Masterlist.__len__(self)

    def __getitem__(self, key):
        if isinstance(key, int):
            return Masterlist.__getitem__(self, key)
        for k, value in self.items():
            if k == key:
                return value
        else:
            return KeyError(key)

    def __setitem__(self, key, value):
        if value is None:
            return
        if isinstance(key, int):
            return Masterlist.__setitem__(self, key, value)

        for idx, k in enumerate(self.keys()):
            if k == key:
                return Masterlist.__setitem__(self, idx, value)
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        if isinstance(key, int):
            return Masterlist.__setitem__(self, key, EmptyArg())

        for idx, k in enumerate(self.keys()):
            if k == key:
                return Masterlist.__delitem__(self, idx)
        else:
            raise KeyError(key)

    def __copy__(self):
        new = Masterlist.__copy__(self)
        new._argspec = self._argspec
        new.owner = None

    def __deepcopy__(self, memo):
        memo[id(self)] = new = Masterlist.__deepcopy__(self, memo)
        new._argspec = deepcopy(self._argspec, memo)
        new.owner = None
        return new

    #===========================================================================
    # Dictionary interface
    #===========================================================================
    def items(self):
        '''Iterates over (argname, argvalue) in the correct order of arguments'''

        return zip(self._argspec, Masterlist.__iter__(self))

    def keys(self):
        return iter(self._argspec)

    def values(self):
        return iter(Masterlist.__iter__(self))

    def pop(self, idx=None):
        obj = self[idx or -1]
        del self[idx or -1]
        return obj

    #===========================================================================
    # TeXElement interface
    #===========================================================================
    def source(self, trunc=None):
        '''Return the source code for the collection of arguments'''

        source = []
        for k, v in self.items():
            spec = self.argspec[k]
            source.append(spec.source(v, trunc=trunc))
        return ''.join(source)

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def argspec(self):
        return self._argspec

#===============================================================================
# Argument casts
#===============================================================================
class DictListArg(UserDict, TeXElement):
    '''Mixed dict/list type that appear as argument in some LaTeX macros
    
    Example
    
    From a LaTeX source such as ['foo, bar, ham=spam'], we access elements 
    either by key or by index
    '''
    # TODO: reimplement this and move to the python types package

    def __init__(self, data={}):
        super(DictListArg, self).__init__(data)
        self.data.update(data)

    def source(self):
        items = []
        for k, v in self.items():
            if v is True:
                items.append(k)
            else:
                items.append('%s=%s' % (k, v.source()))
        return ', '.join(items)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
