from collections import MutableMapping

class NestedDict(MutableMapping):
    '''Represent nested mappings.
    
    The example shows how to use it
    
    >>> ns = NestedDict(foo=1); ns
    NestedDict({'foo': 1})
    
    Now we go up one level and modify the dictionary
    
    >>> ns.up()
    >>> ns['bar'] = 2; ns
    NestedDict({'foo': 1, 'bar': 2})
    
    We can shadow a variable from a lower level
    
    >>> ns.up()
    >>> ns['foo'] = 3; ns
    NestedDict({'foo': 3, 'bar': 2})
    
    Finally, we recover the base versions of the dictionary, by going down() 
    and discarding changes 
    
    >>> ns.down(); ns
    NestedDict({'foo': 1, 'bar': 2})
    >>> ns.down(); ns
    NestedDict({'foo': 1})
    
    We can't go down indefinitely...
    
    >>> ns.down()
    Traceback (most recent call last):
    ...
    ValueError: already in the lowest level of dictionary
    '''

    def __init__(self, data=None, **kwds):
        self._data = [{}]
        self.update(data or {})
        self.update(kwds)

    def up(self, dic=None):
        '''Create a new level in the namespace object'''
        self._data.append(dic if dic is not None else {})

    def down(self):
        '''Discard the last level in the namespace object'''
        if len(self._data) == 1:
            raise ValueError('already in the lowest level of dictionary')
        self._data.pop()

    def __delitem__(self, key):
        for d in reversed(self._data):
            if key in d:
                del d[key]
                break
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        for d in reversed(self._data):
            if key in d:
                return d[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        used = {...}
        for d in self._data:
            for k in d:
                if k not in used:
                    used.add(k)
                    yield k

    def __len__(self):
        return sum(1 for _ in self)

    def __setitem__(self, key, value):
        self._data[-1][key] = value

    def __repr__(self):
        data = ', '.join('%r: %r' % item for item in self.items())
        return 'NestedDict({%s})' % data

if __name__ == '__main__':
    import doctest
    doctest.testmod()