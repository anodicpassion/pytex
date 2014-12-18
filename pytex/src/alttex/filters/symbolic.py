from pytex.util.texfy import TeXfy
from pytex.alttex.filters import isfilter
import sympy as sp

#===============================================================================
# Vector representations
#===============================================================================
def _comp_convert(x):
    if x == 1:
        return ''
    elif x == -1:
        return '-'
    txt = TeXfy(x).source()
    if isinstance(x, sp.Add):
        txt = '\\left(%s\right)' % txt
    return txt

def _plus(x):
    if x.startswith('-'):
        return x
    else:
        return '+ ' + x

@isfilter
def uvector(v):
    r'''Convert a vector (a,b,c) into a string using the unit vector notation,
    i.e.,
    
    >>> uvector((1, 2, 3))
    ' \\mathbf{i} + 2 \\mathbf{j} + 3 \\mathbf{k}'
    
    If the vector/list has more than 3 components, uses the unit basis 
    e_1, e_2, etc.
    '''

    components = [ _comp_convert(x) for x in v if x ]
    if not components:
        return '0'

    if len(v) <= 3:
        base = list('ijk'[:len(v)])
    else:
        base = ['e_{%s}' % i for i in range(1, len(v) + 1)]
    base = ['\\mathbf{%s}' % x for x in base ]

    # Create string concatenating all components
    head, *tail = zip(components, base)
    expr = [ '%s %s' % head ]
    expr.extend('%s %s' % (_plus(c), b) for (c, b) in tail)
    return ' '.join(expr)
