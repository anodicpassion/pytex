if __name__ == '__main__':
    import pytex; __package__ = 'pytex.textypes'  # @UnusedImport @ReservedAssignment

from . import TeXContainer
from ..context import Context

__all__ = ['TeXStream', 'TeXDocument', 'TeXPreamble', 'TeXBody']

#===============================================================================
# LaTeX documents: preamble, document, etc
#===============================================================================
class TeXStream(TeXContainer):
    '''A TeXStream is the most basic type of Group that can represent a working 
    document. It has a .context object that can hold information about package
    imports, a table of macros names, parsing environment variables, etc.
    
    The other derived TeXDocument assumes a "full" LaTeX document with a 
    preamble and a document environment.
    '''

    def __init__(self, children=None, *, context=None):
        TeXContainer.__init__(self, children=children)
        self._context = Context() if context is None else context

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    def revalue(self, method, *args, **kwds):
        '''Post-parsing of TeXStreams control useless whitespace in the begining
        or in the end of the TeX snippet.
        
        Trailing and leading whitespace and \par tokens are eliminated.'''

        TeXContainer.revalue(self, method, *args, **kwds)
        par = self.context.get_macro('par')

        # Remove empty whitespace from the beginning or the end of the stream
        for idx in [0, -1]:
            while self.children:
                obj = self.children[idx]

                if (isinstance(obj, str) and obj.isspace()) or isinstance(obj, par):
                    del self.children[idx]
                else:
                    break

        # Remove empty whitespaces trailing/ending whitespaces if the the
        # first/last element is a Text
        if self.children:
            first = self.children[0]
            if isinstance(first, str):
                post = first.lstrip()
                if post != first:
                    self.children[0] = post

        if self.children:
            last = self.children[-1]
            if isinstance(last, str):
                post = last.rstrip()
                if post != last:
                    self.children[-1] = post

        # Are we creating the children correctly?
        assert all(x.parent is self for x in self)
        return self

class TeXSubStream(TeXStream):
    '''A TeXStream-like object that is not meant to be the top-level document'''
    @property
    def context(self):
        return self.parent.context

    @context.setter
    def context(self, value):
        self.parent.context = value

class TeXPreamble(TeXSubStream):
    '''Represents the preamble part of a LaTeX document'''

class TeXBody(TeXSubStream):
    '''Represent the document part of a TeXDocument'''

    def source(self):
        return '\\begin{document}\n%s\n\\end{document}' % super(TeXBody, self).source()

class TeXDocument(TeXStream):
    '''Represents a TeX document'''

    def __init__(self, preamble, body, **kwds):
        if 'children' in kwds:
            raise TypeError('Cannot replace children of TeXDocuments: replace preamble and body elements instead')
        super(TeXDocument, self).__init__(**kwds)
        self.add(TeXPreamble(preamble))
        self.add(TeXBody(body))

    def source(self):
        return '%s\n\n%s' % (self.preamble.source(), self.document.source())

    def __str__(self):
        L = [type(self).__name__, '\n   |--', repr(self.preamble), '\n   \--', repr(self.document)]
        return ''.join(L)

    @property
    def preamble(self):
        try:
            # TODO: revert!
            return self.get(0)
        except IndexError:
            self.add(TeXPreamble())
            return self.get(0)

    @property
    def document(self):
        try:
            return self.get(1)
        except IndexError:
            self.preamble
            self.add(TeXBody())
            return self.get(1)

    @preamble.setter
    def preamble(self, value):
        self.preamble
        self.replace(0, value)

    @document.setter
    def document(self, value):
        self.document
        self.replace(1, value)

    @property
    def document_class(self):
        return self.document_class

if __name__ == '__main__':
    from pytex import *  # @UnusedWildImport

    tex = r'''\documentclass[a4]{article}
\usepackage[brazil]{babel}

\begin{document}
A \textbf{simple} \TeX{} document.
\end{document}
    '''
    job = TeXJob(tex)
    doc = job.parse()
    # print(doc.document_class)
    # print(doc)
    # print(doc.source())

