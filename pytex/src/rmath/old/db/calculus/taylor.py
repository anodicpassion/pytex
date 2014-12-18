#from alttex.math.db_core import ctx_template
import sympy as sp

def series_to_poly(expr):
    pass

def taylor_poly(expr, order, x0=0, var=None, poly=True):
    ''''''

    # Return question
    expr = sp.sympify(expr)
    yield expr

    # Compute answer
    def answer():
        series = expr.series(var, n=order, x0=x0)
        return (series_to_poly(series) if poly else series)
    yield answer


    # Compute answer
    if x0:
        def distractor():
            series = expr.series(var, n=order)
            return (series_to_poly(series) if poly else series)
        yield distractor

#===============================================================================
# Define polynomials
#===============================================================================
#F_BASIC(x)
#x * F_BASIC(x)
#F_BASIC(F_BASIC(x))
#F_BASIC_1(x)
#(x + aa) ** (-BB)
#2 ** x

from sympy import sqrt
from sympy.abc import x, A

q, a, d = list(taylor_poly(sqrt(x), 3, A))
print(q, a(), d())
