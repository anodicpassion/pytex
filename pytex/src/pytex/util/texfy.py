from multidispatch import multifunction
import sympy as sp
from .text import escape_tex
from .. import textypes
from ..textypes import TeXElement

t = textypes
SIMPLE_CONVERSIONS = {
    str: t.TeXString,
    int: t.Integer,
}

def TeXfySimple(obj):
    '''TeXfy simple python immutable objects that have a direct TeXElement 
    translation'''

    if isinstance(obj, TeXElement):
        return obj
    try:
        tt = SIMPLE_CONVERSIONS[type(obj)]
    except KeyError:
        raise TypeError('%s object cannot be converted to TeX' % type(obj).__name__)
    return tt(obj)

def TeXfy(obj):
    '''Convert python object into the appropriate TeXElement'''

    if isinstance(obj, TeXElement):
        return obj
    try:
        return obj.texfy()
    except AttributeError:
        return texfy_other(obj)


@multifunction(None)
def texfy_other(x):
    data = escape_tex(str(x))
    return textypes.Text(data)

@texfy_other.dispatch(int)
def from_int(x):
    return textypes.Integer(x)

@texfy_other.dispatch(sp.Expr)
def from_sp(x):
    return textypes.TeXString(sp.latex(x))

