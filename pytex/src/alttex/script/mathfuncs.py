from sympy import diff, cos, sin, exp, tan, atan, asin, acos, sqrt
from sympy.abc import x, y, z  #@UnresolvedImport

def rot(F, x=x, y=y, z=z):
    '''Returns the rotational of a vector field F with respect to the variables
    x, y, z.
    
    The output is a sequence of components, but it may change to a Vector 
    instance in the future.
    
    Examples
    --------
    
    >>> rot((x, y, z))
    (0, 0, 0)
    
    >>> rot((-y, x, 0))
    (0, 0, 2)
    '''

    fx, fy, fz = fill(F, 3)
    rotx = diff(fz, y) - diff(fy, z)
    roty = diff(fx, z) - diff(fz, x)
    rotz = diff(fy, x) - diff(fx, y)
    return (rotx, roty, rotz)

def div(F, x=x, y=y, z=z):
    '''Returns the divergence of a vector field F with respect to the variables
    x, y, z. 
    
    Examples
    --------
    
    >>> div((x, y, z))
    3
    '''

    fx, fy, fz = fill(F, 3)
    return diff(fx, x) + diff(fy, y) + diff(fz, z)

def fill(F, size, fill=0):
    '''Iterates over a sequence and  by pads with the fill until the given size 
    is reached.
    
    Raises an ValueError if is of length greater than size.'''

    for i, x in enumerate(F):
        if i >= size:
            raise ValueError('F did not finish after %s iterations' % size)
        yield x

    i += 1
    while i < size:
        i += 1
        yield fill

def dot(v1, v2):
    '''The dot product between two vectors'''

    return sum(x * y for (x, y) in zip(v1, v2))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
