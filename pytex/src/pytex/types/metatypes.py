'''
This module contains all metatypes used by TeXElements subclasses.
'''

if __name__ == '__main__':
    import pytex; __package__ = 'pytex.types'  # @UnusedImport @ReservedAssignment

from .argspec import Argspec

#===============================================================================
# Macro and Environment metatypes
#===============================================================================
class BaseMeta(type):
    '''Common implementation of the MacroMeta and EnvironmentMeta metatypes'''

    def __new__(cls, name, bases, ns):
        cls.get_submacros(ns)
        cls.get_subenvs(ns)
        new = type.__new__(cls, name, bases, ns)
        cls.make_name(new, cls.varname, name)
        cls.make_abstract(new)
        cls.make_argspec(new)
        cls.make_argprops(new)
        cls.make_final(new)
        return new

    @staticmethod
    def get_submacros(ns):
        '''Scan the namespace for all sub-macros'''

        sub = ns.pop('sub_macros', [])
        for v in ns.values():
            if getattr(v, 'macro_name', None) is not None:
                sub.append(v)
        ns['sub_macros'] = sub

    @staticmethod
    def get_subenvs(ns):
        '''Scan the namespace for all sub-macros'''

        sub = ns.pop('sub_environments', [])
        for v in ns.values():
            if getattr(v, 'env_name', None) is not None:
                sub.append(v)
        ns['sub_environments'] = sub

    @staticmethod
    def make_name(new, varname, name):
        '''Save the name into the given variable varname, if not set'''

        if varname not in new.__dict__:
            setattr(new, varname, name)

    @staticmethod
    def make_abstract(new):
        '''Sets the 'is_abstract' property to False, if it was not explicitly
        set'''

        if 'is_abstract' not in new.__dict__:
            setattr(new, 'is_abstract', False)

    @classmethod
    def make_argspec(cls, new):
        '''Format the argspec and convert it into an Argspec object.'''

        if 'argspec' in new.__dict__:
            new.argspec = Argspec(new.argspec, new)

        else:
            # Tries to read argspec from docstring
            macro_name = '\\' + getattr(new, cls.varname)
            doc = new.__doc__ or ''

            # Look for lines which start with whitespace and \macroname{args}
            for L in doc.splitlines():
                if macro_name in L:
                    pre, __, spec = L.partition(macro_name)
                    if pre.strip():
                        continue
                    spec = spec.partition(' ==>')[0].strip()
                    new.argspec = Argspec(spec, new)
                    break
            else:
                new.argspec = Argspec(new.argspec, new)

    @classmethod
    def make_argprops(cls, new):
        '''Create properties based on arguments on class's argspec'''

        for spec in new.argspec.values():
            attr = spec.name
            prop = cls.get_property_from_spec(spec)

            if (hasattr(new, attr) and
                not isinstance(getattr(new, attr), property)):
                attr = attr + '_'
            setattr(new, attr, prop)

    @classmethod
    def get_property_from_spec(cls, spec):
        '''Creates a new property for accessing the attribute described by spec'''

        key = spec.name

        def getter(self): return self.args[key]

        def setter(self, value):
            try:
                self.args[key] = value
            except TypeError:
                from ..util.texfy import TeXfySimple
                self.args[key] = TeXfySimple(value)

        getter.__name__ = key

        return property(getter, setter)

    @classmethod
    def make_final(cls, new):
        '''Must be overriden in subclasses to make additional changes to the
        output type'''
        return

class MacroMeta(BaseMeta):
    '''Metatype for Macro subclassess'''

    varname = 'macro_name'

    @staticmethod
    def make_name(new, varname, name):
        BaseMeta.make_name(new, varname, name)
        new.command_name = '\\' + new.macro_name

class EnvironmentMeta(BaseMeta):
    '''Metaclass for environment classes'''

    varname = 'env_name'

    @classmethod
    def make_final(cls, new):
        name = new.env_name or 'environment'
        argspec = new.argspec
        begin = cls.begin_macro.new_macro(name, argspec, base='self')
        end = cls.end_macro.new_macro('end' + name, base='self')
        begin.environment = new
        end.environment = new
        new.begin_macro = begin
        new.end_macro = end

        if (not new.is_abstract) and 'support_macros' not in new.__dict__:
            new.support_macros = [begin, end]

    @classmethod
    def register_macros(cls, begin, end):
        '''Register the Begin/End macros that will be used as base classes
        in the construction of new Environment types'''

        cls.begin_macro = begin
        cls.end_macro = end
