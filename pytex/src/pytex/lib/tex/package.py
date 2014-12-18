if __name__ == '__main__':
    import pytex; __package__ = 'pytex.lib.tex'  # @ReservedAssignment @UnusedImport

from ...package import Package
from ...textypes import Command

PACKAGE = Package('@TeX')

PACKAGE.add_commands(r'''
% base control flow commands
\relax
\protect
\global
\hfil

% conditionals
\fi
\else 

% spacing
\leavemode
\kern
\hrule
\long
\undefined

% spacing internal
\@undefined
\@vobeyspaces
\@noligs

% spacing
\vskip{size:dimen}
\hskip{size:dimen}
''')

class par(Command):
    r'''\par ==> divide paragraphs in a TeX document'''

    @classmethod
    def invoke(cls, job, tokens):
        '''Ignore multiple \par tokens'''

        par = tok = tokens.get_macro('par')
        while tok == par:
            tok = tokens.get_next(None)
        tokens.push(tok)
        return cls()

    def source(self):
        return '\n\n'

    def isspace(self):
        return True

class endinput(Command):
    r'''\endinput ==> Consume all tex tokens'''

    @classmethod
    def invoke(self, job, tokens):
        for _ in tokens:
            pass

class jobname(Command):
    r'''\jobname ==> Expand to the name of the current job'''

    def expand(self, job, tokens):
        tokens.push_text(job.context.jobname)
