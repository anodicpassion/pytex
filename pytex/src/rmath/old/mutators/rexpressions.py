import random
import sympy as sp



def is_var_atom(x):
    '''Return True if object is a spec variable'''

    return isinstance(x, sp.Symbol)


def get_spec(formula):
    atoms = [ x for x  in formula.atoms() if is_var_atom(x) ]
    print(get_spec)

def apply_spec(formula, spec):
    pass

def distractors(init):
    '''Generator that yields unique expressions similar to the ones in the 
    list init.
    
    The resulting expressions can be used as distractors in a multiple-choice
    test. '''


