if __name__ == '__main__' and __package__ is None:
    import pytex.alttex; __package__ = 'pytex.alttex'  # @UnusedImport @ReservedAssignment

from pytex.util import print_capture
from pytex.textypes import TeXString
from pytex.util.errors import render_error
from .namespace import Namespace
from .auxtypes import Choices
from . import script
import pygments.lexers
import pygments.formatters

#===============================================================================
# Namespace code handlers
#===============================================================================
class Runner:
    '''Run some code inside a TeX document.
    
    Code can be used to print messages or to set internal variables
    '''
    def __init__(self, source):
        self.source = source
        self.exec_context = None

    def run(self, max_tries=None, timeout=None):
        '''Tries to run the code object serveral times until an answer is 
        obtained. It calls the obj.runonce() method as needed.'''

        return self.runonce()

    def runonce(self):
        '''Runs the code once and returns a string with the print output.'''

        raise NotImplementedError

    def eval(self, max_tries=None, timeout=None):
        '''Similar to run(), but evaluates code and returns its result rather 
        then the print output'''

        return self.evalonce()

    def evalonce(self):
        '''Evaluates the code once and retunrs the result'''

        raise NotImplementedError

    def prepare(self, obj):
        '''Prepare a context for running the code. The context may depends on 
        the position of the given obj in the document hierarchy.'''

        raise NotImplementedError

    def context_create(self):
        '''Returns a new object representing the execution context for that 
        job'''

        return {}

    def context_copy(self, context):
        '''Used internally to create copies of context objects in order to avoid
        with its internal state'''

        return context.copy()

    def get_namespace(self, obj):
        '''Return a TeXElement that stores information about the execution 
        context. Return None when not necessary to store this information.'''

        raise NotImplementedError

    @property
    def valid_context(self):
        if self.exec_context is not None:
            return self.exec_context
        else:
            return self.context_create()

class GRunner(Runner):
    '''Base class for all global runners.
    
    Global runners are defined by languages that start with a 'g' (e.g., 'gpython').
    They distinguish from local runners in that a single execution context is
    shared for all document.
    '''

    def prepare(self, obj):
        '''Global runners mantain a unique global context in the master object
        for each different language.'''

        # Get global namespaces
        master = obj.master
        try:
            ctx_dict = master.gcode_contexts
        except AttributeError:
            ctx_dict = master.gcode_contexts = {}

        # Select language
        try:
            self.exec_context = ctx_dict[self.language]
        except KeyError:
            self.exec_context = ctx_dict[self.language] = self.context_create()

class LRunner(Runner):
    '''Base class for all local runners.
    
    Local runners have a context defined hierachically inside the document. Each
    execution context inherits properties from any context defined in parent 
    objects inside the document tree.
    '''
    def prepare(self, obj):
        '''Local runners mantain a different context for each hierarchy level.
        in the document tree.'''

        self.exec_context = self.context_create()

class PyRunner(Runner):
    @property
    def code_exec(self):
        return compile(self.source, '<input>', 'exec')

    @property
    def code_eval(self):
        return compile(self.source, '<input>', 'eval')

    def runonce(self):
        '''Executes some python code and return a string with the printed output'''

        with print_capture() as st:
            exec(self.code_exec, self.exec_context)
        return str(st).strip()

    def evalonce(self):
        return eval(self.code_eval, self.namespace)

    def context_create(self):
        ctx = {}
        for k, v in vars(script).items():
            if not k.startswith('_'):
                ctx[k] = v
        return ctx

    def format_error(self, error):
        '''Format some exception for displaying inside a document.'''

        pylex = pygments.lexers.get_lexer_by_name('python')
        texfmt = pygments.formatters.get_formatter_by_name('latex')
        texfmt.linenos = True
        tex = pygments.highlight(self.source, pylex, texfmt)
        tb = render_error(type(error), error, error.__traceback__)
        return TeXString('\\begin{minipage}[t]{1\\columnwidth}\n\\textbf{Python Error}\n%s\n\n\\textbf{Traceback}\n%s$$ $$\\end{minipage}' % (tex, tb)), error

    def get_namespace(self):
        return dict(self.exec_context.get('ns', {}))

class GPythonR(PyRunner, GRunner):
    language = 'gpython'

class PythonR(PyRunner, LRunner):
    language = 'python'

    def context_create(self):
        # Add namespace, choices, etc
        ctx = super(PythonR, self).context_create()
        ns = ctx['ns'] = ctx['namespace'] = Namespace()
        ctx['choices'] = ctx['choices0'] = Choices()
        ns.choices0 = ns.choices = ctx['choices']
        for i in range(1, 10):
            ci = ctx['choices%s' % i] = Choices()
            setattr(ns, 'choices%i' % i, ci)

        return ctx

RUNNERS = {'gpython': GPythonR,
           'python': PythonR}

def get_runner(language, code, texobject):
    runner = RUNNERS[language](code)
    runner.prepare(texobject)
    return runner

#===============================================================================
# Filters
#===============================================================================
def apply_filters(var, filters, filters_lib):
    '''Apply a list of filters in variable'''

    if var is None:
        return TeXString('')
    for F in (filters or ()):
        var = filters_lib[F](var)
    out = finalize(var)

    if out is var:
        return var.copy()
    else:
        return var

def finalize(value):
    if isinstance(value, TeXElement):
        return value
    else:
        return TeXString(escape_tex(str(value)))


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    from .altsource import AltSource

    tex = r'''\begin{namespace}{python}
ns.foo = 1
ns.bar = 2
\end{namespace}foo=\var{foo}'''

    print()
    doc = AltSource(tex)
    print(doc.get_all_sources())
    print(doc.get_all_sources('foo'))


