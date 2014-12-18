from .LaTeX import *
from pytex.textypes import Command

class ifundefined_(Command):
    macroName = '@ifundefined'
    args = 'name:str true:nox false:nox'
    def _invoke(self, tex):
        a = self.parse(tex)
        if a['name'] in self.ownerDocument.context:
            tex.pushTokens(a['false'])
        else:
            tex.pushTokens(a['true'])
        return []

class vwritefile_(Command):
    macroName = '@vwritefile'
    args = 'file:nox content:nox'

class pagelabel(Command):
    args = 'label:nox content:nox'

class verbatiminput(Command):
    pass

class makeatother(Command):
    def _invoke(self, tex):
        self.ownerDocument.context.catcode('@', 12)

# class makeatletter(Command):
#     def invoke(self, tex):
#         self.ownerDocument.context.catcode('@', 11)

class maketitle(Command):
    pass

from ... import package
package.LATEX = PACKAGE
