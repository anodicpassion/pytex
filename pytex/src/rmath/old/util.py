import sympy as sp
from .symbols import CONSTANTS, FUNCTIONS

def list_constants(expr):
    '''Return the list of constants in expression.'''

    return [ x for x in CONSTANTS if x in sp.sympify(expr).atoms() ]

def list_functions(expr):
    '''Return the list of constants in expression.'''

    funcs = [ sp.Symbol(str(type(x))) for x in sp.sympify(expr).atoms(sp.Function) ]
    out = [ func for func in funcs if func in FUNCTIONS ]
    return out

def indent(st, level, first=True):
    '''Indent string to the given indentation level. 
    
    If ``first`` is False, does not indent the first line.'''

    indent = ' ' * level
    lines = st.splitlines()
    if first:
        lines[0] = indent + lines[0]
    for i in range(1, len(lines)):
        lines[i] = indent + lines[i]

    return '\n'.join(lines)


