if __name__ == '__main__':
    import pytex; __package__ = 'pytex.util'  # @ReservedAssignment @UnusedImport

import traceback
import sys
from pygments import highlight
from pygments.lexers import PythonLexer  # @UnresolvedImport
from pygments.formatters import LatexFormatter  # @UnresolvedImport
from .text import print_capture
from .rawtex import tex_document

PYGMENTS_DEFS = LatexFormatter().get_style_defs().strip()

def render_error(etype=None, evalue=None, tb=None, as_document=False):
    r'''Renders the last traceback as LaTeX code. The resulting code uses 
    pygments for syntax highlighting. If no traceback object is given, the last
    traceback is used.
    
    Example
    -------
    
    >>> try:
    ...     1/0
    ... except:
    ...     print(render_error())                        #doctest: +ELLIPSIS
    \makeatletter...
    \begin{Verbatim}[commandchars=\\\{\}]
    \PY{n}{Traceback}...
    \end{Verbatim}
    '''

    if evalue is None:
        etype, evalue, tb = sys.exc_info()

    with print_capture(capture_errors=True) as tbcode:
        traceback.print_exception(etype, evalue, tb)

    return  highlight(tbcode, PythonLexer(), LatexFormatter(full=as_document))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
