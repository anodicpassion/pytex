if __name__ == '__main__':
    import pytex; __package__ = 'pytex.textypes'  # @UnusedImport @ReservedAssignment

from . import TeXString, Environment, Join, Alignment, Text, Group
from ..types.argspec import Argspec
from ..util.text import indent
from ..util.splitters import split_type, strip

#===============================================================================
# Itemize
#===============================================================================
class Item(Group):
    '''Base class for all \item commands inside a itemize environment'''
    trim_newlines = True

    def __init__(self, data, item_name=None):
        super(Item, self).__init__('', data, '')
        self.item_name = item_name or 'item'

    def source(self):
        return '  \%s %s' % (self.item_name, indent(self.children_source(), 4, False))

class Itemize(Environment):
    '''Base class for all itemize-like environments such as enumerate, 
    description, etc.'''

    has_preamble = False
    item_command = 'item'

    @classmethod
    def invoke_body(cls, job, tokens, new):
        item_cmd = job.get_macro(cls.item_command)
        body = super(Itemize, cls).invoke_body(job, tokens, new)
        body = split_type(body, item_cmd)
        if len(body[0]) == 1 and not body[0][0].strip():
            body[0] = []

        # Check the existence of a preamble element
        if (not cls.has_preamble) and body[0]:
            raise ValueError('unexpected preamble in class: %s' % body[0])
        elif cls.has_preamble:
            new.children.append(Join.as_element(body.pop(0)))
        else:
            del body[0]

        # Convert all lists to Item groupings
        body = [Item(x, item_name=cls.item_command) for x in body]
        return body

    def children_source(self):
        return '\n'.join(x.source() for x in self.children)

#===============================================================================
# Tabular
#===============================================================================
class TabularLine(Join):
    argspec = Argspec('{top:tok}{bottom:tok}')
    is_abstract = True

    def __init__(self, data, top=None, bottom=None):
        # Initialize arguments
        self.args = self.argspec.new_arguments()
        if top is not None:
            self.args['top'] = top
        if bottom is not None:
            self.args['bottom'] = bottom

        # Initialize lists
        super(TabularLine, self).__init__(data)

    def as_line(self):
        return list(self.children)

    def source(self):
        top = self.top.source() + ('\n' if self.top else '')
        bottom = self.bottom.source() + ('\n' if self.bottom else '')
        return '%s%s \\tabularnewline\n%s' % (top, ' & '.join(x.source() for x in self), bottom)

    def lineon(self, pos):
        pass

    def lineoff(self, pos):
        pass

    top = argspec.get_property('top')
    bottom = argspec.get_property('bottom')

TabularLine.argspec.owner = TabularLine

class Tabular(Environment):
    # TODO: make \\ maps to \tabularnewline and break lines on \tabularnewline's
    argspec = '{colspec:str}'

    def __init__(self, data, alignment=None, lines=True):
        super(Tabular, self).__init__()
        for L in data:
            self.children.append(TabularLine(L))
        if lines:
            self.children[0].lineon('top')
            for L in self.children:
                L.lineon('bottom')

        # Set alignment
        self.colspec = Text('c' * len(self.children))

    @classmethod
    def empty(cls, rows, cols, alignment=None, lines=True):
        data = [[ Text('') for _ in range(cols) ] for _ in range(rows) ]
        return cls(data, alignment=None, lines=True)

    # Iterations ---------------------------------------------------------------
    def iter_cells(self, transpose=False):
        rows, cols = self.shape
        if transpose:
            for i in range(rows):
                for j in range(cols):
                    yield self[i][j]
        else:
            for i in range(cols):
                for j in range(rows):
                    yield self[j][i]

    def set_alignment(self, align):
        '''Define the alignment of all colums in the table to either 'left', 'right'
        or 'center'.'''

        align = align[0]
        self.colspec = align * self.cols

    # Tabular initialization ---------------------------------------------------
    @classmethod
    def new(cls):
        '''A constructor that takes no arguments'''

        obj = Environment.__new__(cls)  # @UndefinedVariable
        Environment.__init__(obj)
        return obj

    @classmethod
    def invoke_body(cls, job, tokens, new):
        tabularnewline = job.get_macro(r'\\')
        body = super(Tabular, cls).invoke_body(job, tokens, new)
        if any(x.macro_name == 'tabularnewline' for x in body):
            tabularnewline = job.get_macro(r'tabularnewline')
        body = strip(body)
        body = split_type(body, tabularnewline)
        body = [[[], L, []] for L in body]
        # Collect \hlines
        for (pre, L, _) in body:
            if not L:
                continue
            while L and L[0].macro_name in ['hline']:
                pre.append(L.pop(0))

        # Move \hlines of last line, if line is empty
        if len(body) >= 2 and not body[-1][1]:
            body[-2][2].extend(body[-1][0])
            del body[-1]

        # Move one of doubled \hlines to the bottom position of the previous line
        for idx, (pre, L, _) in enumerate(body):
            if sum(x.macro_name == 'hline' for x in pre) == 2:
                for i, x in enumerate(pre):
                    if x.macro_name == 'hline':
                        body[idx - 1][-1].append(pre.pop(i))

        # Transform lists into elements
        for idx, (pre, L, pos) in enumerate(body):
            # Split L in Alignments
            L = split_type(L, Alignment)
            L = strip(L)
            body[idx][1] = [Join.as_element(x or Text(' ')) for x in L]

            # Pre and pos
            body[idx][0] = Join.as_element(pre) if pre else None
            body[idx][2] = Join.as_element(pos) if pos else None

        return [ TabularLine(L, top=t, bottom=b) for (t, L, b) in body ]

    # Other methods and properties ---------------------------------------------
    def as_matrix(self):
        return [ L.as_line() for L in self.children ]

    @property
    def cols(self):
        return max(max([len(L) for L in self]), 1)

    @property
    def rows(self):
        return max(len(self.children), 1)

    @property
    def shape(self):
        return self.rows, self.cols

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            i, j = idx
            return self[i][j]
        else:
            return self.children[idx]

#===============================================================================
# Verbatim
#===============================================================================
class Verbatim(Environment):
    '''Base class for all verbatim environments'''

    def __init__(self, data='', **kwds):
        super(Verbatim, self).__init__(**kwds)
        self.add(TeXString(data))

    @classmethod
    def invoke(cls, job, tokens):
        # Read \beginenvironment macro and its arguments
        new = cls()
        macro = cls.invoke_macro(job, tokens, new)
        new.args = macro.args
        new.args.owner = new

        # Read verbatim until \endverbatim or \end{verbatim} is found
        end1 = new.env_name
        end2 = '{%s}' % new.env_name
        n1, n2 = len(end1), len(end2)
        data = [tokens.read_verbatim(r'\end'), r'\end']
        while True:
            if tokens.tell_char(n1) == end1:
                tokens.read_char(n1)
            elif tokens.tell_char(n2) == end2:
                tokens.read_char(n2)
            else:

                data.append(tokens.read_verbatim(r'\end'))
                data.append(r'\end')
                continue
            break
        data = ''.join(data)
        data = TeXString(data[:-4])  # remove trailing \end
        new.clear()
        new.add(data)
        return new

    @classmethod
    def invoke_body(cls, job, tokens, new):
        raise RuntimeError

    @property
    def verbdata(self):
        return self.children[0]

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    tex = r'''\begin{Tabular}{ccc}
1 & 2 & 3 \tabularnewline
4 & 5 & 6 \tabularnewline
7 & 8 & 9
\end{Tabular}'''

    tex = r'''\begin{tabular}{|c|c|c|}
\hline 
 &  & \tabularnewline
\hline 
\hline 
 &  & \tabularnewline
\hline 
 &  & \tabularnewline
\hline 
\end{tabular}'''

    from pytex import TeX
    doc = TeX(tex, loaditems=[Tabular])
    print(doc)
    print(doc.get(0).as_matrix())
    print(doc.source())
