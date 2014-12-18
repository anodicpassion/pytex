import re
import io
import sys
import contextlib
import collections

__all__ = ['escape_tex', 'indent', 'letter', 'roman', 'capture_to_list',
           'print_capture']

#===============================================================================
# LaTeX escaping
#===============================================================================
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash '),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots '),
)

def escape_tex(text):
    '''Escape the given `text` to safe LaTeX'''

    newval = text
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

#===============================================================================
# Text formatting
#===============================================================================
def indent(st, indent, indent_first=True):
    '''Indent string `st` by the string `indent`. 
    
    The parameter `indent` can also be a number representing the number of 
    spaces. The optional `indent_first` (default=True) tells if the first line 
    should be indented or not.
    '''

    istr = indent if isinstance(indent, str) else ' ' * indent
    lines = st.splitlines()
    if indent_first:
        return ''.join(istr + line for line in lines)
    else:
        return '\n'.join(lines)

#===============================================================================
# Numbers to letters
#===============================================================================
# Convert integers to letters
LETTERS = 'abcdefghijklmnopqrstuvwxyz'

def letter(idx):
    '''Convert numerical index (starting from 0) to the corresponding letter'''

    if idx < 0:
        raise ValueError('do not accept negative indexes')
    return (letter(idx // 26 - 1) if idx // 26 else '') + LETTERS[idx % 26]

# Convert integers to roman numerals
ROMANS = (('M', 1000),
          ('CM', 900),
          ('D', 500),
          ('CD', 400),
          ('C', 100),
          ('XC', 90),
          ('L', 50),
          ('XL', 40),
          ('X', 10),
          ('IX', 9),
          ('V', 5),
          ('IV', 4),
          ('I', 1))

def roman(idx):
    """Convert integer to Roman numeral"""

    if not (0 < idx < 5000):
        return str(idx)

    result = ""
    for roman, i in ROMANS:
        while idx >= i:
            result += roman
            idx -= i
    return result

#===============================================================================
# Printing behavior
#===============================================================================
def capture_to_list(L):
    '''Return a function that works like print(), but redirects all output to
    a list L.
    
    Example
    -------
    
    >>> L = [] 
    >>> myprint = capture_to_list(L)
    >>> myprint('foobar') 
    >>> myprint('foo', 'bar', end='. ')
    >>> L
    ['foobar\n', 'foo bar. ']
    '''

    def my_print(value, *args, sep=' ', end='\n', file=sys.stdout, flush=False):
        out = io.StringIO() if file is sys.stdout else file
        print(value, *args, sep=sep, end=end, file=out, flush=False)
        if file is sys.stdout:
            L.append(out.getvalue())

    return my_print

class strbuffer(collections.UserString):
    def __init__(self, F=None):
        self.file = F if F is not None else io.StringIO()
        self._loc = self.file.tell()
        self.data = ''

    def stringfy(self):
        '''Read content from file buffer and transfer it to the `.data` 
        attribute of the string.'''

        loc = self.file.tell()
        try:
            self.file.seek(self._loc)
            self.data = self.file.read()
        finally:
            self.file.seek(loc)

    def decode(self, encoding=None):
        return self.data

    def encode(self, *args, **kwds):
        return self.data.encode(*args, **kwds)

@contextlib.contextmanager
def print_capture(capture_errors=False):
    '''A context manager that captures all print statements to a buffer which 
    behaves like a string.
    
    Example
    -------
    
    >>> with capture_to_list() as st:
    ...    print('foo')
    ...    print('bar')
    >>> print(st)
    foo
    bar
    <BLANKLINE>
    '''

    try:
        old_stderr = sys.stderr
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        if capture_errors:
            sys.stderr = sys.stdout
        buffer = strbuffer(sys.stdout)
        yield buffer

    finally:
        buffer.stringfy()
        sys.stdout = old_stdout
        sys.stderr = old_stderr


if __name__ == '__main__':
    import doctest
    doctest.testmod()
