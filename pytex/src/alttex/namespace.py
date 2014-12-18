import contextlib

class Namespace:
    '''Namespace objects are used inside Python scripts in order to export 
    variables to a LaTeX document.
    '''

    def __init__(self, data=None):
        data = {} if data is None else data
        self.__dict__['_data'] = data
        self.__dict__['_defs'] = []

    @contextlib.contextmanager
    def display_defs(self, title='Variables'):
        '''Display all variables defined inside the with block
        
        Example
        -------
        
        >>> ns = Namespace()
        >>> with ns.display_defs('Initial coords'):
        ...     ns.x = 1
        ...     ns.y = 2
        ...     ns.z = 3
        Initial coords
        --------------
            x = 1
            y = 2
            z = 3
        '''
        # __enter__()
        self._defs[:] = []

        yield

        # __close__()
        print(title)
        print('-' * len(title))
        for k in self._defs:
            print('  %s = %r' % (k, self._data[k]))
        self._defs[:] = []


    # Magical methods ----------------------------------------------------------
    def __iter__(self):
        return iter(self._data.items())

    def __setattr__(self, attr, value):
        if attr.isalnum():
            self._data[attr] = value
            self._defs.append(attr)
        else:
            raise AttributeError('invalid variable name: %r, only letters and numbers are accepted' % attr)

    def __getattr__(self, attr):
        try:
            return self._data[attr]
        except KeyError:
            raise AttributeError(attr)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
