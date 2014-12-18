'''The implementation of the parsing routines in this package are based on the
description of the LaTeX processor found in Victor Eijkout's book "TeX by topic,
a TeXnician reference"

LaTeX processing is divided into 4 phases:

1) Tokenizer: Convert the document source into LaTeX tokens. Tokens can be 
either character tokens or control sequece tokens (such as "\foo"). This phase
is implemented by the "Tokenizer" class which converts a LaTeX text into an
iterator over tokens.

2) Expansion processor: some tokens are expanded into other lists of tokens. 
This is the case, for instance, of user-defined macros that are expanded into
other LaTeX tokens.

3) Execution processor: non-expandable tokens are executable. They can change
the state of execution (such as assignment of macros, loading packages, etc)

4) Visual processor: this phase regards the construction of the final postscript
which is presented to the user.

...

'''
if __name__ == '__main__':
    import pytex; __package__ = 'pytex'  # @ReservedAssignment @UnusedImport

# Import tokens and catcodes
from . import tokens as TK
from .errors import LaTeXError
from .textypes import (TeXDocument, TeXStream, TeXToken, Text, Group, TeXElement)
from .textypes.texmath import Math, DisplayMath
from .textypes.macro import Macro
from .textypes.environment import Environment

__all__ = ['TeXJob', 'TeX']

NoneType = type(None)

#===============================================================================
# Public API: The main LaTeX parser is implemented in the TeXJob class. TeX
# snippets can be processed by the TeX() function
#===============================================================================
class TeXJob:
    r'''Process a TeX code. The final result is a TeXDocument object representing
    input LaTeX children.
    
    Examples
    ---------
    
    Parses arbitrary TeX code
    
    >>> p = TeXJob(r'\hello world!') 
    >>> p.parse()
    TeXStream([<\hello macro>, 'world!'])
    
    TeXJob understands most LaTeX commands and can correctly assign arguments to
    each macro
        
    >>> tex = r'\documentclass[a4]{article}'
    >>> TeXJob(tex).parse()
    TeXStream([<\documentclass[a4]{article} macro>])
    
    Math expressions are not parsed
    
    >>> tex = r"math: $\int x dx = \frac{x^2}{2}$"
    >>> TeXJob(tex).parse()
    TeXStream(['math: ', '$...$'])
    
    If the LaTeX source has a \begin{document} declaration, it automatically 
    recognizes as a LaTeX document and return an instance of TeXDocument instead 
    of TeXStream
    
    Document objects have a preamble and a body attributes.
    
    >>> tex = r"""\documentclass{article}
    ... \usepackage[brazil]{babel}
    ... 
    ... \begin{document}
    ... Some \TeX document.
    ... \end{document}
    ... """
    >>> doc = TeXJob(tex).parse()
    >>> print(doc)
    TeXDocument
       |--TeXPreamble([<\documentclass{article} macro>, '\n', <\usepackage[brazil]{babel} macro>])
       \--TeXBody(['Some ', <\TeX macro>, 'document.'])
       
    The LaTeX source can be easily computed from any TeXElement object
    
    >>> print(doc.source())
    \documentclass{article}
    \usepackage[brazil]{babel}
    <BLANKLINE>
    \begin{document}
    Some \TeX document.
    \end{document}
    
    
    '''
    def __init__(self, source, packages=[], silent=True):
        if not isinstance(source, str):
            raise TypeError('source must be a string')
        elif not source:
            raise ValueError('empty source string')

        self.source = str(source)
        self._tokens = TK.Tokenizer(source)
        self._buffer = []
        self._master = TeXStream()
        self._env_table = {}
        self._is_parsed = False
        self._silent = silent

        for p in packages:
            self.context.load_package(p)

    #===========================================================================
    # Context related functions
    #===========================================================================
    def get_macro(self, x, warn=None):
        '''Return a macro from its name'''

        if warn is None:
            warn = 0 if self._silent else 1
        return self.context.get_macro(x, warn)

    def get_environment(self, x, warn=None):
        '''Return an environment from its name'''

        if warn is None:
            warn = 0 if self._silent else 1
        return self.context.get_environment(x, warn)

    def save_environment(self, env):
        '''Save an environment to context'''

        self.context.save_environment(env)

    def save_macro(self, macro):
        '''Save a macro to context'''

        self.context.save_macro(macro)

    def load_package(self, package):
        '''Load package from its name or from a Package object'''

        self.context.load_package(package)

    #===========================================================================
    # TeX argument reading
    #===========================================================================
    def read_all(self, tokens):
        '''Return a list with the results of .read_next() until all tokens
        are depleted'''

        L = []
        nxt = self.read_next(tokens)
        while nxt is not None:
            L.append(nxt)
            nxt = self.read_next(tokens)
        return L

    def read_next(self, tokens):
        '''Reads and process the next element of a sequence of tokens. This 
        function simply delegates processing to more specialized functions 
        depending on the type of the first token.
        
        Any number of tokens (starting from 1) can be consumed by this function.
        Tokens are consumed until a consistent element can be created.'''

        token = tokens.tell_next()
        tk = TK

        # Old versions of this code were pushing initialized TeXElements to the
        # tokenizer. This cannot happen anymore!
        assert isinstance(token, (tk.Token, NoneType)), 'invalid type for token: %s' % type(token).__name__

        try:
            # Macros
            if isinstance(token, tk.TkEscape):
                macro = self.read_macro(tokens)
                if macro is None:
                    return self.read_next(tokens)
                else:
                    return macro

            # The tokenizer returns None from tell_next() when we run out of
            # tokens. We should return these None's to sinalize the parser
            # that there are nothing more to process
            elif token is None:
                return None

            # Text tokens
            elif 10 <= token.catcode <= 12:
                return self.read_text(tokens)

            # Groups
            elif isinstance(token, tk.TkBGroup):
                return self.read_group(tokens)

            # Math
            elif isinstance(token, tk.TkMath):
                return self.read_math(tokens)

            # TkSkipped text can be either a skipped whitespace or a skipped new line
            # we are ignoring skipped spaces but trying to keep the skipped new lines
            # in order to preserve formatting
            elif isinstance(token, tk.TkSkipped):
                next(tokens)
                return self.read_next(tokens)

            # Comments, TkAlignment and other single char tokens
            elif isinstance(token, (tk.TkAlignment, tk.TkParameter, tk.TkSuper,
                                    tk.TkSub, tk.TkActive, tk.TkComment)):
                return TeXToken.from_token(next(tokens))

            # Return token if not handled
            msg = ['\nTokens : ', str(list(tokens)),
                   '\nParsed :', str(self._master.children),
                   '\nToken: ', repr(token) ]
            raise RuntimeError(''.join(msg))

        # This helps to find bugs in the read_* methods. They should never raise
        # StopIteration due to running out of tokens, but rather we should convert
        # this exception to more meaningfull errors such as EOLError, LaTeXError, etc.
        #
        # We avoid any guessing and declare this behavior as a bug.
        except StopIteration:
            raise RuntimeError('StopIteration unhandled in read_next()')

    def read_text(self, tokens):
        '''Read text from a sequence of tokens. Texts are created from 
        sequences of characters of catcodes CC_SPACE (10), CC_LETTER (11) or 
        CC_OTHER (12)'''

        tk = TK

        # Absorb letters
        letters = []
        for tok in tokens:
            if 10 <= tok.catcode <= 12:
                letters.append(tok)
            else:
                tokens.push(tok)
                break
        data = ''.join(letters)

        # Absorb a trailing newline, if it exists
        if isinstance(tok, tk.TkSkippedNL):
            next(tokens)
            data += '\n'
        if data.endswith(' \n'):
            data = data[:-1]

        # The processor seems to be adding too many TkExtraSpace tokens
        # absorb them!
        if isinstance(tokens.tell_next(), tk.TkExtraSpace):
            next(tokens)

        return Text(data)

    def read_macro(self, tokens):
        '''Read and initializes a macro from tokens. Return the non-expanded 
        macro.'''

        # Read macro name and push token back
        macro_tok = tokens.get_specific(TK.TkEscape)
        macro_name = macro_tok.macro_name
        tokens.push(macro_tok)

        # Obtain macro class and invoke it
        macro_cls = self.get_macro(macro_name)
        macro = macro_cls.invoke(self, tokens)

        # Invoke can return None to tell that no object should be constructed.
        # This can be used for macros that put tokens in the token stream to
        # be processed later.
        if macro is None:
            return None

        # TODO: implement the force_expand list and only implement the macros in
        # this list (or those that declare themselves force_expand=True)
        if macro.force_expand:  # or in force_expand_list
            macro = macro.expand(self, tokens)

        return macro

    def read_group(self, tokens):
        '''Read a group starting from a bgroup token'''

        tk = TK
        bgroup = tokens.get_specific(tk.TkBGroup)  # read bgroup token
        children = self.read_all(tokens.stopping_before(tk.TkEGroup))
        egroup = tokens.get_specific(tk.TkEGroup)  # read egroup token
        return Group(bgroup, children, egroup)

    def read_math(self, tokens):
        '''Read math object and initializes it'''

        # Decide if it will be a DisplayMath object or a regular Math object
        mshift = bmath = tokens.get_specific(TK.TkMath)
        if tokens.tell_next() == bmath:
            display_math = True
            mshift += next(tokens)
        else:
            display_math = False

        # Read all elements
        elements = self.read_all(tokens.stopping_before(bmath))
        tokens.get_specific(bmath)

        # Return the appropriate object
        if display_math:
            tokens.get_specific(bmath)
            return DisplayMath(mshift, elements, mshift)
        else:
            return Math(mshift, elements, mshift)

    def read_verbatim(self, tokens, stop_char):
        '''Read a text verbatim until stop_char is encountered. Return a string
        that includes the trailing `stop_char`'''

        if len(stop_char) != 1:
            raise NotImplementedError("only single leter stop_char's are supported: %r" % stop_char)

        return tokens.read_verbatim(stop_char)

    def read_int(self, tokens):
        '''Reads a integer object'''

        tokens.skip_whitespace()

        pass


    #===========================================================================
    # Indexing and sequence interface
    #===========================================================================
    def __getitem__(self, idx):
        self.parse()
        return self._master[idx]

    def __iter__(self):
        return self

    def __next__(self):
        '''Compute and yield the next element.'''

        element = self.read_next(self._tokens)

        if isinstance(element, NoneType):
            raise StopIteration
        elif not isinstance(element, TeXElement):
            raise RuntimeError('unparsed token: %r (%s)' % (element, type(element).__name__))
        self._master.add(element)
        return element

    def __len__(self):
        self.parse()
        return len(self._master)

    #===========================================================================
    # Other
    #===========================================================================
    def parse(self):
        '''Return a list of all parsed elements'''

        if not self._is_parsed:
            for _ in self:
                pass
            self._is_parsed = True
            self._master = self._master.revalue('finish')
            document = self._master.context.get_environment('document')
            try:
                document = self._master.get(document)
            except ValueError:
                pass
            else:
                # Create a TeXDocument instance
                siblings_before = document.get_siblings_prev()
                siblings_after = document.get_siblings_next()
                self._master.clear()
                self._master = TeXDocument(siblings_before, document.clear(),
                                           context=self._master.context)

                # ensure that there is no non-empty data after \end{document}
                for obj in siblings_after:
                    if obj.source().strip().replace('\n', ''):
                        msg = 'invalid command after document had finished: %s' % obj.source()
                        raise LaTeXError(msg)

                # Revalue
                self._master = self._master.revalue('finish')

        return self._master

    @property
    def context(self):
        return self._master.context

    @context.setter
    def context(self, value):
        self._master.context = value

def TeX(text, context=None, loaditems=[], packages=[]):
    '''Process a string with LaTeX children. 
    
    The `parent` object is assigned to the result. Moreover, important 
    information such as loaded macros and environments can be obtained from this
    object. If no parent is given, a vanilla LaTeX environment is assumed. '''

    # Create processor
    job = TeXJob(text)

    # Define its context
    if context is not None:
        job.context = context

    # Load user supplied items (macros, environments, etc)
    for item in loaditems:
        if isinstance(item, type):
            if issubclass(item, Macro):
                job.save_macro(item)
                continue
            elif issubclass(item, Environment):
                job.save_environment(item)
                continue
        tname = item.__name__ if isinstance(item, type) else type(item).__name__
        raise TypeError('cannot load %s objects' % tname)

    # Load user supplied packages
    for package in packages:
        job.load_package(package)

    # Now run!
    return job.parse()

if __name__ == '__main__':
    import doctest
    doctest.testmod(report=True, optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)


    doc = TeX(r'hello \world!')
    print(doc)
