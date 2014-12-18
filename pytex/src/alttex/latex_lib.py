if __name__ == '__main__' and __package__ is None:
    import pytex.alttex; __package__ = 'pytex.alttex'  # @UnusedImport @ReservedAssignment

from pytex import (TeX, TeXElement, TeXString, Text, Group, List, Join, Command,
                Environment)
from pytex.util import (walk_items, strip, split_str, partition_type,
                     roman, letter, lcm, lyx_to_tex, escape_tex)
from pytex.util.texfy import TeXfy
from pytex.lib import latex
from . import filters
from .external_code import get_runner
import collections
import warnings
import random
import math
import os

# Store post-import namespace in order to remove names afterwards
__all__ = dir()

#===============================================================================
# Constants
#===============================================================================
class secname(Command):
    r'''\secname  ==> expand to the name of the current section'''

    def revalue_alttex(self, section, idx, **kwds):
        return Text(section or 'default')

class maxversions(Command):
    r'''\maxversions  ==> expand to the number of versions of the current job'''

class setversions(Command):
    r'''\setversions{value:int}  ==> define the default number of versions 
    of the current job.'''

    def revalue_alttex(self, section, idx, **kwds):
        # The job is actually done by AltSource, which searches for this command
        # and then sets the correct number of versions
        return None

class altidx(Command):
    r'''\altidx{begin:str}  ==> expand to the index of the current version'''

    def revalue_alttex(self, section, idx, **kwds):
        begin = self.begin or '1'

        if begin.isdigit():
            return Text(str(idx + int(begin)))
        elif begin in ['letter', 'l']:
            return Text(letter(idx))
        elif begin in ['LETTER', 'L']:
            return Text(letter(idx).upper())
        elif begin in ['roman', 'r']:
            return Text(roman(idx + 1).lower())
        elif begin in ['ROMAN', 'R']:
            return Text(roman(idx + 1).upper())
        else:
            raise ValueError('invalid optional specification: %s' % begin)

#===============================================================================
# The \alt command and friends
#===============================================================================
class alt(Command):
    r'''The \alt command define alternative values that can change between 
    different versions of the same document
    
    Example
    -------
    
    >>> alts = AltSource(r'\alt{a|b|c}'); alts.get_template()
    TeXStream([<\alt{a|b|c} macro>])
    
    >>> alts.get_all_sources()
    ['a', 'b', 'c']
    
    Or for alternative sections...
    
    >>> alts = AltSource(r'\alt[foo, bar]{1|2|3}')
    >>> alts.get_all_sources('foo')
    ['1', '2', '3']
    
    '''

    argspec = '[sections:list(str)]{data:tex}'

    def __init__(self, data=None, sections=None):
        super(alt, self).__init__()

        if sections is not None:
            sections = list(sections)
        if data is not None:
            data = map(Join.as_element, data)
            data = List(split_str(Group.as_list(data), '|'), brackets=None, sep='|')
        self.sections = sections
        self.data = data

    @classmethod
    def invoke(cls, job, tokens):
        '''Read argument and populate children from the "|" separated options'''

        # Invoke command normally
        new = super(alt, cls).invoke(job, tokens)
        data = split_str(new.data.clear(), '|')
        data = map(Join.as_element, data)
        new.data = List(data, brackets=None, sep='|')
        return new

    @property
    def alt_size(self):
        return len(self.data)

    @property
    def alt_sections(self):
        return self.sections

    def revalue_alttex(self, section, idx, **kwds):
        '''Picks up the correct option'''

        if self.sections and (section not in self.sections):
            return Text('')
        else:
            result = self.data.children.pop(idx % len(self.data))
            return result.revalue('alttex', section, idx, **kwds)

class altcond(Command):
    r'''Similar to \alt, but requires an obligatory sections argument and it
    also define an "else" part to be executed if not in the specified sections.
    '''

    argspec = '{sections:list(str)}{ifdata}{elsedata}'
    def __init__(self, sections=None, ifdata=None, elsedata=None):
        super(altcond, self).__init__()
        self.sections = List((TeXfy(x) for x in (sections or [])), brackets='')
        self.ifdata = List((TeXfy(x) for x in (ifdata or [])), brackets='', sep='|')
        self.elsedata = List((TeXfy(x) for x in (elsedata or [])), brackets='', sep='|')

    @classmethod
    def invoke(cls, job, tokens):
        '''Read argument and populate children from the "|" separated options'''

        # Invoke command normally
        new = super(altcond, cls).invoke(job, tokens)

        ifdata = split_str(new.ifdata.clear(), '|')
        ifdata = map(Join.as_element, ifdata)
        new.ifdata = List(ifdata, brackets=None, sep='|')

        elsedata = split_str(new.elsedata.clear(), '|')
        elsedata = map(Join.as_element, elsedata)
        new.elsedata = List(elsedata, brackets=None, sep='|')

        if len(new.ifdata) != len(new.elsedata):
            warnings.warn('ifdata has different length of elsedata (%s != %s)' % (len(ifdata), len(elsedata)))
        return new

    @property
    def alt_size(self):
        return lcm([len(self.ifdata), len(self.elsedata)])

    @property
    def alt_sections(self):
        return self.args[0]

    def revalue_alttex(self, section, idx, **kwds):
        '''Picks up the correct option'''

        if section in self.sections:
            result = self.ifdata.children.pop(idx % len(self.ifdata))
            return result.revalue('alttex', section, idx, **kwds)
        else:
            result = self.elsedata.children.pop(idx % len(self.elsedata))
            return result.revalue('alttex', section, idx, **kwds)

#===============================================================================
# Shuffling
#===============================================================================
class shufflepoint(Command):
    '''A command to signal a shuffle point in the TeX stream'''

class shuffle(Environment):
    '''The shuffle environment defines some shuffle points inside the TeX 
    document and it shuffles the elements inside when revalued with 
    `alttex.shuffle = True`'''

    def __init__(self, options=None, tex=None):
        super(shuffle, self).__init__()
        self.children.extend([options or Join(), tex or Join()])

    @property
    def options(self):
        return self.children[0]

    @property
    def body(self):
        return self.children[1]

    @classmethod
    def invoke_body(cls, job, tokens, new):
        '''Read the list of children and find the shuffle points and its 
        possible values in the data stream'''

        options = []
        body = Join(job.read_all(tokens))

        while True:
            # we put this in a while loop in order to process only the first
            # occurrence of a string with a shuffle block opening
            # The workload is:
            #    1) find the first string matching with a '<<'
            #    2) extract the contents until a '>>' is found
            #    3) save it and the previous element into the options list
            #    4) repeat the operation with a new walk_items() search
            #    5) stop repeating when walk_items() finds no matching string
            #
            for obj in walk_items(body, str):
                # Search for the beginning of the shuffle block
                if '<<' in obj:
                    pre, _, post = obj.partition('<<')
                    obj.replace_by(pre)
                    if post:
                        pre.insert_next(post)

                    # create a shuffle point
                    spoint = shufflepoint()
                    if pre:
                        pre.insert_next(spoint)
                    else:
                        pre.replace_by(spoint)
                else:
                    continue

                # Search for the closing tag for the shuffle block
                option = []
                for obj in spoint.get_siblings_next():
                    if isinstance(obj, str) and '>>' in obj:
                        data, _, post = obj.partition('>>')
                        option.append(data)
                        obj.replace_by(post)
                        break
                    else:
                        obj.unlink()
                        option.append(obj)
                else:
                    raise RuntimeError('closing >> block not found!')

                if len(option) == 1:
                    option = option[0]
                else:
                    option = Join(option)

                options.append(option)
            # if the walk_items loop complete without finding any match for a
            # opening block, break the main while loop.
            else:
                break

        # We don't want to extend our children
        # Let us add elements to the existing options and body groups
        new.options.children.extend(options)
        new.body.children.extend(body.children.clear())

        return []

    def children_source(self):
        '''Insert the options in the correct shuffle points'''

        options = self.options
        spoints = []
        try:
            for idx, spoint in enumerate(walk_items(self.body, shufflepoint)):
                text = Text('<<%s>>' % options[idx].source())
                spoint.replace_by(text)
                spoints.append((spoint, text))
            self.options.replace_by(Text(''))
            source = super(shuffle, self).children_source()
        finally:
            for spoint, text in spoints:
                text.replace_by(spoint)
            self.options.replace_by(options)
        return source

    def revalue_alttex(self, section, idx, **kwds):
        '''Picks up the correct option'''

        # Compute a predictable shuffling from the idx argument
        stripped_src = self.options.source()
        stripped_src = ''.join(stripped_src.split())
        random.seed(stripped_src + str(idx))
        options = self.options.revalue('alttex', section, idx, **kwds)
        L = options.children.clear()
        random.shuffle(L)

        # Insert elements in shufle points and return body
        body = self.body.revalue('alttex', section, idx, **kwds)
        for spoint in walk_items(body, shufflepoint):
            spoint.replace_by(L.pop())

        # Create return element
        new = Join(self.body.children.clear())
        return new if len(new) != 1 else new[0]

#===============================================================================
# Include files
#===============================================================================
class libinclude(Command):
    '''A command to include data from some other LyX/LaTeX file in the user's
    library.'''

    argspec = '{filename:str}'

    def __init__(self, filename=''):
        super(Command, self).__init__()
        self.filename = filename

    def get_include_data(self, context=None, strip_meta=True):
        '''Returns the TeX elements inside the included file'''

        if context is None:
            context = self.context
        def process(path):
            '''Process a TeX document file'''

            # Read and process full TeX file
            with open(path, encoding='utf8') as F:
                tex = TeX(F.read(), context=context)

            # Remove title/author/etc data
            if strip_meta:
                elements = tex.document.clear()
                preamble, _, elements = partition_type(elements, latex.maketitle)
                return Join(elements or preamble)
            else:
                return Join(tex.document.clear())

        # Process input file
        path = self.get_include_path()
        if path.endswith('lyx'):
            with lyx_to_tex(path) as tex_path:
                return process(tex_path)
        else:
            return process(path)

    def _get_path(self, path, name, exts=['.lyx', '.tex']):
        '''Return the path to the first valid file name under path.
        
        Example
        -------
        
        In the tree
        
        foo/
          |- bar/
          |   |- foobar.txt
          |   |- foobar.tex
          |   \- README.rst
          \- some_file.txt
          
          
        A call to getfile('foo', 'bar/foobar', ['.tex', '.txt', '.lyx']) will return
        'foo/bar/foobar.tex'. If no matching file is found, returns None.
        '''

        base = prefix = name
        while base:
            if not os.path.exists(path):
                return None
            base, _, prefix = prefix.rpartition('/')
            path = os.path.join(path, base)
        else:
            name = prefix

        # Filter file names that starts with the correct values
        for ext in exts:
            fpath = os.path.join(path, name + ext)
            if os.path.exists(fpath) and os.path.isfile(fpath):
                return fpath

    def get_include_path(self, wpath=None):
        '''Return the full path for the source file to be processed'''

        wpath = wpath or os.getcwd()

        # Generates a list of valid parent paths
        def parent_paths():
            path = wpath
            while True:
                if os.path.exists(os.path.join(path, 'lib')):
                    yield os.path.join(path, 'lib')
                yield path
                new, _ = os.path.split(path)
                if new == path:
                    break
                else:
                    path = new

        # Test each possible path for the existence of a valid file
        for base in parent_paths():
            path = self._get_path(base, self.filename)
            if path:
                return path

    def revalue_includes(self):
        return self.get_include_data()

#===============================================================================
# Question types
#===============================================================================
class Question(Environment):
    '''Base class for all question environments.'''
    pass

class correct(Command):
    '''Command used to mark correct choices.'''

class score(Command):
    '''Command to set the score given to some specific choice or specific 
    question'''

    argspec = '{value:number}'

class feedback(Command):
    '''Define some comment to be returned back to students for any given 
    question or choice'''

    argspec = '{text}'

class comment(Command):
    '''Internal commentary available only to teachers (or the person applying 
    the questions)'''

    argspec = '{text}'

#===============================================================================
# Multiple choice questions
#===============================================================================
class choices(latex.Itemize):
    r'''The choices environment lists the choices from a \multiplechoice 
    question'''

    def __init__(self, choices=None):
        super(_choices_cls, self).__init__()
        if isinstance(choices, _choices_cls):
            raise NotImplementedError
        for choice in (choices or []):
            raise NotImplementedError

    def user_choices(self, idx=None, section=None):
        r'''Iterates over the user-visible data for each choice, discarding all 
        commands such as \correct, \feedback, etc'''

        for choice in self:
            try:
                choice.get(correct)
                is_correct = True
            except ValueError:
                is_correct = False

            choice = choice.copy()
            choice.remove_all(correct)
            choice.remove_all(feedback)
            choice.remove_all(comment)
            choice = Join(choice.clear())

            if is_correct:
                ifdata = choice.copy().revalue('alttex', idx, 'answers')
                ifdata = r'\textcolor{red}{\textbf{<<}~ %s ~\textbf{>>}}' % ifdata.source()
                ifdata = TeXString(ifdata)
                choice = Join([altcond(['answers'], [ifdata], [choice.copy()])])
            yield choice

    def render_horizontal(self, idx=None, section=None):
        '''Render choices horizontally'''

        final = Join()
        final.add(TeXString(' \quad '))
        for idx, choice in enumerate(self.user_choices(idx=idx, section=section)):
            final.add(Text('(%s) ' % letter(idx)))
            final.add(choice.copy())
            final.add(TeXString(' \qquad '))
        final.pop()
        return final

    def render_vertical(self, idx=None, section=None):
        '''Render choices vertically'''

        items = latex.itemize()
        for choice in self.user_choices(idx=idx, section=section):
            items.add(choice)
        return items

    def render_table(self, rows=None, cols=None, idx=None, section=None):
        '''Render choices in a table'''

        if rows is None and cols is None:
            raise ValueError('at least cols or rows must be specified')

        # Define shape for the table
        N = len(self)
        if cols is None:
            cols = math.ceil(N / rows)
        else:
            rows = math.ceil(N / cols)

        final = latex.tabular.empty(rows, cols, lines=False)  # @UndefinedVariable
        cell_choice = zip(final.iter_cells(transpose=True), self.user_choices())
        for idx, (cell, choice) in enumerate(cell_choice):
            label = Text('(%s) ' % letter(idx))
            cell.replace_by(Join([label] + choice.clear()))

        final.set_alignment('left')
        return final

_choices_cls = choices  # Alias to choices(), necessary for the multiplechoice constructor

class multiplechoice(Question):
    '''Represents a multiple choice question'''

    argspec = '[options:dict]'
    fixed_size = 4
    named_fields = ['stem', 'choices', 'feedback', 'comment']

    def __init__(self, stem=None, choices=None, feedback=None, comment=None):
        super(multiplechoice, self).__init__()
        self.children.append(Join.as_element(stem or []))
        self.children.append(_choices_cls(choices or []))
        self.children.append(feedback or Join([]))
        self.children.append(comment or Join([]))
        self.id = id(self)

    # Properties ---------------------------------------------------------------
    @property
    def stem(self):
        return self.children[0]

    @stem.setter
    def stem(self, value):
        self.children[0] = value

    @property
    def choices(self):
        return self.children[1]

    @choices.setter
    def choices(self, value):
        self.children[1] = value

    @property
    def feedback(self):
        return self.children[2]

    @feedback.setter
    def feedback(self, value):
        self.children[2] = value

    @property
    def comment(self):
        return self.children[3]

    @comment.setter
    def comment(self, value):
        self.children[3] = value


    # Invokation ---------------------------------------------------------------
    @classmethod
    def invoke_body(cls, job, tokens, new):
        data = super(multiplechoice, cls).invoke_body(job, tokens, new)
        data = Join(data)

        # Get comments and feedback
        new.feedback = Join.as_element([ x.unlinked() for x in data if isinstance(x, feedback) ])
        new.comment = Join.as_element([ x.unlinked() for x in data if isinstance(x, comment) ])

        # Discard all data after choices
        try:
            choices_ = data.get(choices)
            [ x.unlink() for x in choices_.get_siblings_next() ]
        except ValueError:
            choices_ = choices()

        # Reorganize elements
        new.choices = choices_.unlinked()
        new.stem = Join.as_element(strip(data.clear()))
        new.id = id(new)

        return []

    # Final rendering ----------------------------------------------------------
    def revalue_template(self, idx, **kwds):
        for i, child in enumerate(self.children):
            new = child.revalue('template', idx, **kwds)
            if new is not child:
                self.children[i] = new

        stem, choices, feedback, comment = self.clear()
        opts = dict(self.options or {})
        final = Join()
        final.add(stem)
        final.add(TeXString('\n%\n\\par\\smallskip\n%\n'))

        # See if choices needs to be populated from vars
        if opts.get('varchoices') is not None:
            varchoices = opts['varchoices']
            varchoices = '0' if varchoices is True else varchoices
            if varchoices.isdigit():
                varchoices = 'choices' + varchoices

            # Get choices object
            choices = var.get_variable(self, varchoices)

            # Apply options in choices object
            if opts.get('shuffle'):
                del opts['shuffle']
                choices.shuffle()

            if opts.get('sort'):
                del opts['sort']
                choices.sort()

            choices = choices.texfy()

        # Shuffle choices, if required
        if opts.get('shuffle', False):
            data = choices.clear()
            seed = self.id + idx
            random.seed(seed)
            random.shuffle(data)
            choices.add(data)

        # Format choices depending on the arguments
        if opts.get('horizontal', False):
            final.add(choices.render_horizontal(idx=idx))
        elif opts.get('rows', None) is not None:
            final.add(choices.render_table(rows=int(opts['rows']), idx=idx))
        elif opts.get('cols', None) is not None:
            final.add(choices.render_table(cols=int(opts['cols']), idx=idx))
        elif opts.get('vertical', True):
            choices = final.add(choices.render_vertical(idx=idx))

        # Adds an extra spacing after choices
        final.add(TeXString('\n%\n\\endgraf\\smallskip{}\n%\n'))

        # Print feedback, comments, etc, depending on the section
        return Group('\\begingroup\n', final.clear(), '\n\\endgroup')

#===============================================================================
# LaTeX Environments for defining code or variables
#===============================================================================
class exec_(latex.Verbatim):
    r'''Executes some code and paste the output into the document.
    
    Example
    -------
    
    >>> tex = \
    ... r"""\begin{exec}{python}
    ... print('Hello world!')
    ... \end{exec}"""
    >>> doc = AltSource(tex)
    >>> doc.get_source(0)
    'Hello world!'
    '''

    env_name = 'exec'
    argspec = '[mode:str]{language:str}'

    def revalue_template(self, idx):
        runner = get_runner(self.language, self.verbdata, self)
        data = runner.run()

        # Choose the rendering method depending on the mode
        if data:
            mode = self.mode or 'escape'
            if mode == 'escape':
                return TeXString(escape_tex(data))
            elif mode == 'verbatim':
                verbatim = self.context.get_environment('verbatim')
                return verbatim(data)
            elif mode == 'raw':
                return TeX(data)
            else:
                warnings.warn('unsupported mode: %s, using escape' % mode)
                return TeXString(escape_tex(data))

class namespace(latex.Verbatim):
    r'''Uses code to set up the values of variables that are accessible by the 
    \var command
    
    Example
    -------
    >>> tex = r"""\begin{namespace}{python}
    ... ns.x = 1
    ... ns.y = 2
    ... \end{namespace}
    ... x = \var{x}, y = \var{y}"""
    >>> AltSource(tex).get_source(0)
    '\nx = 1, y = 2'
    '''

    argspec = '{language:str}'
    is_executable = True

    def revalue_template(self, idx):
        runner = get_runner(self.language, self.verbdata, self)
        runner.run()
        return Namespace(runner.get_namespace())

class namespaceinclude(Command):
    '''Uses an external script to set up the values of variables in the current
    level of the namespace'''

    argspec = '{language:str}{file:str}'


class Namespace(TeXElement, collections.UserDict):
    '''TeXElement that stores information on namespace variables'''

    def __init__(self, D):
        self.data = {}
        self.data.update(D)

    def asdict(self):
        return self.data.copy()

    def source(self):
        return ''

    def __str__(self):
        return 'Namespace(%s)' % self.asdict()

#===============================================================================
# Retrieving variables
#===============================================================================
class py(latex.Verb):
    '''Evaluates some python code in the gpython context'''

    language = 'gpython'
    is_executable = True

    def revalue_template(self, idx):
        runner = get_runner('gpython', self.data[1:-1], self)
        return TeXfy(runner.eval())

    def _render_empty(self):
        '''Return itself as an empty command'''
        # Return variable with an interrogation mark in order to signal that
        # some error occurred.
        new_data = self.data[:-1] + '?' + self.data[0]
        return py(new_data)

class var(Command):
    '''Retrieve the value of a variable (or some expression involving variables),
    process it with filters and return the output to the document'''

    argspec = '[filters:list(str)]{expr:str}'

    @classmethod
    def get_variable(cls, obj, varname):
        return cls.get_variables(obj, [varname])[varname]

    @classmethod
    def get_variables(cls, obj, variables):
        '''Return a dictionary associating all variables with its respective
        values retrieved from parent namespace objects'''

        unbound = set(variables)
        bounded = {}

        # Retrieve the variables from the namespace objects in the document
        # hieararchy
        while obj.parent and unbound:
            for x in obj.parent.children:
                if isinstance(x, Namespace):
                    common = set(x).intersection(unbound)
                    for varname in common:
                        bounded[varname] = x[varname]
                        unbound.remove(varname)
            obj = obj.parent

        # Attribute all unbound variables to None
        for var in unbound:
            bounded[var] = None

        return bounded

    def revalue_template(self, idx):
        # Compile var expression and obtain the necessary variables
        # (only simple expressions supported, for now)
        unbound = { self.expr }
        bounded = self.get_variables(self, unbound)

        # Compute the expression
        # (only simple expressions are supported, for now)
        if len(bounded) != 1:
            raise ValueError('complex expressions not supported: %s' % self.data)

        # Obtain the final value for the expression and apply filters
        value = bounded[self.expr]
        value = filters.apply(self.filters or [], value)
        return TeXfy(value).copy()

#===============================================================================
# Create the alttex package and make it discoverable
#===============================================================================
# Remove old imports from __all__
__all__ = list(set(dir()) - set(__all__ + ['__all__']))
from .. import Package, register_package
PACKAGE = Package.from_module('pytex.alttex.latex_lib', 'alttex')
register_package('alttex', PACKAGE)

# Fix local latex converters in the Choice and Choices classes
from .auxtypes import Choice, Choices
Choice.tex_correct = correct
Choice.tex_feedback = feedback
Choice.tex_score = score
Choices.tex_choices = choices

if __name__ == '__main__':
    from .altsource import AltSource  # @UnusedImport (for doctests)
    import doctest
    # doctest.testmod()

    os.chdir('/home/chips/aulas/calculo3/2014_2/')
    tex = r'''\documentclass{article}
    \usepackage{alttex}
    \begin{document}
    \libinclude{integrais-linha/green}
    \end{document}'''
    # tex = r'\libinclude{integrais-linha/green}'
    alts = AltSource(tex)
    # mc = alts._master.document.children[-1].children[-1]
    # print(type(mc) is multiplechoice)
    print(alts.get_source(0, 'answers'))
    # print()



