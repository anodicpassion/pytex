# The other exports are added programmatically.
# These include all NNa, NNb, ..., ZZa, ZZb, ... proxies
__all__ = ['reset_proxy']

#===============================================================================
# Base Proxy class
#===============================================================================
class FactoryProxy:
    '''Façade to a delegate object created from a factory function.
    
    The delegate is only created on-demand if some method/attribute of the 
    Proxy instance is required in some computation. All instances that were
    initialized are registered in the FactoryProxy.PROXY_INITIALIZED list.
    
    The ``reset_proxy()`` function reset all initialized ``FactoryProxy`` 
    instances.
    
    Examples
    --------
    
    >>> a = FactoryProxy(int, (1,))
    >>> a, a + a, 2 + a
    (1, 2, 3)
    '''

    PROXY_INITIALIZED = []

    def __init__(self, func, args=(), kwds={}):
        self.__dict__['_func'] = func
        self.__dict__['_args'] = tuple(args)
        self.__dict__['_kwds'] = dict(kwds)

    def __getattr__(self, attr):
        '''Delegates attribute to _proxy_delegate'''

        if '_proxy_delegate' not in self.__dict__:
            delegate = self._func(*self._args, **self._kwds)
            self.__dict__['_proxy_delegate'] = delegate
            self.PROXY_INITIALIZED.append(self)
        if attr == '_proxy_delegate':
            return self._proxy_delegate
        return getattr(self._proxy_delegate, attr)

    def __setattr__(self, attr, value):
        setattr(self._delegate, attr, value)

    @classmethod
    def __add_method(cls, name):
        '''Adds new methods to the class'''

        def generic(self, *args):
            method = getattr(self._proxy_delegate, name)
            args = (getattr(arg, '_proxy_delegate', arg) for arg in args)
            return method(*args)
        generic.__name__ = name
        setattr(cls, name, generic)

# Special methods taken from int, float, str, list, dict 
for method in ['__abs__', '__bool__', '__ceil__', '__float__', '__floor__',
               '__hash__', '__index__', '__int__', '__invert__',
               '__iter__', '__len__', '__neg__', '__pos__', '__pow__',
               '__repr__', '__reversed__', '__round__', '__setitem__',
               '__sizeof__', '__str__', '__trunc__']:
    FactoryProxy._FactoryProxy__add_method(method)

for method in ['__add__', '__and__', '__contains__', '__delitem__',
               '__divmod__', '__eq__', '__floordiv__', '__format__', '__ge__',
               '__getitem__', '__gt__', '__iadd__', '__iand__', '__imul__',
               '__ior__', '__isub__', '__ixor__', '__le__', '__lshift__',
               '__lt__', '__mod__', '__mul__', '__ne__', '__or__', '__radd__',
               '__rand__', '__rdivmod__', '__rfloordiv__', '__rlshift__',
               '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
               '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__sub__',
               '__truediv__', '__xor__']:
    FactoryProxy._FactoryProxy__add_method(method)

class SharedProxy(FactoryProxy):
    '''Subclass of FactoryProxy in which instances share the `func`, `args`, 
    and `kwds` attributes.'''
    _args = ()
    _kwds = {}
    def __init__(self):
        if not hasattr(self, '_func'):
            raise ValueError('type must provide a _func method')

#===============================================================================
# Utility functions
#===============================================================================
def reset_proxy():
    '''Globally reset all proxy instances
    
    Examples
    --------
    
    >>> import random; random.seed(0)
    >>> a = FactoryProxy(random.random)
    >>> b = FactoryProxy(random.random)
    >>> a, b
    (0.8444218515250481, 0.7579544029403025)
    >>> reset_proxy()
    >>> a, b
    (0.420571580830845, 0.25891675029296335)
    '''

    for var in FactoryProxy.PROXY_INITIALIZED:
        if '_proxy_delegate' in var.__dict__:
            del var.__dict__['_proxy_delegate']

    FactoryProxy.PROXY_INITIALIZED = FactoryProxy.PROXY_INITIALIZED[:]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
