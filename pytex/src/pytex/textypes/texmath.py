if __name__ == '__main__':
    import pytex.textypes; __package__ = 'pytex.textypes'  # @ReservedAssignment @UnusedImport

from .containers import TeXContainer

__all__ = ['Math', 'DisplayMath']

class MathBase(TeXContainer):
    '''Base class for all math objects. Subclasses must override the default
    ``bmath`` and ``emath`` tokens.'''

    def __init__(self, *args, **kwds):
        bmath = kwds.get('bmath', '')
        emath = kwds.get('emath', '')
        children = kwds.get('children', [])
        bmath, emath = kwds.get('mathshift', (bmath, emath))

        if len(args) == 3:
            bmath, children, emath = args
        elif len(args) == 1:
            children = args[0]
        elif len(args) != 0:
            raise TypeError('Group can be initialized with 0, 1 or 3 positional _data, got %s' % len(args))

        super(MathBase, self).__init__(children=children)
        self.bmath = bmath or type(self).bmath
        self.emath = emath or type(self).emath

    def __repr__(self):
        source = self.children_source()
        source = source if len(source) < 10 else '...'
        return "'%s%s%s'" % (self.bmath, source, self.emath)

    def source(self):
        return (self.bmath + self.children_source() + self.emath)

class Math(MathBase):
    '''Inline math objects'''
    bmath = '$'
    emath = '$'

class DisplayMath(MathBase):
    '''Display math objects'''
    bmath = '$$'
    emath = '$$'

if __name__ == '__main__':
    import doctest
    doctest.testmod()