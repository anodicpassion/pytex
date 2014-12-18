if __name__ == '__main__':
    import rmath.mutators #@UnusedImport
    __package__ = 'rmath.mutators' #@ReservedAssignment

from collections import namedtuple
import random
import sympy as sp
from .util import mutate_up, keep_sign

op_tuple = namedtuple('op_tuple', ['operator', 'numargs'])

def _polish_worker(formula, rpn=True):
    '''Implementation for polish and rpolish'''

    formula = sp.sympify(formula)
    if not formula.args:
        return [formula]
    else:
        op = op_tuple(type(formula), len(formula.args))
        L = [] if rpn else [op]
        for arg in map(_polish_worker, formula.args):
            L.extend(arg)
        if rpn:
            L.append(op)
        return L

def polish(formula):
    '''Convert expression to a list in the direct polish notation (DPN).
    
    Operators are converted into a named tuple of (operator, numargs). This is 
    necessary to remove ambiguity of operators which can have a variable number
    of arguments.
    '''

    return _polish_worker(formula, False)

def rpolish(formula):
    '''Convert an expression to a list in the reverse polish notation (RPN).
    
    Operators are converted into a named tuple of (operator, numargs). This is 
    necessary to remove ambiguity of operators which can have a variable number
    of arguments.
    '''

    return _polish_worker(formula, True)

def from_polish(L):
    '''Compute formula from its DPN representation'''

    aux = []
    L = list(L)

    while L:
        last = L.pop()
        if isinstance(last, op_tuple):
            op, N = last
            args = aux[:N]
            aux = aux[N:]
            L.append(op(*args))
        else:
            aux.insert(0, last)

    assert len(aux) == 1, 'invalid aux: %s' % aux
    return aux[0]


def from_rpolish(L):
    '''Compute formula from its RPN representation'''

    L = list(L)
    stack = []
    for obj in L:
        if isinstance(obj, op_tuple):
            op, N = obj
            args = reversed([stack.pop() for _ in range(N)])
            obj = op(*args)
        stack.append(obj)

    return obj

#===============================================================================
# Expressions
#===============================================================================
# TODO: make this programmatically
RPN_MUTATE_CLASSES = {
    sp.cos: [sp.sin, sp.cos, sp.tan, sp.sec, sp.csc],
}
def rpn_atomic_mutate(atom):
    '''Mutate expression by changing one element from its RPN representation'''

    if isinstance(atom, op_tuple) and atom.operator in RPN_MUTATE_CLASSES:
        cls = RPN_MUTATE_CLASSES[atom.operator]
        return op_tuple(random.choice(cls), atom.numargs)
    elif isinstance(atom, sp.Rational):
        return atom + random.choice([1, 2, -1, -2])
    else:
        return atom

@keep_sign
@mutate_up
def mutate_expr(formula):
    '''Mutate the given formula by changing values from its RPN representation'''

    return from_rpolish(mutate_rpn(rpolish(formula)))

def mutate_rpn(rpn):
    order = list(range(len(rpn)))
    random.shuffle(order)
    for idx in order:
        atom = rpn[idx]
        subs = rpn_atomic_mutate(atom)
        if subs != atom:
            rpn[idx] = subs
            return rpn

if __name__ == '__main__':
    e1 = sp.cos(sp.var('x')) ** 2
    e2 = sp.exp(1)

    print(rpolish(e1))
    print(from_rpolish(rpolish(e1)))
    print(mutate_expr(e1))
    #print(distractors([e1, e2]))
