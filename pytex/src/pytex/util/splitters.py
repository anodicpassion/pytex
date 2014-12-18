__all__ = ['split_type', 'split_str', 'partition_type', 'partition_str',
           'strip', 'rstrip', 'lstrip']

#===============================================================================
# Splitting functions
#===============================================================================
def split_type(L, type_):
    '''Split a list L in sub-lists that are separated by elements of the given
    type
    
    Usage
    -----
    
    >>> L = [1, 2, 3, None, None, 5, None]
    >>> split_type(L, type(None))
    [[1, 2, 3], [], [5], []]
    
    >>> L = [None, 2, 3, None, 4]
    >>> split_type(L, type(None))
    [[], [2, 3], [4]]
    '''

    final = [[]]
    for elem in L:
        if isinstance(elem, type_):
            final.append([])
        else:
            final[-1].append(elem)
    return final

def split_str(L, sep):
    '''Split a list L in sub-lists separated by the given substring separator
    
    Usage
    -----
    
    >>> L = [1, 2, 'foo = bar', 3]
    >>> split_str(L, '=')
    [[1, 2, 'foo '], [' bar', 3]]
    
    >>> L = ['=1', '2=3=4' , '5']
    >>> split_str(L, '=')
    [[], ['1', '2'], ['3'], ['4', '5']]
    '''
    final = [[]]
    for elem in L:
        aux = None
        if isinstance(elem, str):
            for _ in range(elem.count(sep)):
                pre, aux, elem = elem.partition(sep)
                if pre:
                    final[-1].append(pre)
                if aux:
                    final.append([])
            if elem:
                final[-1].append(elem)
        else:
            final[-1].append(elem)

    return final

def partition_type(L, tt):
    if not L:
        return [], None, []

    pre, post = [], []
    for idx, elem in enumerate(L):
        if isinstance(elem, tt):
            L = list(L)
            post = L[min(idx + 1, len(L) - 1):]
            return pre, elem, post
        pre.append(elem)
    else:
        return L, None, []


def partition_str(L, sep):
    r'''Partition a list L into two sublists separented by some string separator
    sep. Return (list 1, sep, list 2).
    
    Example
    -------
    
    >>> L = [1, 2, 'foo = bar', 3]
    >>> partition_str(L, '=')
    ([1, 2, 'foo '], '=', [' bar', 3])
    '''
    if not L:
        return [], '', []

    pre, post = [], []
    for idx, elem in enumerate(L):
        if isinstance(elem, str):
            pre_e, sep_e, pos_e = elem.partition(sep)
            if sep_e:
                pre.append(pre_e)
                if pos_e:
                    post.append(pos_e)
                if idx < len(L) - 1:
                    post.extend(L[idx + 1:])
                return pre, sep, post
        pre.append(elem)
    else:
        return L, '', []


#===============================================================================
# Whitespace control
#===============================================================================
def strip(L):
    r'''Clean all empty whitespace in the begining or in the end of the list L
    
    Example
    -------
    
    >>> L = ['\n', ' ', 1, 2, 3, ' \n']
    >>> strip(L)
    [1, 2, 3]
    '''

    return lstrip(rstrip(L))

def rstrip(L):
    while L:
        elem = L[-1]
        try:
            if elem.isspace():
                L.pop()
            else:
                new = elem.rstrip()
                if new != elem:
                    L[-1] = new
                break
        except AttributeError:
            break
    return L

def lstrip(L):
    while L:
        elem = L[0]
        try:
            if elem.isspace():
                L.pop(0)
            else:
                new = elem.lstrip()
                if new != elem:
                    L[0] = new
                break
        except AttributeError:
            break
    return L

if __name__ == '__main__':
    import doctest
    doctest.testmod()
