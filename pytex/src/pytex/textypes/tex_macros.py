if __name__ == '__main__':
    import pytex; __package__ = 'pytex.textypes'  # @UnusedImport @ReservedAssignment

from . import Command, TeXString, tk

#===============================================================================
# Verbatim
#===============================================================================
class Verb(Command):
    '''Base class for all verbatim \verb-like commands.'''

    argspec = '{data:str}'
    def __init__(self, data):
        super(Verb, self).__init__()
        if data[0] != data [-1]:
            raise ValueError('beginding and ending character must match')
        self.data = data

    @classmethod
    def invoke(cls, job, tokens):
        verb = tokens.get_macro(cls.macro_name)
        tok = next(tokens)

        # Check if it needs to call the * version of the \verb command
        # (i.e.: \verb*)
        if tok == '*' and not verb.endswith('*'):
            tokens.push(tk.TkEscape(verb + tok))
            return None

        # Create the \verb object and its data argument
        data = [tok]
        data.extend(tokens.stopping_after(tok))
        data = TeXString(''.join(data))
        new = Command.__new__(cls)  # @UndefinedVariable
        new.args = cls.argspec.new_arguments(data=data)
        new.args.owner = new

        return new

    def source(self):
        '''Prevents showing {}'s at the argument'''
        return self.command_name + self.data

    def __repr__(self):
        return '<%s macro>' % self.source()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
