import sympy as sp
from alttex.math.db_core.symbols import * #@UnusedWildImport
from alttex.math import db_core as core
import random

class convergent(core.Factory):
    integer_constants = True
    positive_constants = True

    # Simple negative powers
    template_0 = sp.Integral(1 / ((x + A) * (x + B)), (x, C, sp.oo))
    conds_0 = [sp.Ne(A, B)]

    # Exponential
    template_1 = sp.Integral(x * sp.exp(-A * (x - B)), (x, B, sp.oo))

    # Power and logarithm 
    template_2 = sp.Integral(1 / (x * (sp.ln(x)) ** P), (x, D, sp.oo))
    conds_2 = [core.Domain(A, [1, 2])]

class divergent(Factory):
    integer_constants = True
    positive_constants = True

    # Simple negative powers
    template_0 = sp.Integral(1 / ((x + A) * (x + B)), (x, C, sp.oo))
    conds_0 = [sp.Ne(A, B)]


if __name__ == '__main__':
    from alttex.math.db_core import display_module
    display_module()

    a = convergent()
    a.pprint()
    sp.pprint(a.answer())
