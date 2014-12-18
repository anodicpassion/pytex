'''
Functions that control the default complexity value
'''
GLOBAL_COMPLEXITY = 6

def read_complexity(value):
    '''Return the global complexity if value is default or the given 
    complexity'''

    if value is None:
        return GLOBAL_COMPLEXITY
    else:
        return value

def get_global_complexity():
    '''Returns the current global complexity'''

    return GLOBAL_COMPLEXITY

def set_global_complexity(value):
    '''Returns the current global complexity'''

    global GLOBAL_COMPLEXITY
    GLOBAL_COMPLEXITY = value

__all__ = ['get_global_complexity', 'set_global_complexity', 'read_complexity']
