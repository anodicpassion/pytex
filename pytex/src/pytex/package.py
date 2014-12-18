if __name__ == '__main__':
    import pytex; __package__ = 'pytex'  # @ReservedAssignment @UnusedImport

import re
from importlib import import_module
from collections import MutableMapping
from .errors import PackageImportError
from .textypes.macro import Macro, Command
from .textypes.environment import Environment

__all__ = ['register_package', 'register_path', 'load_packages', 'load_package', 'Package', 'LATEX', 'TEX']

PACKAGES = {}
LIB_PATHS = ['pytex.lib.packages']
LATEX_PACKAGES = ['@LaTeX', '@TeX']

def register_package(name, package):
    '''Register the given module in the packages dictionary'''

    if isinstance(package, Package):
        PACKAGES[name] = package
    else:
        PACKAGES[name] = Package.from_module(package)

def register_path(path):
    '''Register a python module path to search for packages'''

    LIB_PATHS.append(path)

def load_packages(names, load_latex=False):
    '''Return a list of packages from the given package names'''

    if load_latex:
        names = LATEX_PACKAGES + list(names)
    return [ load_package(name) for name in names ]

def load_package(name):
    '''Return a package from its name'''

    try:
        return PACKAGES[name]
    except KeyError:
        for path in reversed(LIB_PATHS):
            try:
                package = Package.from_module(path + '.' + name, name=name)
                break
            except PackageImportError:
                pass
        else:
            raise ValueError('no package named %s on import paths: %s' % (name, LIB_PATHS))

    PACKAGES[name] = package
    return package

class Package(MutableMapping):
    '''Class that represents a package. 
    
    A Package is essentially a dictionary mapping names to macros'''

    def __init__(self, name, **kwds):
        self.name = name
        self._data = {}
        self._data.update(kwds)

    @classmethod
    def from_module(cls, module, name=None):
        '''Creates a Package object from a module'''

        if isinstance(module, str):
            module = import_module(module)
        name = name or module.__name__.split('.')[-1]
        data = {}
        for (k, v) in vars(module).items():
            if isinstance(v, type):
                if getattr(v, 'is_abstract', True):
                    continue
                elif issubclass(v, Macro):
                    data[k] = v
                elif issubclass(v, Environment):
                    for macro in v.support_macros:
                        data[macro.macro_name] = macro

        package = getattr(module, 'PACKAGE', Package(name))
        package.update(data)
        return package

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __repr__(self):
        return 'Package(%r)' % self.name

    NAME_REGEX = re.compile(r'^\\[a-zA-Z@]+')
    def add_commands(self, tex, base=Command):
        '''Automatically create commands from a template'''

        # Recursivelly call this function for multi-line templates
        lines = tex.splitlines()
        if len(lines) > 1:
            for line in lines:
                line = line.strip()
                if line.startswith('%'):
                    continue
                if line:
                    self.add_commands(line)
            return

        # Process single-line templates
        name = self.NAME_REGEX.findall(tex)
        if len(name) != 1:
            raise ValueError('invalid command template: "%s"' % tex)
        name = name[0][1:]
        spec = tex[len(name) + 1:].strip()

        cls = type(name, (base,), {'argspec': spec})
        self[name] = cls

#===============================================================================
# Instantiate LaTeX and TeX packages
#===============================================================================
LATEX = None
TEX = None