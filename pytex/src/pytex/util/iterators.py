__all__ = ['bufferediter', 'walk_items', 'iter_items']

class bufferediter:
    """Buffered iterator. Items can be pushed to the main iteration."""

    def __init__(self, obj):
        self._iter = iter(obj)
        self._buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer:
            return self._buffer.pop()
        return next(self._iter)

    def push(self, value):
        '''Add a single value to buffer'''
        self._buffer.append(value)

    def push_many(self, values):
        '''Add a sequence of values to buffer'''
        self._buffer.extend(values)

#===============================================================================
# Iterates over TeX documents
#===============================================================================
# Iteration functions are used to query objects of specific types or with
# specific properties among the children.
#
# The walk_* functions iterate over all children and the children's children
# recursivelly. iter_* functions do not use recursion
#

def _normalize_type(obj, name):
    '''Convert a latex name into the corresponding type (e.g. "\par" is 
    pointed to the macro \par. Used internally by the walk_items and 
    iter_items functinos'''

    if isinstance(name, type):
        return name

    # Recognize environments
    elif name.startswith('\\begin{'):
        return obj.context.get_environment(name[7:-1])

    # Recognize object as a Macro
    elif name.startswith('\\'):
        return obj.context.get_macro(name[1:])

    else:
        raise ValueError('unrecognized type: %s' % name)

def walk_items(obj, item_type=None, **filters):
    '''Like iter_items(), but works recursivelly in the children of each 
    children'''
    item_type = _normalize_type(obj, item_type or object)

    if isinstance(obj, item_type):
        for (k, v) in filters.items():
            if getattr(obj, k) != v:
                break
        else:
            yield obj

    if hasattr(obj, '_subitems_'):
        for item in obj._subitems_():
            yield from walk_items(item, item_type, **filters)

def iter_items(obj, item_type=None, **kwds):
    '''Iterate over all items of the given type amongst the children.
    
    The parameter item_type can be a subclass of TeXElement() or a string
    that represents the given subclass. The following string conversions
    are accepted:
    
    * macros: strings of the form r"\macro" are converted into the class that 
    implements the corresponding macro.
    
    * environments: environments are represented by strings of the form 
    r"\begin{envname}"
    
    '''
    item_type = _normalize_type(obj, item_type)

    for item in obj._subitems_():
        if isinstance(item, item_type):
            for (k, v) in kwds.items():
                if getattr(item, k) != v:
                    break
            else:
                yield item
