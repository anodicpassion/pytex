if __name__ == '__main__':
    import pytex; __package__ = 'pytex.elements'  # @UnusedImport @ReservedAssignment

import warnings
from contextlib import contextmanager
from .types.nested_dict import NestedDict

class Context:
    '''Defines a TeX processor state. It maps names to macros and environments, 
    it store global variables for the TeX processor, current environment, etc.'''
    PACKAGE = None

    def __init__(self, packages=[], macros={}):
        self._init_class()
        self._macro_table = NestedDict()
        self._packages = [[]]
        self._namespace = {}

        # Load TeX and LaTeX macros
        packages = self.PACKAGE.load_packages(packages, load_latex=True)
        for package in packages:
            self.load_package(package)

    def get_macro(self, macro_name, warn=2):
        '''Return the macro if it exists in the macro table'''

        try:
            return self._macro_table[macro_name]
        except KeyError:
            if warn >= 2:
                raise ValueError('macro not found: %s' % macro_name)
            elif warn == 1:
                warnings.warn('creating macro \\%s' % macro_name)

            new = self._new_macro(macro_name)
            self.save_macro(new)
            return new

    def save_macro(self, macro):
        '''Saves a macro to the macros table'''

        self._macro_table[macro.macro_name] = macro

    def get_environment(self, envname, warn=2):
        '''Return the macro if it exists in the macro table'''

        try:
            return self.get_macro(envname, warn=2).environment
        except ValueError:
            if warn >= 2:
                raise ValueError('environment not found: %s' % envname)
            elif warn == 1:
                warnings.warn('creating a new %s environment' % envname)

            new = self._new_environment(envname)
            self.save_macro(new.begin_macro)
            self.save_macro(new.end_macro)
            return new

    def save_environment(self, env):
        '''Register an environment to the macro table'''

        self.save_macro(env.begin_macro)
        self.save_macro(env.end_macro)

    def load_package(self, package):
        '''Load all macros from the given Package object.'''

        if isinstance(package, str):
            package = self.PACKAGE.load_package(package)
            return self.load_package(package)

        for _, obj in package.items():
            if isinstance(obj, type):
                if issubclass(obj, self._MACRO):
                    self.save_macro(obj)
                elif issubclass(obj, self._ENVIRONMENT):
                    self.save_environment(obj)

        self._packages[-1].append(package.name)

    def set_variable(self, varname, value):
        '''Set the value of a context variable'''

        self._namespace[varname] = value

    def get_variable(self, varname, *args):
        '''Get the value for a variable or the second argument if this variable
        does not exist'''

        if len(args) > 1:
            raise TypeError('get_variable(varname[,default]) can be called with one or two positional arguments')
        try:
            return self._namespace[varname]
        except KeyError:
            if args:
                return args[0]
            else:
                raise ValueError("variable doesn't exist: %s" % varname)

    def begin_group(self):
        '''Begin a new group. Define a nested namespace for the group.'''
        self._macro_table.up()

    def end_group(self):
        '''Ends the namespace defined by begin_group()'''
        self._macro_table.down()

    @contextmanager
    def grouping(self):
        '''Context manager for safely creating new groups'''
        # __enter__()
        self.begin_group()

        # Execute block
        yield

        # __exit__()
        self.end_group()

    @classmethod
    def _init_class(cls):
        if cls.PACKAGE is None:
            from pytex import package
            cls.PACKAGE = package

    def copy(self):
        warnings(NotImplemented)
        return self

if __name__ == '__main__':
    import doctest
    doctest.testmod(report=True, optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
