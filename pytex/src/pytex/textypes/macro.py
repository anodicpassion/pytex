if __name__ == '__main__':
    import pytex; __package__ = 'pytex.elements'  # @UnusedImport @ReservedAssignment

from . import TeXElement, Text
from ..types.metatypes import MacroMeta
from ..context import Context

__all__ = ['Macro', 'Command']

NoneType = type(None)

class Macro(TeXElement, metaclass=MacroMeta):
    '''Base macro class. Represents unexpanded macros and implements the 
    invoke()/expand() mechanism.
    
    Apart from the regular initialization, Macro instances can be initializated
    from the current TeX processor and a list of tokens. In this case, the 
    ``.invoke(job, tokens)`` method is called to  read a sequence of tokens and 
    extract the argument values.
    
    Afterwards, the ``.expand(job, tokens)`` method is called. It can return an 
    expanded object that should be added to the document or None to supress the 
    object. Non-expandable objects simply return themselves. A common pattern
    which mimmicks the way that the TeX processor works is to push tokens and 
    then return None so the object is not added to the document. 
    
    '''
    is_abstract = True
    force_expand = False
    argspec = ''

    def __init__(self, *args, **kwargs):  # @ReservedAssignment
        super(Macro, self).__init__()
        self.args = self.argspec.new_arguments(*args, **kwargs)
        self.args.owner = self

        # Detect API change
        if hasattr(self, 'from_job'):
            raise RuntimeError(type(self))

    def __repr__(self):
        return '<%s%s macro>' % (self.command_name, self.args.source(trunc=8))

    def _subitems_(self):
        return iter(self.args)

    def source(self):
        '''Return a string with the LaTeX source code of the given macro'''

        src = [self.command_name]
        argsource = self.args.source()

        # Control whitespaces between macro and arguments
        if argsource:
            src.append(argsource if not argsource[0].isalpha() else ' ' + argsource)

        # Control whitespace between macro and the next element
        if isinstance(self.next, Text) and self.next and self.next[0].isalpha():
            src.append(' ')

        return ''.join(src)

    def expand(self, job, tokens):
        '''Expands the macro. The default behavior is to return itself, telling 
        that the macro cannot be further expanded.
        
        Subclasses may override this method and manually compute the expansion
        and insert tokens to the `tokens` tokenizer and return None.'''

        return self

    def expand_to_object(self):
        '''This method can be called by converters in order to force expansion
        of non-recognized objects. This expansion may be recognized and 
        converted to the proper output.
        
        The default behavior is to use the implemenation on expand.'''

        # Check if the object is non expandable or if its expansion does not
        # mess up with the tokens or the job object
        try:
            # TODO: create a Pseudo object that raises a predictable exception
            # upon any interaction
            return self.expand(None, None)
        except Exception:
            pass

        # Creates a job and a tokens object that shares context with self
        raise NotImplementedError

    @classmethod
    def invoke(cls, job, tokens):
        '''Invoke Macro object from a list of tokens. It reads and initializes
        the arguments and use them to create output.
        
        Some macros perform additional operation at this step. The result in not 
        necessarely a Macro object. (e.g.: \begin{environment} will invoke an
        Environment object, and not a Macro)'''

        # Read macro token
        tokens.get_macro(cls.macro_name)

        # Initialize object and read arguments
        obj = cls()
        obj.args = cls.argspec.invoke(job, tokens, obj)

        return obj

    @classmethod
    def new_macro(cls, name, argspec='', base=None):
        '''Creates a new macro class from name and argspec'''

        if base == 'self':
            base = cls
        base = base or UnknownCommand
        return type(str(name), (base,), {'name': name, 'argspec': argspec})

    def revalue(self, method, *args, **kwds):
        '''Apply revalue to all TeX object arguments'''

        for name, value in self.args.items():
            if isinstance(value, TeXElement):
                new = value.revalue(method, *args, **kwds)
                if new is not value:
                    self.args[name] = new

        return super(Macro, self).revalue(method, *args, **kwds)

class Command(Macro):
    """ Base class for all Python-based LaTeX commands """
    is_abstract = True

class UnknownCommand(Command):
    """ Base class for unknwon commands """
    is_abstract = True

#===============================================================================
# Configure the Context class to be able to create new Macros
#===============================================================================
Context._new_macro = Macro.new_macro
Context._MACRO = Macro

if __name__ == '__main__':
    import doctest
    doctest.testmod()
