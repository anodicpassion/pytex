if __name__ == '__main__':
    import pytex; __package__ = 'pytex.textypes'  # @UnusedImport @ReservedAssignment

from . import Command, TeXContainer, tk
from ..types.metatypes import EnvironmentMeta
from ..context import Context
from ..util.splitters import strip

class EndEnvironment(Command):
    '''Base command that defines the ending of an environment'''

    is_abstract = True

class BeginEnvironment(Command):
    '''Base command that defines the beginning of an environment'''

    is_abstract = True
    endmacro = EndEnvironment

    @classmethod
    def invoke(cls, job, tokens, *, invoke_macro=False):
        '''Creates Environment object'''

        if invoke_macro:
            return super(BeginEnvironment, cls).invoke(job, tokens)
        else:
            return cls.environment.invoke(job, tokens)

EnvironmentMeta.register_macros(BeginEnvironment, EndEnvironment)

#===============================================================================
# Environment class
#===============================================================================
class Environment(TeXContainer, metaclass=EnvironmentMeta):
    r"""Base class for all Python-based LaTeX environments.
    
    Subclasses of this class define new LaTeX environments.
    
    Both in LaTeX and in pytex, the command "\begin{environment}" is expanded to
    \beginenvironment, which is then used to initialized the environment. It process
    tokens until \endenvironment is called, which is just the expansion of 
    "\end{environment}"
    
    The metaclass automatically define the `.begin_macro` and `.end_macro` attributes
    as these two macros. Subclasses may override the environment name by 
    setting the `.env_name` attribute and the `.argspec` that shall be passed
    to the "\beginenvironment" macro.
    
    
    Usage
    -----
    
    User must subclass Environment in order to create new environments.
    
    >>> from pytex import TeX
    >>> class foo(Environment):
    ...     pass
    
    >>> tex = r'''\begin{foo}
    ... Some data
    ... \end{foo}'''
    >>> TeX(tex)
    TeXStream([foo(['Some data'])])
    """
    abstract = True
    argspec = None
    env_name = None
    trim_newlines = True
    support_macros = [BeginEnvironment, EndEnvironment]

    def __init__(self, children=None, **kwargs):  # @ReservedAssignment
        super(Environment, self).__init__(children=children)
        self.args = self.argspec.new_arguments(**kwargs)
        self.args.owner = self

    def source(self):
        begin = '\\begin{%s}%s' % (self.env_name, self.args.source())
        end = '\\end{%s}' % self.env_name
        body = self.children_source()
        sep1 = '' if body.startswith('\n') else '\n'
        sep2 = '' if body.endswith('\n') else '\n'
        return ''.join([begin, sep1, body, sep2, end])

    def load_subcommands(self, context=None):
        '''Load all subcommands in the current context'''

        context = self.context if context is None else context
        for sub in self.sub_macros:
            context.save_macro(sub)
        for sub in self.sub_environments:
            context.save_environment(sub)

    @classmethod
    def new(cls):
        '''An empty constructor for objects of the class'''
        return cls()

    @classmethod
    def invoke(cls, job, tokens):
        '''Invoke in an enviroment works in three steps: 
        
        1) read the \beginenvironment[opt]{args} macro with `.invoke_macro()`
        2) save its arguments back to the environment 
        2) creates an iterator that stops at the \endenviroment macro
        3) feed this iterator to `.invoke_body()`. It should return a list of
           TeXElements to be appended to the new environment's children.
        '''

        # Read \beginenvironment macro and its arguments
        new = cls.new()
        macro = cls.invoke_macro(job, tokens, new)
        new.args = macro.args
        new.args.owner = new

        # Invoke the contents of the body
        with job.context.grouping():
            trunc_tokens = tokens.stopping_before_macro(cls.end_macro.macro_name)
            body = cls.invoke_body(job, trunc_tokens, new)
            if not isinstance(body, (list, tuple)):
                raise ValueError('invoke_body must return a list, got %s' % type(body).__name__)
            new.add(body)

        # Get the \endenvironment macro
        tokens.get_macro(cls.end_macro.macro_name)
        return new

    @classmethod
    def invoke_macro(cls, job, tokens, new):
        '''This classmethod should return the \beginenvironment macro initialized
        with all its arguments'''

        return cls.begin_macro.invoke(job, tokens, invoke_macro=True)

    @classmethod
    def invoke_body(cls, job, tokens, new):
        '''This classmethod should a list of elements to be inserted as children 
        of the newly created environment.'''

        data = job.read_all(tokens)
        if cls.trim_newlines:
            strip(data)
        return data

    @classmethod
    def new_environment(cls, name, argspec=''):
        '''Creates a new environment from the given name and argspec'''

        return type(name, (cls,), {'env_name': name, 'argspec': argspec})


#===============================================================================
# Base class for the \begin and \end commands in LaTeX
#===============================================================================
class BeginEnv(Command):
    r'''Beginning of an environment.
    
    The \begin{env} and \end{env} are expanded to \env and \endenv 
    commands. These commands should generate the proper Environment objects to
    be put in the parse stream.'''

    argspec = '{env_name:str}'
    is_abstract = True

    @classmethod
    def invoke(cls, job, tokens):
        bcmd = super(BeginEnv, cls).invoke(job, tokens)
        btok = tk.TkEscape(bcmd.command_name[0] + bcmd.env_name)
        tokens.push(btok)
        beginenv = job.get_environment(bcmd.env_name, warn=1)
        return beginenv.invoke(job, tokens)

class EndEnv(Command):
    '''End of an environment'''

    argspec = '{env_name:str}'
    is_abstract = True

    @classmethod
    def invoke(cls, job, tokens):
        end_str = 'end'
        ecmd = super(EndEnv, cls).invoke(job, tokens)
        etok = tk.TkEscape(ecmd.command_name[0] + end_str + ecmd.env_name)
        try:
            job.get_macro(str(etok)[1:], warn=2)
        except ValueError:
            raise ValueError('unknown end command: %s' % ecmd.source())
        tokens.push(etok)
        return None

#===============================================================================
# Register itself in the Context classs. This is done here in order to avoid
# depedency loops between modules
#===============================================================================
Context._new_environment = Environment.new_environment
Context._ENVIRONMENT = Environment

if __name__ == '__main__':
    import doctest
    doctest.testmod()
