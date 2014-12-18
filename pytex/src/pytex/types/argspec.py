if __name__ == '__main__':
    import pytex; __package__ = 'pytex.types'  # @UnusedImport @ReservedAssignment

from collections import Mapping
import warnings
from .. import tokens as tk

#===============================================================================
# Delayed imports
#===============================================================================
# This variable is set during the construction of the pytex.texlements
# module in order to avoid a circular dependency between the two modules.
#
tex = None

#===============================================================================
# Argspec types
#===============================================================================
class Argspec(Mapping):
    '''Specifies the names/types of arguments of a macro or environment.
    
    Argspec objects are initialized from 'argspec' strings or from other Argspec
    objects. They are implemented as a mapping between argument names to their
    specification (which is a ArgAtom object).
    
    Usage
    -----
    
    >>> argspec = Argspec('[options:dict]{names:list}')
    >>> for arg in argspec:
    ...     print('%s = %s' % (arg, argspec[arg]))
    options = ArgAtom('options', type='dict', grouping='[]')
    names = ArgAtom('names', type='list')
    '''
    def __init__(self, argspec, owner=None):
        # Copy data from other Argspec object, if first argument
        if isinstance(argspec, Argspec):
            argspec = argspec._declaration

        # Initialize from a string
        self._declaration = str(argspec or '')
        self._argnames = []
        self._data = {}
        self.owner = owner

        # Read and process the list of ArgAtom objects
        atoms = read_arg_atoms(self._declaration, self)
        self._argnames.extend(atom.name for atom in atoms)
        self._data.update({ atom.name: atom for atom in atoms })

        # Define self as the parent argspec atribute of each atom
        for atom in atoms:
            atom.argspec = self

    def __repr__(self):
        if self.owner:
            return 'Argspec(%r, %r)' % (self._declaration, self.owner)
        else:
            return 'Argspec(%r)' % self._declaration

    def __getitem__(self, name):
        return self._data[name]

    def __iter__(self):
        for name in self._argnames:
            yield name

    def __len__(self):
        return self._argnames

    @property
    def full_declaration(self):
        return getattr(self.owner, 'command_name', '<unknown macro>') + self._declaration

    def invoke(self, job, tokens, owner=None):
        '''Read an Argument object from the parsing job'''

        arguments = tex.Arguments(argspec=self, owner=owner)
        for name, spec in self.items():
            value = spec.invoke(job, tokens, owner)
            arguments[name] = value
        return arguments

    def new_arguments(self, *args, **data):
        '''Return a new Arguments object initialized from the given keyword
        arguments'''

        for argname, value in zip(self, args):
            data[argname] = value
        return tex.Arguments(self, owner=None, data=data)

    def get_property(self, argname):
        '''Return a property object that access the given argument'''

        if argname not in self:
            raise ValueError('unrecognized argument: %r' % argname)

        @property
        def fget(self):
            return self.args[argname]

        @fget.setter
        def fset(self, value):
            self.args[argname] = value

        return fget

class ArgAtom:
    """Specification for a single Macro argument.
    
    Members of this class store the information necessary to read a sequence of 
    tokens in search for an argument of a given type.
    """

    BRACKET_MATCHES = {None: None, '[': ']', '(': ')', '<': '>'}

    def __init__(self, name, type='tex', grouping=None, argspec=None):  # @ReservedAssignment
        if not isinstance(name, str):
            raise TypeError('expected string, got %s' % type(name).__name__)
        self.name = name
        self.argspec = argspec
        self.grouping = grouping

        # Initializes the type specification
        self.type, self.tt_args, self.tt_kwargs = typeargs(type)

        # Choose the correct reader and source functions according to the type
        # specification
        try:
            self._read = getattr(self, 'read_' + self.type)
            self._source = getattr(self, 'source_' + self.type)
        except AttributeError:
            msg = 'type not supported: %s' % self.type
            if (self.argspec is not None):
                msg = 'wrong type at declaration at "%s": %s' % \
                            (self.argspec.full_declaration, self.type)
                warnings.warn(msg)
            else:
                raise ValueError(msg)

    def __repr__(self):
        opt = [repr(self.name)]
        for attr in ['type', 'grouping']:
            if getattr(self, attr) is not None:
                opt.append('%s=%r' % (attr, getattr(self, attr)))
        return 'ArgAtom(%s)' % (', '.join(opt))

    @property
    def owner(self):
        return getattr(self.argspec, 'owner', None)

    @property
    def bgroup(self):
        if self.grouping is None:
            return None
        else:
            return self.grouping[0]

    @property
    def egroup(self):
        if self.grouping is None:
            return None
        else:
            return self.grouping[1]

    #===========================================================================
    # Reader functions
    #===========================================================================
    def invoke(self, job, tokens, owner=None):
        '''Read the next argument from a job object and a list of tokens'''

        # If grouping is defined, read data and process all data until the grouping
        # character is found
        if self.grouping:
            if  self.bgroup == tokens.tell_next():
                next(tokens)
                trunc_tokens = tokens.stopping_before(self.egroup)
                data = self._read(job, trunc_tokens, owner, greedy=True)
                tokens.get_specific(self.egroup)
            else:
                data = None

        # The non-grouping case is more complicated since we cannot expect the
        # grouping delimiters to be present. We first check for this and proceed
        # as before if a \bgroup token was found. Otherwise we delegate this
        # task to the read_ method associated to which type.
        else:
            if isinstance(tokens.tell_next(), tk.TkBGroup):
                group = job.read_next(tokens)
                data = tex.Join(group.clear())

                if self.type == 'tex':
                    return data
                elif self.type == 'str':
                    return tex.TeXString(data.source())
                elif self.type == 'int':
                    return tex.Integer(data.source().strip())
                else:
                    tokens = data.tokenize()
                    data = self._read(job, tokens, owner, greedy=True)

            else:
                data = self._read(job, tokens, owner, greedy=False)

        assert data is None or isinstance(data, tex.TeXElement), 'unexpected type as %s: %s' % (self.type, type(data))
        return data

    def read_tex(self, job, tokens, owner=None, greedy=False):
        '''Argument is a TeX element. Return a Group if multiple elements are
        found or a single element otherwise'''

        # Process the whole token stream and return everything in it
        if greedy:
            data = job.read_all(tokens)
            if len(data) == 0:
                return None
            elif len(data) == 1:
                return data[0]
            else:
                return tex.Join(data)

        # Non-greedy reading is more complicated. It must return the next
        # single TeX element. Spaces must be skipped, only a single letter
        # shall be used. All other objects are created normally.
        else:
            for tok in tokens:
                if isinstance(tok, (tk.TkSpace, tk.TkEOL, tk.TkSkipped)):
                    continue
                elif isinstance(tok, (tk.TkLetter, tk.TkOther)):
                    return tex.Text(tok)
                else:
                    tokens.push(tok)
                    return job.read_next(tokens)
            raise EOFError

    def read_str(self, job, tokens, owner=None, greedy=False):
        '''Read the tokens stream as a string'''

        if greedy:
            return tex.TeXString(''.join(tokens))
        else:
            data = self.read_tex(job, tokens, owner, greedy)
            if isinstance(data, tex.Group):
                return tex.TeXString(data.children_source())
            else:
                return tex.TeXString(data.source())

    def read_dict(self, job, tokens, owner=None, greedy=False):
        '''Process arguments and return them as a dictionary of key=value pairs'''

        # For now, only dictionaries of string types are supported
        if self.tt_args and self.tt_args != ('str',):
            raise NotImplementedError

        # Create the dictionary and populate with data from the argument string
        dic = tex.DictListArg({})
        data = self.read_str(job, tokens, owner, greedy).split(',')
        for datum in data:
            key, _, value = datum.partition('=')
            key = key.strip()
            value = value.strip() or True
            dic[key] = value

        return dic or None

    def read_list(self, job, tokens, owner=None, greedy=False):
        '''Read argument as a list of strings'''

        data = self.read_str(job, tokens, owner, greedy)
        return tex.List([ x.strip() for x in data.split(',') ], brackets=None)

    # TODO: implement these properly
    def read_not_implemented_properly(self, job, tokens, owner=None, greedy=False):
        '''Generic implementation for non-implemented types'''

        warnings.warn('reading unsupported argument of type %s as string' % self.type)
        return self.read_str(job, tokens, owner, greedy)

    def read_tok(self, job, tokens, owner=None, greedy=False):
        return next(tokens)

    def read_int(self, job, tokens, owner=None, greedy=False):
        out = job.read_int(tokens)
        if greedy:
            tokens.skip_whitespace()
            if tokens.get_next() is not None:
                raise ValueError('some tokens were not consumed')
        return out

    read_dimen = read_not_implemented_properly

    #===========================================================================
    # Source formatting functions
    #===========================================================================
    def source(self, arg, trunc=None, owner=None):
        '''Return the source code for some argument'''

        if isinstance(arg, tex.EmptyArg):
            if self.grouping:
                return ''
            else:
                warnings.warn('empty required %s argument of %s' % (self.name, self.argspec.full_declaration))
                return ''
        return self._source(arg, trunc=trunc)

    def source_str(self, arg, trunc=None, owner=None):
        '''Render string objects'''

        if trunc is not None and len(arg) > trunc:
            arg = arg[:trunc - 1] + '...'
        grouping = self.grouping or '{}'
        return ''.join([grouping[0], arg, grouping[1]])

    def source_tex(self, arg, trunc=None, owner=None):
        '''Renders some arbitrary TeX element into a source string'''

        data = arg.source()
        if isinstance(arg, tex.Group) and arg.grouping == '{}':
            return self.source_str(data[1:-1], trunc, owner)
        else:
            return self.source_str(data, trunc, owner)

    def source_dict(self, arg, trunc=None, owner=None):
        '''Renders a dictionary argument as string'''

        return self.source_str(arg.source(), trunc, owner)

    def source_list(self, arg, trunc=None, owner=None):
        '''Renders a list of argument as string'''

        return self.source_str(arg.source(), trunc, owner)

    def source_tok(self, arg, trunc=None, owner=None):
        '''Renders a TeX token as string'''
        return str(arg)

    def source_int(self, arg, trunc=None, owner=None):
        '''Renders an integer as string'''
        return str(arg)

    # TODO: implement these properly
    def source_not_implemented_properly(self, arg, trunc, owner):
        '''Generic implementation for non-implemented types'''

        warnings.warn('rendering an unsupported argument of type %s as string' % self.type)
        return self.source_str(str(arg), trunc, owner)

    source_dimen = source_not_implemented_properly

#===========================================================================
# Utility functions
#===========================================================================
def typeargs(fmt_str):
    '''Convert a type format string into a triple (type_name, args, kwargs)
    
    Example
    -------
    
    >>> typeargs("foo(arg1, arg2, karg=bar)")
    ('foo', ('arg1', 'arg2'), {'karg': 'bar'})
    '''

    # Retrieve defaults for empty strings (or None)
    if not fmt_str:
        return ('tex', (), {})

    # Extract the type name
    tt, _, args_str = fmt_str.partition('(')

    # Extract _data
    args_str = args_str.rstrip(') ')
    if args_str:
        args = []
        kwargs = {}
        for item in args_str.split(','):
            name, _, value = item.partition('=')
            if value:
                kwargs[name.strip()] = value.strip()
            else:
                args.append(name.strip())
        return tt, tuple(args), kwargs
    else:
        return (tt, (), {})

def read_arg_atoms(argstr, parent=None):
    '''Convert a format string for arguments into a list of ArgAtom's objects
    
    Examples
    --------
    
    >>> read_arg_atoms('[options:dict]{packages:list}')
    [ArgAtom('options', type='dict', grouping='[]'), ArgAtom('packages', type='list')]
    '''
    if not argstr:
        return []

    matches = {'[': ']', '{': '}', '<': '>'}
    matches_inv = { v: k for (k, v) in matches.items() }
    whitespace = set(' \t')
    atoms_list = []

    chars = list(reversed(argstr))
    while chars:
        char = chars.pop()

        # Find the content inside brackets: e.g.: [arg1] or [arg2]
        if char in matches:
            arg = []
            egroup = matches[char]
            while char != egroup:
                char = chars.pop()
                arg.append(char)
            char = matches_inv[char] + char  # reverse the bracket mapping to get the bgroup character
            char = char if char != '{}' else None
            arg.pop()
            arg = ''.join(arg)
            name, _, tt = arg.partition(':')
            atoms_list.append(ArgAtom(name, type=tt, grouping=char, argspec=parent))

        elif char in whitespace:
            continue

        else:
            raise RuntimeError('invalid argument spec string: %s' % argstr)

    return atoms_list

if __name__ == '__main__':
    import doctest
    doctest.testmod()
