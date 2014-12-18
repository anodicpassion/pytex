from rmath.complexity import complexity as _complexity

def issimple(obj, max_complexity=5):
    '''
    Return True if object's complexity is less then or equal to ``max_complexity``
    
    Examples
    --------
    
    >>> issimple(6)
    True
    >>> issimple(6, 2)
    False
    '''
    return round(_complexity(obj)) <= max_complexity

def assure_simple(obj, max_complexity=5):
    '''
    Raises an AssertionError if object's complexity is greater than 
    ``max_complexity``.
    '''
    compl = round(_complexity(obj))
    if not(compl <= max_complexity):
        msg = 'complexity of %s greater than the maximum complexity %s'
        msg = msg % (compl, max_complexity)
        raise AssertionError(msg)
