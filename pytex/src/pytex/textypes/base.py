if __name__ == '__main__':
    import pytex.textypes; __package__ = 'pytex.textypes'  # @ReservedAssignment @UnusedImport

from collections import MutableSequence
import copy
from . import Element, Container
from .. import tokens as tk
from ..util.splitters import strip
from collections.abc import Iterable

#===============================================================================
# TeXElement
#===============================================================================
class TeXElement(Element):
    '''Base class for all parsed TeX objects'''

    force_expand = False
    macro_name = None

    def __init__(self):
        pass

    def __repr__(self):
        source = self.source()
        if len(source) > 10:
            source = source[:7] + '...'
        return "'%s'" % source

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        '''Two TeXElements are identical if they have the same source'''
        if isinstance(other, TeXElement):
            return self.source() == other.source()
        elif isinstance(other, str):
            return self.source() == other
        else:
            TypeError(type(other))

    def source(self):
        '''Return a string with the source code associaded with object'''

        raise NotImplementedError('Must be implemented in subclasses')

    def tokenize(self):
        '''Convert itself into a list of tokens'''

        return list(tk.Tokenizer(self.source()))

    def revalue(self, method, *args, **kwds):
        '''
        This method allows a TeXElement to re-evaluate itself according to some
        rule. The default implementation just calls `obj.revalue_<method>(**kwds)`, 
        if implemented. Compound objects also revalue its children.  
        '''

        method = getattr(self, 'revalue_' + method, None)
        if method is None:
            return self
        else:
            return method(*args, **kwds)

    def revalue_finish(self):
        '''
        This method is invoked on all objects after initial parsing is complete.
        This allows the object to modify itself (or a neighbor) after the full
        document structure is ready.
        
        It must return a modified object or itself, if no changes are necessary.
        '''

        return self

    def copy(self):
        '''Return a deepcopy of itself'''

        return copy.deepcopy(self)

    @property
    def context(self):
        try:
            return self.parent.context
        except AttributeError:
            raise RuntimeError('object without defined context, %r' % self)

    @property
    def master(self):
        master = self
        while master.parent is not None:
            master = master.parent
        return master

#===============================================================================
# String Types
#===============================================================================
class TeXString(TeXElement, str):
    '''Base class for all string-like objects
    
    TeXString subtypes work very similarly to strings. It can be used 
    transparently as a native string.
    
    >>> foo, bar = SkippedLine('foo'), SkippedLine('bar')
    >>> foo.title()
    *'Foo'
    >>> foo[0].join('LETTERS')
    *'LfEfTfTfEfRfS'
    >>> foo + bar
    *'foobar'
    '''

    __slots__ = []

    def __new__(cls, st):
        if not isinstance(st, str):
            raise ValueError('Trying to initialize with a %s, must be a string' % type(st).__name__)
        return str.__new__(cls, st)

    def __init__(self, st):
        TeXElement.__init__(self)

    def __eq__(self, other):
        '''Test by string equality'''
        return str.__eq__(self, other)

    def __repr__(self):
        return str.__repr__(self)

    def __str__(self):
        return str.__str__(self)

    def __hash__(self):
        return str.__hash__(self)

    def __getitem__(self, idx):
        return type(self)(str.__getitem__(self, idx))

    def __mul__(self, idx):
        return type(self)(str.__mul__(self, idx))

    def __add__(self, other):
        return type(self)(str.__add__(self, other))

    def __radd__(self, other):
        return type(self)(str.__add__(other, self))

    def source(self):
        return str.__str__(self)

    # String methods -----------------------------------------------------------
    def capitalize(self): return type(self)(str.capitalize(self))
    def lower(self): return type(self)(str.lower(self))
    def swapcase(self): return type(self)(str.swapcase(self))
    def title(self): return type(self)(str.title(self))
    def upper(self): return type(self)(str.upper(self))
    def center(self, width, fillchar=' '): return type(self)(str.center(self, width, fillchar))
    def ljust(self, width, fillchar=' '): return type(self)(str.ljust(self, width, fillchar))
    def rjust(self, width, fillchar=' '): return type(self)(str.rjust(self, width, fillchar))
    def zfill(self, width): return type(self)(str.zfill(self, width))
    def decode(self, encoding=None, errors=None): return type(self)(str.decode(self, encoding, errors))
    def expandtabs(self, tabsize=None): return type(self)(str.expandtabs(self, tabsize))
    def format(self, *args, **kwds): return type(self)(str.format(self, *args, **kwds))
    def join(self, seq): return type(self)(str.join(self, seq))
    def replace(self, st1, st2): return type(self)(str.replace(self, st1, st2))
    def translate(self, table, deletechars=None): return type(self)(str.translate(self, table, deletechars))
    def strip(self, chars=None): return type(self)(str.strip(self, chars))
    def rstrip(self, chars=None): return type(self)(str.rstrip(self, chars))
    def lstrip(self, chars=None): return type(self)(str.lstrip(self, chars))
    def partition(self, sep): return tuple(map(type(self), str.partition(self, sep)))
    def rpartition(self, sep): return tuple(map(type(self), str.rpartition(self, sep)))

    def split(self, word=None):
        tt = type(self)
        return [ tt(x) for x in str.split(self, word) ]

    def splitlines(self, keepends=False):
        tt = type(self)
        return [ tt(x) for x in str.splitlines(self, keepends) ]

class TeXComment(TeXString):
    '''Represents a line of comment'''

class Text(TeXString):
    '''Represents a text fragment'''

class SkippedLine(TeXString):
    '''Represents a text fragment (usually whitespace) that were skipped during
    TeX processing'''

    def __repr__(self):
        return '*' + TeXString.__repr__(self)

#===============================================================================
# Token Types
#===============================================================================
class TeXToken(TeXElement):
    '''Represents am unexpanded TeX token.
    
    This class cannot be used direclty, but one should use one of its subclasses 
    bellow.'''

    _TOKEN_CLASSES = {}
    token_type = None

    def __init__(self, token):
        if self.token_type != type(token):
            cname = type(self).__name__
            tname = type(token).__name__
            raise ValueError('Trying to intialize a %s with a %s token' % (cname, tname))
        else:
            super(TeXToken, self).__init__()
            self._token = token

    def source(self):
        return str(self._token)

    def __eq__(self, other):
        if isinstance(other, TeXToken):
            return self._token == other._token
        elif isinstance(other, TeXToken):
            return self._token == other
        else:
            return str(self) == other

    @property
    def token(self):
        return self._token

    @property
    def catcode(self):
        return self._token.catcode

    @classmethod
    def from_token(cls, token):
        '''Create a TeX token from a token object'''

        try:
            return cls._TOKEN_CLASSES[type(token)](token)
        except KeyError:
            raise TypeError('not a supported token type: %s' % type(token).__name__)

    @classmethod
    def register(cls, tt):
        '''Register a class as a token class'''

        cls._TOKEN_CLASSES[tt.token_type] = tt
        return tt

# Subclasses for specific token types. These are left as-is by the base parser.
# (They should be converted from Token to TeXElements to be in a TeX document, though)
@TeXToken.register
class Alignment(TeXToken):
    token_type = tk.TkAlignment

@TeXToken.register
class Parameter(TeXToken):
    token_type = tk.TkParameter

@TeXToken.register
class Super(TeXToken):
    token_type = tk.TkSuper

@TeXToken.register
class Sub(TeXToken):
    token_type = tk.TkSub

@TeXToken.register
class Active(TeXToken):
    token_type = tk.TkActive

@TeXToken.register
class Comment(TeXToken):
    token_type = tk.TkComment

#===============================================================================
# Containers
#===============================================================================class
class TeXContainer(Container, TeXElement):
    '''Base class for compound objects. 
    
    Has a 'children' argument that is a list of children objects, and a 
    children_source() method that returns a string with the source code of all 
    children.'''

    trim_newlines = False

    def __init__(self, *, children=None):
        TeXElement.__init__(self)
        Container.__init__(self)
        children = children or []
        if self.trim_newlines:
            strip(children)
        try:
            self.children.extend(children)
        except ValueError:
            raise ValueError('trying to include objects that already have parents')

    def __repr__(self):
        children = [ repr(x) for x in self ]
        if len(children) > 7:
            children = children[:7]
            children.append('...')
        children = ', '.join(children)
        return '%s([%s])' % (type(self).__name__, children)

    def __len__(self):
        return len(self.children)

    def __contains__(self, obj):
        return obj in self.children

    def __iter__(self):
        return iter(self.children)

    def __reversed__(self):
        return reversed(self.children)

    def _subitems_(self):
        return iter(self.children)

    #===========================================================================
    # Children control
    #===========================================================================
    def add(self, obj, index=None):
        '''Adds a new children at the given index or at the end'''

        children = self.children

        if index is None:
            if isinstance(obj, Join):
                children.extend(obj.clear())
            elif isinstance(obj, TeXElement):
                children.append(obj)
            elif isinstance(obj, Iterable):
                children.extend(obj)
            else:
                tname = type(obj).__name__
                raise ValueError('cannot add %s object' % tname)
        else:
            if isinstance(obj, Join):
                children.add(obj.clear(), index)
            elif isinstance(obj, TeXElement):
                children.insert(index, obj)
            else:
                for elem in reversed(obj):
                    self.add(elem, index)

    def get(self, arg):
        '''Return some child element.
        
        If arg is int, return children at the given index. If arg is a type, 
        return the first children of the given type.'''

        if isinstance(arg, int):
            return self.children[arg]
        elif isinstance(arg, type) and issubclass(arg, TeXElement):
            try:
                return next(x for x in self if isinstance(x, arg))
            except StopIteration:
                raise ValueError('no child of type %s' % arg.__name__)
        else:
            raise TypeError(type(arg))

    def get_all(self, tt):
        '''Return all children of the given type'''

        return [ x for x in self if isinstance(x, tt) ]

    def replace(self, arg, value):
        '''Replace the child at given index or at the position of the first child
        of the given type'''

        if isinstance(arg, int):
            self.children[arg] = value
        elif isinstance(arg, type) and issubclass(arg, TeXElement):
            try:
                value = next(x for x in self if isinstance(x, arg))
            except StopIteration:
                raise ValueError('no child of type %s' % arg.__name__)
            value.replace_by(value)
        else:
            raise TypeError(type(arg))

    def pop(self, arg=None):
        '''Pops the child at the given position (or first child of given type'''

        if arg is None:
            return self.children.pop()
        elif isinstance(arg, int):
            return self.children.pop(arg)
        else:
            value = next(iter(x for x in self if isinstance(x, arg)))
            value.unlink()
            return value

    def remove(self, arg):  # @ReservedAssignment
        '''Remove children at given position (or first child of given type).
        
        If argument is a type and all=True, remove all children of the given 
        type.'''

        self.get(arg).unlink()

    def remove_all(self, tt):
        '''Remove all elements of the given type'''

        for obj in self.get_all(tt):
            obj.unlink()

    def clear(self):
        '''Remove and unparent all children.
        
        Return a list of the unparented children.'''

        return self.children.clear()

    # Other functions
    def children_source(self):
        '''Return a string concatenating the source code of all children'''

        return ''.join(elem.source() for elem in self)

    def source(self):
        '''The default implementation for source() in groups is identical to 
        children_source()'''

        return self.children_source()

    def revalue(self, method, *args, **kwds):
        '''Post-parsing in container types simply apply this function to the 
        first child and then subsequently to its .next attribute until the list
        ends'''

        if self.children:
            obj = self.children[0]
            while obj is not None:
                new = obj.revalue(method, *args, **kwds)
                nxt = obj.next
                if new is None:
                    obj.unlink()
                elif new is not obj:
                    try:
                        obj.replace_by(new)

                    # Raised when new is not a TeXElement type
                    except TypeError:
                        msg = 'invalid %s revalue obtained from %s element'
                        msg = msg % (type(new), type(obj))
                        raise TypeError(msg)

                    # Raised when returned object is already in a masterlist
                    except ValueError as e:
                        msg = '%s object revalued to a parented object' % type(obj).__name__
                        msg += '\n            %s' % e
                        raise ValueError(msg)

                obj = nxt

        return TeXElement.revalue(self, method, *args, **kwds)

class Sequence(TeXContainer, MutableSequence):
    '''Represents a sequence of TeXElements'''

    def __init__(self, data=()):
        super(Sequence, self).__init__(children=data)

    def __len__(self):
        return len(self.children)

    def __delitem__(self, index):
        del self.children[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    def __contains__(self, value):
        for x in self.children:
            if x == value:
                return True
        else:
            return False

    def __getitem__(self, idx):
        return self.children[idx]

    def insert(self, index, value):
        self.children.insert(index, value)

    @classmethod
    def from_data(cls, data):
        return cls(data)

    @classmethod
    def as_element(cls, obj):
        '''Return obj, if object is a TeXElement or a 1-sized list of 
        TeXElements. Otherwise, return the Join of the elements in this list'''

        if type(obj) is cls:
            return obj if len(obj) != 1 else obj[0]
        elif isinstance(obj, TeXElement):
            return obj
        else:
            if len(obj) == 1:
                if isinstance(obj[0], TeXElement):
                    return obj[0]
                else:
                    tname = type(obj).__name__
                    raise TypeError('not a TeXElement: %s' % tname)
            else:
                return cls.from_data(obj)

    @classmethod
    def as_join(cls, obj):
        if type(obj) is cls:  # avoid subtypes
            return obj
        elif isinstance(obj, TeXElement):
            return cls.from_data([obj])
        else:
            return cls.from_data(obj)

    @classmethod
    def as_list(cls, obj):
        if type(obj) is cls:
            return list(obj)
        elif isinstance(obj, TeXElement):
            return [obj]
        elif isinstance(obj, list):
            value = obj
        else:
            value = list(obj)

        assert all(isinstance(x, TeXElement) for x in value)
        return value

class Join(Sequence):
    pass

class Group(Sequence):
    '''Represents grouped elements. Usually items like {<children>}'''

    def __init__(self, bgroup, data, egroup):
        super(Group, self).__init__(data)
        self.bgroup = str(bgroup)
        self.egroup = str(egroup)

    def source(self):
        return self.bgroup + self.children_source() + self.egroup

    @property
    def grouping(self):
        return self.bgroup + self.egroup or None

    @classmethod
    def from_data(cls, data):
        return cls('{', data, '}')


class List(Sequence):
    '''A TeXElement that behaves like a python list'''

    def __init__(self, data, sep=', ', brackets='[]'):
        brackets = brackets or ('', '')
        self.sep = str(sep)
        self.blist = str(brackets[0])
        self.elist = str(brackets[1])
        super(List, self).__init__(data)

    def source(self):
        return self.blist + self.children_source() + self.elist

    def children_source(self):
        return self.sep.join(x.source() for x in self.children)

    @property
    def brakets(self):
        return (self.blist, self.elist)

#===============================================================================
# Other types
#===============================================================================
class Integer(TeXElement, int):
    def __init__(self, data):
        int.__init__(data)

    def source(self):
        return int.__str__(self)

#===============================================================================
# Clean namespace
#===============================================================================
del Element, MutableSequence

if __name__ == '__main__':
    import doctest
    doctest.testmod()
