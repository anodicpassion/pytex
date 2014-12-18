'''
Test is TeX parser is obtaining the correct template from TeX snippets
'''
if __name__ == '__main__':
    import pytex_tests; __package__ = 'pytex_tests'  # @UnusedImport @ReservedAssignment

import copy
from . import load_tex
from pytex import TeXJob, TeXContainer, Command, TeXPreamble, TeXBody, Environment, Text, Group, Macro, Math, DisplayMath

class ExampleTester:
    '''Test if a given LaTeX source matches a given type/class structure'''

    INDEX = 0

    def __init__(self, descr, tex, template, precise=True):
        self.descr = descr
        self.tex = tex
        self.template = template
        self.precise = precise
        try:
            self.result = TeXJob(self.tex).parse()
        except Exception as ex:
            self.result = None
            self.ex = ex

    def run_struct(self):
        if self.result is None:
            raise self.ex

        assert self.isinstance(self.result, self.template), self.error_msg()

    def run_copy(self):
        if self.result is None:
            raise self.ex

        assert self.result == copy.deepcopy(self.result)

    def run_render(self):
        if not self.precise:
            return

        if self.result is None:
            raise self.ex

        orig = self.tex
        result = self.result.source()

        # Trailing whitespace doesn't count
        orig_L = [ line.rstrip() for line in orig.splitlines() ]
        result_L = [ line.rstrip() for line in result.splitlines() ]
        if orig_L != result_L:
            orig = orig if '\n' not in orig else '\n' + orig
            result = result if '\n' not in result else '\n' + result
            assert False, 'bad source formatting\noriginal: %s\n\nresult: %s' % (orig, result)

    def isinstance(self, str1, str2):
        '''Test if a given template str1 is a special case of the template str2'''

        if len(str1) != len(str2):
            return False
        for x, y in zip(str1, str2):
            if isinstance(y, list):
                if not isinstance(x, y[0]):
                    return False
                if not self.isinstance(x.children, y[1:]):
                    return False
            elif not isinstance(x, y):
                return False
        return True

    def error_msg(self):
        '''Return an error message for non-matching structures'''

        result_strut = self._get_result_structure(self.result, self.template)
        result_strut = self.fmt_structure(result_strut)
        template = self.fmt_structure(self.template)
        source = self.tex
        if '\n' in self.tex:
            source = 'document:\n\n%s\n' % source
        else:
            source = '"%s", ' % source
        return 'bad template for %sgot: %s, expected: %s' % \
                (source, result_strut, template)

    def _get_result_structure(self, st, template):
        L = []
        for (x, y) in zip(st, template):
            if isinstance(y, list) and isinstance(x, TeXContainer):
                tt = self._get_result_structure(x.children, y[1:])
                tt = [type(x)] + tt
            else:
                tt = type(x)
            L.append(tt)

        if len(st) > len(template):
            for i in range(len(template), len(st)):
                L.append(type(st[i]))

        return L

    def fmt_structure(self, structure):
        '''Format structure as a human-friendly string representation'''

        L = []
        for obj in structure:
            if isinstance(obj, list):
                L.append(self.fmt_structure(obj))
            else:
                L.append(obj.__name__)
        return '[%s]' % (', '.join(L))

    @classmethod
    def export_examples(cls, *args):
        '''Export a number of StrutureTest-based functions to the global 
        namespace. These functions are recognized by nose as unit tests'''

        global_ns = globals()
        examples = []

        for arg in args:
            tester = ExampleTester(*arg)

            name = 'test_strut_%i' % cls.INDEX
            global_ns[name] = cls._make_struct_func(name, tester)
            examples.append(global_ns[name])

            name = 'test_copy_%i' % cls.INDEX
            global_ns[name] = cls._make_copy_func(name, tester)
            examples.append(global_ns[name])

            name = 'test_render_%i' % cls.INDEX
            global_ns[name] = cls._make_render_func(name, tester)
            examples.append(global_ns[name])

            cls.INDEX += 1
        return examples

    @classmethod
    def _make_struct_func(cls, name, runner):
        '''Auxiliary method for export_examples()'''

        def func(): runner.run_struct()
        func.__name__ = name
        func.__doc__ = '%s\n\n%s' % (runner.descr, runner.tex)
        return func

    @classmethod
    def _make_copy_func(cls, name, runner):
        '''Auxiliary method for export_examples()'''

        def func(): runner.run_copy()
        func.__name__ = name
        func.__doc__ = '%s\n\n%s' % (runner.descr, runner.tex)
        return func

    @classmethod
    def _make_render_func(cls, name, runner):
        '''Auxiliary method for export_examples()'''

        def func(): runner.run_render()
        func.__name__ = name
        func.__doc__ = '%s\n\n%s' % (runner.descr, runner.tex)
        return func


def local_tester(tex, title=None, show_source=True):
    '''Parse LaTeX and print the result. Used only if __name__ == '__main__' '''

    print('-' * 80)
    if title:
        print(title)
    if show_source:
        print(tex)
    doc = TeXJob(tex).parse()
    source = doc.source()
    if show_source:
        if '\n' in tex and not (tex.endswith('\n') or source.startswith('\n')):
            print()
        print(source)
    if '\n' in tex:
        print()
    print(doc)

#===============================================================================
# EXAMPLES
#===============================================================================

# TeX Commands
ta1_macro = r'\TeX', [Command]
ta2_unkown_macro = r'\foo', [Macro]
ta3_macro_with_args = r'\textbf{1234}', [Command]
ta4_macro_with_opt_args = r'\documentclass[a4]{article}', [Command]
ta5_escape_command = r'\\', [Macro]
ta6_macro_with_ommited_opt_args = r'\documentclass{article}', [Command]
ta7_nested_macro = r'\textbf{foo \textrm{bar}}', [Command]
ta8_verb = r'\verb$foo$', [Command]
ta9_verb2 = r'\verb*$foo$', [Command]
ta10_usepackage = r'\usepackage{alttex}', [Command]
ta11_unknown_args = r'\foo{bar}', [Command, Group]


# Environments
tb0_group = r'{foo}', [[Group, Text]]
tb1_simple_envinronment = ('\\begin{center}\nSome document with text\n\\end{center}',
                           [Environment])
tb2_unknown_environment = ('\\begin{foo}\nbar\n\\end{foo}', [Environment], True)
tb3_verbatim = ('\\begin{verbatim}\n\n\n\\endinput bye!\n\\end{verbatim}',
                [Environment])

# Math
tc1_some_math = r"$1 + 1 = 2$", [Math]
tc2_display_math = r"$$1 + 1 = 2$$", [DisplayMath]

# Documents
td1_simple_document = (r'\documentclass{article}\begin{document}Foo\end{document}',
                       [TeXPreamble, TeXBody],
                       False)

# External examples
te1_basic_external = (load_tex('basic'),
                      [TeXPreamble, [TeXBody, Text, Command, Text]],
                      False)
te2_basic_lyx = (load_tex('basic-lyx'),
                 [TeXPreamble, [TeXBody, Text, Macro, Group, Text]],
                 False)

for name, obj in sorted(list(globals().items())):
    if isinstance(obj, tuple) and (len(obj) == 2 or len(obj) == 3) and name.startswith('t'):
        name = name.replace('_', ' ').upper()
        tcode, _, name = name[1:].partition(' ')
        name = 'TEST %s - %s' % (tcode, name)
        show_source = len(obj) == 2
        if __name__ == '__main__':
            local_tester(obj[0], name, show_source)
        for func in ExampleTester.export_examples(tuple((name,) + obj)):
            func()
