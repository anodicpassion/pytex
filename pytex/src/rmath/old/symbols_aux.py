#===============================================================================
# Special functions
#===============================================================================
# TODO: create separate classes for all the functions bellow
from sympy.abc import a, b, c, d, x
from sympy import Lambda, Rational, log

linear = Lambda(x, a + x)
third = Rational(1, 3)
quadratic = Lambda(x, a + b * x + x ** 2)
cubic = Lambda(x, a + b * x + c * x ** 2 + x ** 3)
quartic = Lambda(x, a + b * x + c * x ** 2 + d * x ** 3 + x ** 4)
cubicroot = Lambda(x, x ** third)
rational_11 = Lambda(x, (a + x) / (b + x))
rational_12 = Lambda(x, (a + x) / (b + c * x + x ** 2))
rational_21 = Lambda(x, (a + b * x + x ** 2) / (c + x))
rational_22 = Lambda(x, (a + b * x + x ** 2) / (c + d * x + x ** 2))
log10 = Lambda(x, log(x, 10, evaluate=False))
log2 = Lambda(x, log(x, 2, evaluate=False))

__all__ = ['linear', 'third', 'quadratic', 'cubic', 'quartic', 'cubicroot',
           'rational_11', 'rational_12', 'rational_21', 'rational_22',
           'log10', 'log2']
