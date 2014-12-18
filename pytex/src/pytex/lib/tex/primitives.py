'''Few randomly selected tests

>>> from pytex.parser import TeXProcessor 
>>> tex = r"Hi \endinput bye!"
>>> TeXProcessor(tex).parse()
[<Text element "Hi ">, <endinput macro "\endinput">]
'''
from pytex.elements import Command
from pytex.packages_lib.util import create_commands

#===============================================================================
# Base classes
#===============================================================================
class BoxCommand(Command):
    """ Base class for box-type commands """
    # TODO: implement properly
    argstr = 'self'
    mathMode = False

    def parse(self, tex):
        MathShift.inEnv.append(None)
        Command.init(self, tex)
        MathShift.inEnv.pop()
        return self.attributes

#===============================================================================
# Other commands
#===============================================================================
class let(Command):
    argstr = 'name:Tok = value:Tok'
    def init(self, tokens):
        super(let, self).init(tokens)
        name_tok = self.args['name'].token
        value_tok = self.args['value'].token
        self.processor.add_let(name_tok, value_tok)

#===============================================================================
# OLD IMPLEMENTATIONS
# TODO: revise or reimplement these
#===============================================================================

class MathShift(Command):
    """ 
    The '$' character in TeX

    This macro detects whether this is a '$' or '$$' grouping.  If 
    it is the former, a 'math' environment is invoked.  If it is 
    the latter, a 'displaymath' environment is invoked.

    """
    macroName = 'active::$'
    inEnv = []

    def invoke(self, tex):
        """
        This gets a bit tricky because we need to keep track of both 
        our beginning and ending.  We also have to take into 
        account \mbox{}es.

        """
        inEnv = type(self).inEnv
        math = self.ownerDocument.createElement('math')
        displaymath = self.ownerDocument.createElement('displaymath')

        # See if this is the end of the environment
        if inEnv and inEnv[-1] is not None:
            env = inEnv.pop()
            if type(env) is type(displaymath):
                for t in tex.itertokens():
                    break
                displaymath.macroMode = Command.MODE_END
                self.ownerDocument.context.pop(displaymath)
                return [displaymath]
            else:
                math.macroMode = Command.MODE_END
                self.ownerDocument.context.pop(math)
                return [math]

        for t in tex.itertokens():
            if t.catcode == CC_MATHSHIFT:
                inEnv.append(displaymath)
            else:
                inEnv.append(math)
                tex.pushToken(t)
            break

        current = inEnv[-1]
        self.ownerDocument.context.push(current)

        return [current]

class AlignmentChar(Command):
    """ The '&' character in TeX """
    macroName = 'active::&'

class SuperScript(Command):
    """ The '^' character in TeX """
    macroName = 'active::^'
    argstr = 'self'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not self.ownerDocument.context.isMathMode:
            return tex.textTokens('^')
        Command.read_args(self, tex)

class SubScript(Command):
    """ The '_' character in TeX """
    macroName = 'active::_'
    argstr = 'self'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not self.ownerDocument.context.isMathMode:
            return tex.textTokens('_')
        Command.read_args(self, tex)

class DefCommand(Command):
    """ TeX's \\def command """
    local = True
    argstr = 'name:Tok args:Args definition:nox'
    def invoke(self, tex):
        self.read_args(tex)
        a = self.attributes
        deflog.debug('def %s %s %s', a['name'], a['args'], a['definition'])
        self.ownerDocument.context.newdef(a['name'], a['args'], a['definition'], local=self.local)

class def_(DefCommand):
    macroName = 'def'

class edef(DefCommand):
    local = True

class xdef(DefCommand):
    local = False

class gdef(DefCommand):
    local = False

class IfCommand(Command):
    pass

class if_(IfCommand):
    """ \\if """
    argstr = 'a:Tok b:Tok'
    macroName = 'if'
    """ Test if character codes agree """
    def invoke(self, tex):
        self.read_args(tex)
        a = self.attributes
        return tex.readIfContent(a['a'] == a['b'])

class ifnum(IfCommand):
    """ Compare two integers """
    argstr = 'a:Number rel:Tok b:Number'
    def invoke(self, tex):
        self.read_args(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.readIfContent(a < b)
        elif relation == '>':
            return tex.readIfContent(a > b)
        elif relation == '=':
            return tex.readIfContent(a == b)
        raise ValueError('"%s" is not a valid relation' % relation)

class ifdim(IfCommand):
    """ Compare two dimensions """
    argstr = 'a:Dimen rel:Tok b:Dimen'
    def invoke(self, tex):
        self.read_args(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.readIfContent(a < b)
        elif relation == '>':
            return tex.readIfContent(a > b)
        elif relation == '=':
            return tex.readIfContent(a == b)
        raise ValueError('"%s" is not a valid relation' % relation)

class ifodd(IfCommand):
    """ Test for odd integer """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(not(not(self.attributes['value'] % 2)))

class ifeven(IfCommand):
    """ Test for even integer """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(not(self.attributes['value'] % 2))

class ifvmode(IfCommand):
    """ Test for vertical mode """
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(False)

class ifhmode(IfCommand):
    """ Test for horizontal mode """
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(True)

class ifmmode(IfCommand):
    """ Test for math mode """
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(self.ownerDocument.context.isMathMode)

class ifinner(IfCommand):
    """ Test for internal mode """
    def invoke(self, tex):
        return tex.readIfContent(False)

class ifcat(IfCommand):
    """ Test if category codes agree """
    argstr = 'a:Tok b:Tok'
    def invoke(self, tex):
        self.read_args(tex)
        a = self.attributes
        return tex.readIfContent(a['a'].catcode == a['b'].catcode)

class ifx(IfCommand):
    """ Test if tokens agree """
    argstr = 'a:XTok b:XTok'
    def invoke(self, tex):
        self.read_args(tex)
        a = self.attributes
        return tex.readIfContent(a['a'] == a['b'])

class ifvoid(IfCommand):
    """ Test a box register """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(False)

class ifhbox(IfCommand):
    """ Test a box register """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(False)

class ifvbox(IfCommand):
    """ Test a box register """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(False)

class ifeof(IfCommand):
    """ Test for end of file """
    argstr = 'value:Number'
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(False)

class iftrue(IfCommand):
    """ Always true """
    def invoke(self, tex):
        self.read_args(tex)
        return tex.readIfContent(True)

class ifpytex(iftrue): pass
class pytexfalse(Command): pass
class pytextrue(Command): pass

class iffalse(IfCommand):
    """ Always false """
    def invoke(self, tex):
        return tex.readIfContent(False)

class ifcase(IfCommand):
    """ Cases """
    argstr = 'value:Number'
    def invoke(self, tex):
        return tex.readIfContent(self.read_args(tex)['value'])


class char(Command):
    """ \\char """
    argstr = 'char:Number'
    def invoke(self, tex):
        return tex.textTokens(chr(self.read_args(tex)['char']))

class chardef(Command):
    argstr = 'command:cs = num:Number'
    def invoke(self, tex):
        a = self.read_args(tex)
        self.ownerDocument.context.chardef(a['command'], a['num'])

class NameDef(Command):
    macroName = '@namedef'
    argstr = 'name:str value:nox'

class makeatletter(Command):
    pass
    # def invoke(self, tex):
    #    self.ownerDocument.context.catcode('@', CC_LETTER)

class everypar(Command):
    argstr = 'tokens:nox'

class catcode(Command):
    """ \\catcode """
    argstr = 'char:Number = code:Number'
    def invoke(self, tex):
        a = self.read_args(tex)
        self.ownerDocument.context.catcode(chr(a['char']), a['code'])
    def source(self):
        return '\\catcode`\%s=%s' % (chr(self.attributes['char']),
                                     self.attributes['code'])
    source = property(source)

class csname(Command):
    """ \\csname """
    def invoke(self, tex):
        name = []
        for t in tex:
            if t.nodeType == Command.ELEMENT_NODE and t.nodeName == 'endcsname':
                break
            name.append(t)
        return [EscapeSequence(''.join(name))]

class endcsname(Command):
    r""" \endcsname ==> do something """
    pass

class input(Command):
    """ \\input """
    argstr = 'name:str'
    def invoke(self, tex):
        a = self.read_args(tex)
        try:
            path = tex.kpsewhich(a['name'])

            status.info(' ( %s ' % path)
            encoding = self.config['files']['input-encoding']
            tex.input(codecs.open(path, 'r', encoding, 'replace'))
            status.info(' ) ')

        except (OSError, IOError) as msg:
            log.warning(msg)
            status.info(' ) ')

class include(input):
    """\\include """

class showthe(Command):
    argstr = 'arg:cs'
    def invoke(self, tex):
        log.info(self.ownerDocument.createElement(self.read_args(tex)['arg']).the())


# class active(CountCommand):
#    value = CountCommand.new(13)

class advance(Command):
    def invoke(self, tex):
        tex.readArgument(type='Number')
        tex.readKeyword(['by'])
        tex.readArgument(type='Number')

class expandafter(Command):
    def invoke(self, tex):
        nexttok = None
        for tok in tex.itertokens():
            nextok = tok
            break
        for tok in tex:
            aftertok = tok
            break
        tex.pushToken(aftertok)
        tex.pushToken(nexttok)
        return []

class openout(Command):
    argstr = 'arg:cs = value:any'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.newwrite(a['arg'].nodeName,
#                                           a['value'].textContent)
        return result

class closeout(Command):
    argstr = 'arg:cs'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.writes[a['arg'].nodeName].close()
        return result

class write(Command):
    argstr = 'arg:cs text:nox'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.writes[a['arg'].nodeName].write(self.attributes['text']+'\n')
        return result

class protected_write(write):
    nodeName = 'protected@write'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
