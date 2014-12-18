import sympy as sp
from rmath.symbols_aux import *

GLOBALS = globals()
old_globals = dict(GLOBALS)

#===============================================================================
# Symbol constants and the pos and neg counterparts
#===============================================================================
# TODO: make explicit sign assumptions
CONSTANTS = []

# Regular numeric constants
for tt in ['NN', 'ZZ', 'ZP', 'QQ', 'QP', 'RR', 'RP', 'CC', 'CQ', 'CZ', 'CN',
           'THETA', 'THETAP', 'SIGN', 'BOOL']:
    for _ in 'abcdefghijklmnopqrstuvwxyz':
        aux = _ * 2
        GLOBALS[aux] = _pos_ = sp.Symbol(aux)
        aux = _.lower() * 2
        GLOBALS[aux] = _neg_ = sp.Symbol(aux)
        CONSTANTS.extend([_pos_, _neg_])

# Angle/Sign/Bool constants
for cls in ['theta', 'sign', 'bool']:
    for i in range(0, 21):
        aux = '%s_%s' % (cls.upper(), i)
        GLOBALS[aux] = pos = sp.Symbol(aux)
        aux = '%s_%s' % (cls, i)
        GLOBALS[aux] = neg = sp.Symbol(aux)
        CONSTANTS.extend([pos, neg])

#===============================================================================
# Expression constants
#===============================================================================
EXPRESSIONS = []
for _ in range(21):
    _expr_ = sp.Symbol('EXPR%s' % _)
    EXPRESSIONS.append(_expr_)
    GLOBALS[str(_expr_)] = _expr_

#===============================================================================
# Functions constants
#===============================================================================
FUNCTIONS = {}
FUNCTIONS_ACCUMULATED = {}
FUNCTION_CLASSES = {}

# Hyperbolic functions ---------------------------------------------------------
TRIGH_F0 = sp.Symbol('TRIGH_F0')
TRIGH_F1 = sp.Symbol('TRIGH_F1')
TRIGH_F2 = sp.Symbol('TRIGH_F2')
FUNCTIONS[TRIGH_F0] = [sp.sinh, sp.cosh]
FUNCTIONS[TRIGH_F1] = [sp.tanh, sp.coth]
FUNCTIONS[TRIGH_F2] = [sp.atanh, sp.acoth, sp.asinh, sp.acosh]
FUNCTION_CLASSES['TRIGH'] = [TRIGH_F0, TRIGH_F1, TRIGH_F2]

# Inverse Trigonometric functions ----------------------------------------------
INVTRIG_F0 = sp.Symbol('INVTRIG_F0')
INVTRIG_F1 = sp.Symbol('INVTRIG_F1')
FUNCTIONS[INVTRIG_F0] = [sp.atan, sp.acot, sp.asin, sp.acos]
FUNCTIONS[INVTRIG_F1] = [] # inverse sec and csc are not yet implemented
FUNCTION_CLASSES['INVTRIG'] = [INVTRIG_F0, TRIGH_F1]

# Trigonometric functions ------------------------------------------------------
TRIG_F0 = sp.Symbol('TRIG_F0')
TRIG_F1 = sp.Symbol('TRIG_F1')
TRIG_F2 = sp.Symbol('TRIG_F2')
FUNCTIONS[TRIG_F0] = [sp.sin, sp.cos]
FUNCTIONS[TRIG_F1] = [sp.tan, sp.cot, sp.sec, sp.csc]
FUNCTIONS[TRIG_F2] = FUNCTIONS[INVTRIG_F0] + FUNCTIONS[INVTRIG_F1]
FUNCTION_CLASSES['TRIG'] = [TRIG_F0, TRIG_F1, TRIG_F2]

# Pré-calculus functions -------------------------------------------------------
PRECALC_F0 = sp.Symbol('PRECALC_F0')
PRECALC_F1 = sp.Symbol('PRECALC_F1')
PRECALC_F2 = sp.Symbol('PRECALC_F2')
FUNCTIONS[TRIG_F0] = [linear]
FUNCTIONS[TRIG_F1] = [quadratic, sp.sqrt]
FUNCTIONS[TRIG_F2] = [cubic, rational_11] # ...
FUNCTION_CLASSES['PRECALC'] = [PRECALC_F0, PRECALC_F1, PRECALC_F2]

# Basic functions --------------------------------------------------------------
BASIC_F0 = sp.Symbol('BASIC_F0')
BASIC_F1 = sp.Symbol('BASIC_F1')
BASIC_F2 = sp.Symbol('BASIC_F2')
BASIC_F3 = sp.Symbol('BASIC_F3')
FUNCTIONS[BASIC_F0] = [sp.exp, sp.log, sp.sqrt] + FUNCTIONS[TRIG_F0]
FUNCTIONS[BASIC_F1] = [log10, log2, cubicroot] + FUNCTIONS[TRIG_F1]
FUNCTIONS[BASIC_F2] = FUNCTIONS[TRIG_F2] + FUNCTIONS[TRIGH_F0] + FUNCTIONS[TRIGH_F1]
FUNCTIONS[BASIC_F3] = FUNCTIONS[TRIGH_F2]
FUNCTION_CLASSES['BASIC'] = [BASIC_F0, BASIC_F1, BASIC_F2, BASIC_F3]

# Simple functions -------------------------------------------------------------
SIMPLE_F0 = sp.Symbol('SIMPLE_F0')
SIMPLE_F1 = sp.Symbol('SIMPLE_F1')
SIMPLE_F2 = sp.Symbol('SIMPLE_F2')
SIMPLE_F3 = sp.Symbol('SIMPLE_F3')
FUNCTIONS[SIMPLE_F0] = FUNCTIONS[BASIC_F0] + [linear]
FUNCTIONS[SIMPLE_F1] = FUNCTIONS[BASIC_F1] + [quadratic, rational_11]
FUNCTIONS[SIMPLE_F2] = FUNCTIONS[BASIC_F2] + [cubic, rational_12, rational_21]
FUNCTIONS[SIMPLE_F3] = FUNCTIONS[BASIC_F3] + [quartic, rational_22]
FUNCTION_CLASSES['SIMPLE'] = [SIMPLE_F0, SIMPLE_F1, SIMPLE_F2, SIMPLE_F3]

# Clean namespace
del sp, GLOBALS, old_globals
