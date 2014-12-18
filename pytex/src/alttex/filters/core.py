from pytex.util.texfy import TeXfy

FILTERS = {}

class SkipFilter(Exception):
    pass

def apply(filters, value):
    '''Apply a sequence of filters to value'''

    for f in filters:
        if callable(f):
            value = f(value)
        else:
            value = FILTERS[f](value)
    return value

def get_filter(name=None, dummy=False):
    '''Return the filter function with the given name. 
    
    If name is not given, return a dictionary mapping names to their respective
    registered filter functions.
    
    Non-existing filters raise an ValueError. If raises is False, return a dummy
    filter that simply transmits the argument as-is in the filter pipeline.
    '''

    if name is None:
        return FILTERS.copy()
    else:
        try:
            return FILTERS[name]
        except KeyError:
            if dummy:
                return lambda x: x
            raise ValueError('unknown filter: %r' % name)

def isfilter(*args):
    '''Decorator that marks a function as a filter. It can be called with an 
    explicit filter name or directly with a function object (in which case
    the function name is used as the filter name).
    
    Examples
    --------
    
    Let us associate the function foo() to the filter "foo" 
    
    >>> @isfilter
    ... def foo(x): return str(x)
    
    If the name of the function should be different from the filter name, it
    suffices to use
    
    >>> @isfilter('bar.foo')
    ... def foo(*x): return str(x)
    
    There is also the inline signature, if the function foo() is already 
    defined elsewhere
    
    >>> isfilter('foo.bar', foo)
    '''

    if len(args) == 2:
        name, func = args
        if name in FILTERS:
            raise ValueError('%s filter already exists' % name)
        FILTERS[name] = func
    else:
        x, = args
        if isinstance(x, str):
            def decorator(func):
                isfilter(x, func)
                return func
            return decorator
        else:
            name = x.__name__
            isfilter(name, x)
            return x

#===============================================================================
# Pytex standard filters
#===============================================================================
if __name__ == '__main__':
    import doctest
    doctest.testmod()
