if __name__ == '__main__':
    import pytex; __package__ = 'pytex'  # @ReservedAssignment @UnusedImport

import string
from collections import abc
from .types.abc import RFile
from .errors import InvalidCharError, MissingTokenError, LaTeXEOFError

#===============================================================================
# Category code constants
#===============================================================================
# The 16 category codes defined by TeX
CC_ESCAPE = 0
CC_BGROUP = 1
CC_EGROUP = 2
CC_MATHSHIFT = 3
CC_ALIGNMENT = 4
CC_EOL = 5
CC_PARAMETER = 6
CC_SUPER = 7
CC_SUB = 8
CC_IGNORED = 9
CC_SPACE = 10
CC_LETTER = 11
CC_OTHER = 12
CC_ACTIVE = 13
CC_COMMENT = 14
CC_INVALID = 15

# this category code does not exist in TeX. It is however included to represent
# skipped characters that should be irrelevant to the TeX processing but are
# desirable to be kept in order to keep the formating of the processed document
# consistent with the input
CC_SKIPPED = 16

# Default TeX categories
_letters = string.ascii_letters + '@'
DEFAULT_CATEGORIES = [
      '\\',  # 0  - TkEscape character
       '{',  # 1  - Beginning of group
       '}',  # 2  - End of group
       '$',  # 3  - Math shift
       '&',  # 4  - TkAlignment tab
      '\n',  # 5  - End of line
       '#',  # 6  - TkParameter
       '^',  # 7  - TkSuper
       '_',  # 8  - TkSub
    '\x00',  # 9  - TkIgnored character
 ' \t\r\f',  # 10 - TkSpace
  _letters,  # 11 - TkLetter
        '',  # 12 - TkOther character - This isn't explicitly defined.  If it
             #                        isn't any of the other categories, then
             #                        it's an "other" character.
       '~',  # 13 - TkActive character
       '%',  # 14 - TkComment character
        '',  # 15 - TkInvalid character
]

VERBATIM_CATEGORIES = [''] * 16
VERBATIM_CATEGORIES[11] = string.ascii_letters

#===============================================================================
# Token classes
#===============================================================================
class TokenMeta(type):
    '''A metaclass for Token types.'''

    def __new__(cls, name, bases, ns):
        if name != 'Token':
            ns.setdefault('__slots__', [])
        new_type = type.__new__(cls, name, bases, ns)

        # Add new type to _CLASSES dictionary (only first occurrence of each
        # catcode
        catcode = ns.get('catcode', None)
        if catcode is not None and Token._CLASSES[catcode] is None:
            Token._CLASSES[catcode] = new_type
        return new_type

class Token(str, metaclass=TokenMeta):
    """ Base class for all TeX tokens """

    _CLASSES = [None] * 17
    catcode = None

    def __repr__(self):
        return '%s(%s)' % (str.__repr__(self), self.catcode)

    def __eq__(self, other):
        if isinstance(other, Token):
            return type(self) == type(other) and super(Token, self).__eq__(other)
        else:
            return super(Token, self).__eq__(other)

    @classmethod
    def from_code(cls, code, st):
        '''Initialize token choosing the appropriate class from the given 
        catcode'''

        return cls._CLASSES[code](st)

class TkEscape(Token):
    catcode = CC_ESCAPE

    @property
    def macro_name(self):
        return self[1:]

class TkBGroup(Token):
    """ Beginning of a TeX group """

    catcode = CC_BGROUP
    macro_name = 'bgroup'

class TkEGroup(Token):
    """ Ending of a TeX group """

    catcode = CC_EGROUP
    macro_name = 'egroup'

class TkMath(Token):
    catcode = CC_MATHSHIFT
    macro_name = 'active::$'

class TkAlignment(Token):
    catcode = CC_ALIGNMENT
    macro_name = 'active::&'

class TkEOL(Token):
    catcode = CC_EOL

class TkParameter(Token):
    catcode = CC_PARAMETER

class TkSuper(Token):
    catcode = CC_SUPER
    macro_name = 'active::^'

class TkSub(Token):
    catcode = CC_SUB
    macro_name = 'active::_'

class TkSpace(Token):
    catcode = CC_SPACE

class TkLetter(Token):
    catcode = CC_LETTER

class TkOther(Token):
    catcode = CC_OTHER

class TkActive(Token):
    catcode = CC_ACTIVE

class TkComment(Token):
    catcode = CC_COMMENT

class TkInvalid(Token):
    catcode = CC_INVALID

class TkIgnored(Token):
    catcode = CC_IGNORED

#===============================================================================
# Extra classes for controlling skipped and extra characters
#
# Should we even try to do this? TeX skip and create some tokens during the
# tokenization process. We try to keep track of these tokens in order to be
# more faithfull to the input document. This might be completely unecessary.
#===============================================================================
class TkExtra:
    '''Base class for all aditional tokens that are added by the tokenizer'''
    def __repr__(self):
        return '+' + super(TkExtra, self).__repr__()

class TkExtraSpace(TkExtra, TkSpace):
    '''Extra space added when a CC_EOL is found in STATE_M'''

class TkSkipped:
    '''Base class for all tokens that are skipped by the tokenizer. Keeping 
    track of these tokens can be important '''
    catcode = CC_SKIPPED

class TkSkippedWS(TkSkipped, TkSpace):
    '''Skipped whitespace when whitespace is found in STATE_S'''
    catcode = CC_SKIPPED

class TkSkippedNL(TkSkipped, TkEOL):
    '''Skipped newlines when in STATE_S or STATE_M'''
    catcode = CC_SKIPPED

#===============================================================================
# Auxiliary tokenizer class. Used by the TeX parser in order to produce tokens
# from a TeX source code
#===============================================================================
class Tokenizer:
    def __init__(self, source='', catcodes=None):
        r'''Implements the tokenizer phase of TeX processing.
        
        Instances are iterators that yields a sequence of tokens.
        
        Examples
        --------
        
        Itertokens objects iterate over tokens read from a LaTeX source
        
        >>> tokens = Tokenizer(r'hi \you')
        >>> list(tokens)
        ['h'(11), 'i'(11), ' '(10), '\\you'(0)]
        
        There ares some methods to perform a partial iteration, if desirable
        
        >>> tokens = Tokenizer(r'hi \you joe')
        >>> list(tokens.stopping_after(TkEscape))
        ['h'(11), 'i'(11), ' '(10), '\\you'(0)]
        
        Of course, we can continue
        
        >>> list(tokens)
        [' '(16), 'j'(11), 'o'(11), 'e'(11)]
        '''

        self._catcode_table = catcodes or DEFAULT_CATEGORIES
        self._tk_buffer = []
        self._tokens = self._itertokens_()
        if isinstance(source, RFile):
            source = source.read()
        elif isinstance(source, str):
            pass
        elif isinstance(source, (tuple, list, abc.Iterable)):
            self._tk_buffer.extend(source)
            source = ''
        else:
            raise TypeError('unsupported source type: %s' % type(source).__name__)
        self._source = source
        self._pos = 0
        self._lineno = 0

    def _itertokens_(self):
        """A iterator over raw tokens extracted from a TeX source. 
        
        This corresponds to the 1st phase (the so-called "eye" part) of TeX 
        parsing."""

        # Local variables
        tk_buffer = self._tk_buffer
        catcoder = self.get_catcode
        read_next = self.read_char
        iter_chars = self._iter_source_

        # Define tokenizer state
        STATE_S = 1  # skipping spaces
        STATE_M = 2  # middle of line
        STATE_N = 4  # new line
        state = STATE_N

        while True:
            # Purge buffer first
            while tk_buffer:
                yield tk_buffer.pop()

            # Read the next token and obtain its catcode
            try:
                token = read_next()
            except EOFError:
                yield None
                continue
            code = catcoder(token)

            # Handle characters like ^^M, ^^@, etc. This step can be seen as a
            # pre-tokenizer, since it convert ^^* into new letters into the
            # input stream that will be tokenizer later
            if code == CC_SUPER:
                char = read_next()
                if char == token:
                    char = read_next()
                    num = ord(char)
                    if num >= 64:
                        token = chr(num - 64)
                    else:
                        token = chr(num + 64)
                    code = catcoder(token)
                else:
                    self._pos -= 1

            # Now we process each letter and yield the tokens associated to
            # them. Depending on the token, the processor may change its states
            # between (S)kipping spaces, (M)iddle of the line or (N)ew line.

            # Test letter and other first since they are the most common
            if code == CC_LETTER:
                state = STATE_M
                yield TkLetter(token)

            elif code == CC_OTHER:
                state = STATE_M
                yield TkOther(token)

            # TkEscape sequence
            elif code == CC_ESCAPE:
                state = STATE_S
                char = read_next()
                char_code = catcoder(char)

                # Get name of command sequence
                if char_code == CC_LETTER:
                    word = [char]
                    for char in iter_chars():
                        if catcoder(char) == CC_LETTER:
                            word.append(char)
                        else:
                            self._pos -= 1
                            break
                    yield TkEscape(token + ''.join(word))
                elif char_code == CC_SPACE:
                    yield TkEscape(token + char)
                else:
                    state = STATE_M
                    yield TkEscape(token + char)

            # End of line
            elif code == CC_EOL:
                if state == STATE_N:
                    yield TkEscape('\\par')
                elif state == STATE_M:
                    # The default TeX behavior is to yield a Space token that
                    # doesn't exists. This can screw a verbatim read, hence we
                    # shall declare this token as TkExtraSpace
                    #
                    # We also want to keep track of skipped newlines, hence we
                    # yield both of these tokens
                    state = STATE_N
                    yield TkExtraSpace(' ')
                    yield TkSkippedNL(token)
                    continue
                else:
                    state = STATE_N
                    yield TkSkippedNL(token)

            # Parameters such as #1, #2, etc and ##
            elif code == CC_PARAMETER:
                char = read_next()
                state = STATE_M
                if char in '0123456789' or char == token:
                    yield TkParameter(token + char)
                else:
                    self._pos -= 1

            # Whitespace
            elif code == CC_SPACE:
                if state == STATE_M:
                    state = STATE_S
                    yield TkSpace(' ')  # TeX converts all catcode=CC_SPACE into
                                        # character code 32 (' ') regardless if
                                        # they were tabs or other space character.
                else:
                    yield TkSkippedWS(token)

            # Comments
            elif code == CC_COMMENT:
                data = [token]
                for char in iter_chars():
                    data.append(char)
                    if catcoder(char) == CC_EOL:
                        break
                yield TkComment(''.join(data))

            # Invalid characters causes errors
            elif code == CC_INVALID:
                raise InvalidCharError('invalid character in LaTeX input: %r' % token)

            # Ignored characters are simply ignored
            elif code == CC_IGNORED:
                yield TkIgnored(token)

            # All other characters are passed direclty and change the state to
            # middle-of-the-line
            else:
                state = STATE_M
                yield Token.from_code(code, token)

    def read_char(self, size=1):
        '''Read the next character in the token stream'''

        if self._tk_buffer:
            raise NotImplementedError
        try:
            char = self._source[self._pos: self._pos + size]
        except IndexError:
            raise EOFError
        else:
            if char:
                self._pos += size
                return char
            else:
                raise EOFError

    def _iter_source_(self):
        while True:
            try:
                char = self._source[self._pos]
                self._pos += 1
                yield char
            except IndexError:
                return

    def __iter__(self):
        return self

    def __next__(self):
        tk = next(self._tokens)
        if tk is not None:
            return tk
        else:
            raise StopIteration

    def push(self, tok):
        '''Pushes a token back to the beginning of the list of tokens'''

        if isinstance(tok, Token):
            self._tk_buffer.append(tok)
        elif tok is None:
            pass
        else:
            tname = type(tok).__name__
            raise TypeError('trying to push a %s to the token stream' % tname)

    def push_list(self, tok_list):
        '''Push all items in tok_list to the beginning of the token stream'''

        tok_list = list(tok_list)
        if not all(isinstance(x, Token) for x in tok_list):
            raise TypeError('trying to push non-tokens to stream')
        tok_list.reverse()
        self._tk_buffer.extend(tok_list)

    def read_verbatim(self, stop_char):
        r'''Reads the input until the stop_char is encountered. Returns a string
        with the content (excluding stop_char)
        
        Example
        -------
        
        >>> tokens = Tokenizer(r'\verbatim Foo \endverbatim')
        >>> tokens.get_next()
        '\\verbatim'(0)
        >>> tokens.read_verbatim(r'\endverbatim')
        ' Foo '
        >>> list(tokens) # It reached EOF, so "tokens" is empty
        []
        
        Verbatim reads works even when there are tokens in the buffer
        
        >>> tokens = Tokenizer(r'barend')
        >>> tokens.push_list(Tokenizer('foo'))
        >>> tokens.read_verbatim('end')
        'foobar'
        
        Even when the pushed tokens are in the middle of stop_char
        
        >>> tokens = Tokenizer(r'dfoo')
        >>> tokens.push_list(Tokenizer('baren'))
        >>> tokens.read_verbatim('end')
        'bar'
        '''

        # Use tokens in buffer
        tokens = self._tk_buffer
        buffer = ''.join(reversed(tokens))
        if stop_char and stop_char in buffer:
            buffer, _, post = buffer.partition(stop_char)
            tokens = list(Tokenizer(post))
            return buffer + stop_char

        if not stop_char:
            self._pos = len(self._source)
            return buffer + self._source[self._pos:]

        # Check if stop char is partially in buffer and correct source
        partials = [ stop_char[:-i] for i in range(1, len(stop_char)) ]
        for partial in partials:
            if buffer.endswith(partial):
                delta = len(stop_char) - len(partial)
                if partial + self.tell_char(delta) == stop_char:
                    self._pos += delta
                    buffer = buffer[:-delta - 1]
                    return buffer

        # Now we know that stop_char is not in buffer nor in the overlap betweeen
        # buffer and source
        idx = self._source.find(stop_char, self._pos)
        if idx == -1:
            raise EOFError('file endend before %s was found in verbatim read' % stop_char)
        data = self._source[self._pos:idx]
        self._pos = idx + len(stop_char)
        self._tk_buffer[:] = tokens

        return buffer + data

    def tell_char(self, size=1):
        '''Tell the next character in the source code.'''

        return self._source[self._pos:self._pos + size]

    def get_specific(self, template, exception=None, e_args=None):
        '''Read a single token and raise an exception if it is not of the 
        expected value or type'''

        try:
            tok = next(self._tokens)
        except StopIteration:
            raise LaTeXEOFError(self)
        if isinstance(template, (type, tuple)):
            if not isinstance(tok, template):
                if exception is None and e_args is None:
                    raise MissingTokenError(tok, template, self)
                else:
                    raise exception(*e_args)
        elif tok != template:
            if exception is None and e_args is None:
                raise MissingTokenError(tok, template, self)
            else:
                raise exception(*e_args)
        return tok

    def get_macro(self, macro_name, exception=None, e_args=None):
        '''Similar to get_specific() but gets a escape token with a given macro 
        name'''

        tok = self.get_specific(TkEscape)
        if tok.macro_name != macro_name:
            raise ValueError('bad macro: expected %s, got %s' % (macro_name, tok.macro_name))
        return tok

    def get_next(self, value=None):
        '''Similar to next(self), but instead of raising an StopIteration for 
        depleted iterators, it returns the given value'''

        try:
            return next(self)
        except StopIteration:
            return value

    def next(self, exception=StopIteration, msg=''):
        '''Similar to next(self), but we can control the exception that is 
        raised for empty iterators'''

        tok = next(self._tokens)
        if tok is None:
            raise exception(msg)

    def get_catcode(self, char):
        """Return the integer character code that `char` belongs to."""

        for no, chars in enumerate(self._catcode_table):
            if char in chars:
                return no
        else:
            return CC_OTHER

    def all_tokens(self):
        '''A debugging function: it return a list of tokens and push all of them
        back to the stream'''

        tokens = list(self)
        self.push_list(tokens)
        return tokens

    def get_lineno(self):
        '''Return the probable line number for the next character.'''

        return self._source.count('\n', 0, self._pos)

    def get_line(self, idx=None):
        '''Return idx-th line of source code.'''

        lines = self._source.splitlines()
        idx = idx if idx is not None else self._pos
        if len(lines) == idx:
            return '<EOL>'
        else:
            return lines[idx]

    def get_charno(self):
        '''Return the proable position of the cursor on the current line.'''

        pos = self._pos
        for line in self._source.splitlines()[:self._lineno]:
            pos -= len(line)
        return pos

    def tell_next(self):
        '''Tell what is the next token'''

        try:
            tok = next(self)
        except StopIteration:
            return None
        else:
            self.push(tok)
            return tok

    def skip_whitespace(self):
        '''Skip all whitespace tokens'''

        nxt = self.tell_next()
        while nxt is not None and nxt.catcode in (CC_SPACE, CC_EOL):
            next(self)

    #===========================================================================
    # Special iterators
    #===========================================================================
    def stopping_after(self, token):
        '''Iterates until the given token is obtained.
        
        Token can be a token or string object for testing by value or a token 
        class for testing by type'''

        yield from self.stopping_before(token)
        yield next(self)

    def stopping_before(self, token):
        '''Stops iteration just before the given token appears in the token 
        stream.
        
        Token can be a token or string object for testing by value or a token 
        class for testing by type'''

        if isinstance(token, (str, Token)):
            func = lambda x: x != token
        elif isinstance(token, (type, tuple)):
            func = lambda x: not isinstance(x, token)
        else:
            raise TypeError(type(token))

        return TakeWhileTokenizer(self, func)

    def stopping_before_macro(self, macro_name):
        '''Stops iteration just before the given macro appears in the token 
        stream.'''

        def func(x):
            return not isinstance(x, TkEscape) or x.macro_name != macro_name

        return TakeWhileTokenizer(self, func)

    def while_equals(self, token):
        '''Iterate while tokens are equal to the given token.
        
        The argument can be a token, a string, a token type or a tuple of types.'''

        if isinstance(token, (str, Token)):
            func = lambda x: x == token
        elif isinstance(token, (type, tuple)):
            func = lambda x: isinstance(x, token)
        else:
            raise TypeError(type(token))

        return TakeWhileTokenizer(self, func)

    def sized(self, size):
        '''Return an iterator that reads at most size tokens'''

        return SizedTokenizer(self, size)

    def until_egroup(self):
        '''Read tokens until a group closes. This method counts opening bgroup
        tokens and only stop iteration when a new unmatched egroup token is 
        found'''

        return EGroupTokenizer(self)

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def source(self):
        return self._source

class SubTokenizer(Tokenizer):
    '''A derived Tokenizer that can override the __next__ method'''

    def __init__(self, tokenizer):
        self._tokenizer = tokenizer
        self._source = tokenizer._source
        self._catcode_table = tokenizer._catcode_table
        self._tk_buffer = tokenizer._tk_buffer
        self._tokens = tokenizer._tokens

    @property
    def _pos(self):
        return self._tokenizer._pos

    @_pos.setter
    def _pos(self, value):
        self._tokenizer._pos = value

    @property
    def _lineno(self):
        return self._tokenizer._lineno

    @_lineno.setter
    def _lineno(self, value):
        self._tokenizer._lineno = value


class TakeWhileTokenizer(SubTokenizer):
    '''A truncated Tokenizer. It iterates while cond_func(token) returns True.'''

    def __init__(self, tokenizer, cond_func=(lambda x: True)):
        super(TakeWhileTokenizer, self).__init__(tokenizer)
        self.cond_func = cond_func

    def __next__(self):
        tok = next(self._tokenizer)
        if not self.cond_func(tok):
            self._tokenizer.push(tok)
            raise StopIteration
        return tok

class SizedTokenizer(SubTokenizer):
    '''A truncated Tokenizer. It stops iteration after maxsize items are yielded.'''

    def __init__(self, tokenizer, maxsize):
        super(SizedTokenizer, self).__init__(tokenizer)
        self._tokenizer = tokenizer
        self.maxsize = maxsize
        self._n_iter = 0

    def __next__(self):
        if self._n_iter < self.maxsize:
            self._n_iter += 1
            return next(self._tokenizer)
        self._n_iter = 0
        raise StopIteration

class EGroupTokenizer(SubTokenizer):
    '''Iterates until a group closes. It matches opening and closing characters
    to avoid an early stop.'''

    def __init__(self, tokenizer):
        super(EGroupTokenizer, self).__init__(tokenizer)
        self._count = 0
        self._bpos = tokenizer._pos

    def __next__(self):
        try:
            tok = next(self._tokenizer)
        except StopIteration:
            print('-' * 80)
            print(self.source[self._bpos:])
            raise EOFError(r'tokens ended before expected "}"')

        # update idx var
        if isinstance(tok, TkEGroup):
            self._count += 1
        elif isinstance(tok, TkBGroup):
            self._count -= 1

        # check stop condition
        if self._count > 0:
            self._tokenizer.push(tok)
            self._count = 0
            raise StopIteration
        return tok

#===============================================================================
# Testing code
#===============================================================================
if __name__ == '__main__':
    import doctest
    doctest.testmod()
