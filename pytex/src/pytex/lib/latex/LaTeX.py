if __name__ == '__main__' and __package__ is None:
    import pytex.lib.latex; __package__ = 'pytex.lib.latex'  # @UnusedImport @ReservedAssignment

from ...textypes.base import TeXString
from ...textypes.macro import Command
from ...textypes.environment import Environment, BeginEnv, EndEnv
from ...textypes.tex_environments import Verbatim, Itemize, Tabular, Item
from ...textypes.tex_macros import Verb
from ...package import Package

#===============================================================================
# Base LaTeX package
#===============================================================================
PACKAGE = Package('@LaTeX')

class DimenCommand(Command):
    is_abstract = True

    @classmethod
    def new(cls, x):
        return

#===============================================================================
# C.1.2 Environments (p167)
#===============================================================================
class begin(BeginEnv):
    pass

class end(EndEnv):
    pass

#===============================================================================
# C.2 The Structure of the Document (p170)
#===============================================================================
class document(Environment):
    pass

#===============================================================================
# C.3.1 Making Sentences (p170)
#===============================================================================

#
# Quotes
#
# '          Apostrophe
# `text'     Single quotes
# ``text''   Double quotes

#
# Dashes
#
# -      Intra-word
# --     Number-range
# ---    Punctuation

# Spacing
class SmallSpace(Command):
    macro_name = ','

class InterWordSpace(Command):
    macro_name = ' '

class NoLineBreak(Command):
    macro_name = 'active::~'

class EndOfSentence(Command):
    macro_name = '@'

class frenchspacing(Command):
    pass

class nonfrenchspacing(Command):
    pass

# Logos
class LaTeX(Command):
    pass

class TeX(Command):
    pass

# Misc
class today(Command):
    pass

class emph(Command):
    args = '{data}'

class em(Environment):
    pass

#===============================================================================
# C.3.4 Accents and Special Symbols (p173)
#===============================================================================
# References: PlasTeX and http://en.wikibooks.org/wiki/LaTeX/Special_Characters

#
# Table 3.1: Accents
#

class Symbol(Command):
    str = None

    def as_letter(self):
        return TeXString(self.str) or self

class Accent(Command):
    args = '{letter}'
    chars = {}

    def as_letter(self):
        return self.chars.get(TeXString(self.letter), self)

class Grave(Accent):
    '''grave accent'''

    macro_name = '`'
    chars = {
        'A': chr(192),
        'E': chr(200),
        'I': chr(204),
        'O': chr(210),
        'U': chr(217),
        'a': chr(224),
        'e': chr(232),
        'i': chr(236),
        'o': chr(242),
        'u': chr(249),
        'N': chr(504),
        'n': chr(505),
    }

class Acute(Accent):
    '''acute accent'''

    macro_name = "'"
    chars = {
        'A': chr(193),
        'E': chr(201),
        'I': chr(205),
        'O': chr(211),
        'U': chr(218),
        'Y': chr(221),
        'a': chr(225),
        'e': chr(233),
        'i': chr(237),
        'o': chr(243),
        'u': chr(250),
        'y': chr(253),
        'C': chr(262),
        'c': chr(263),
        'L': chr(313),
        'l': chr(314),
        'N': chr(323),
        'n': chr(324),
        'R': chr(340),
        'r': chr(341),
        'S': chr(346),
        's': chr(347),
        'Z': chr(377),
        'z': chr(378),
        'G': chr(500),
        'g': chr(501),
    }

class Circumflex(Accent):
    '''circumflex'''

    macro_name = '^'
    chars = {
        'A': chr(194),
        'E': chr(202),
        'I': chr(206),
        'O': chr(212),
        'U': chr(219),
        'a': chr(226),
        'e': chr(234),
        'i': chr(238),
        'o': chr(244),
        'u': chr(251),
        'C': chr(264),
        'c': chr(265),
        'G': chr(284),
        'g': chr(285),
        'H': chr(292),
        'h': chr(293),
        'J': chr(308),
        'j': chr(309),
        'S': chr(348),
        's': chr(349),
        'W': chr(372),
        'w': chr(373),
        'Y': chr(374),
        'y': chr(375),
    }

class Umlaut(Accent):
    '''umlaut, trema or dieresis'''
    macro_name = '"'
    chars = {
        'A': chr(196),
        'E': chr(203),
        'I': chr(207),
        'O': chr(214),
        'U': chr(220),
        'a': chr(228),
        'e': chr(235),
        'i': chr(239),
        'o': chr(246),
        'u': chr(252),
        'y': chr(255),
        'Y': chr(376),
    }

class H(Accent):
    '''long Hungarian umlaut (double acute)'''
    chars = {
        'O': chr(336),
        'o': chr(337),
        'U': chr(368),
        'u': chr(369),
    }

class Tilde(Accent):
    '''tilde'''

    macro_name = '~'
    chars = {
        'A': chr(195),
        'N': chr(209),
        'O': chr(213),
        'a': chr(227),
        'n': chr(241),
        'o': chr(245),
        'I': chr(296),
        'i': chr(297),
        'U': chr(360),
        'u': chr(361),
    }

class c(Accent):
    '''cedilla'''
    chars = {
        'C': chr(199),
        'c': chr(231),
        'G': chr(290),
        'g': chr(123),
        'K': chr(310),
        'k': chr(311),
        'L': chr(315),
        'l': chr(316),
        'N': chr(325),
        'n': chr(326),
        'R': chr(342),
        'r': chr(343),
        'S': chr(350),
        's': chr(351),
        'T': chr(354),
        't': chr(355),
        'E': chr(552),
        'e': chr(553),
    }


class k(Accent):
    '''ogonek'''
    chars = {
        'A': chr(260),
        'a': chr(261),
        'E': chr(280),
        'e': chr(281),
        'I': chr(302),
        'i': chr(303),
        'U': chr(370),
        'u': chr(371),
        'O': chr(490),
        'o': chr(491),
    }

class l(Symbol):
    '''barred l (l with stroke)'''

class Macron(Accent):
    '''macron accent (a bar over the letter)'''

    macro_name = '='
    chars = {
        'A': chr(256),
        'a': chr(257),
        'E': chr(274),
        'e': chr(275),
        'I': chr(298),
        'i': chr(299),
        'O': chr(332),
        'o': chr(333),
        'U': chr(362),
        'u': chr(363),
        'Y': chr(562),
        'y': chr(563),
    }

class b(Accent):
    '''bar under the letter'''

    chars = {
        'B': chr(7686),
        'b': chr(7687),
        'D': chr(7694),
        'd': chr(7695),
        'K': chr(7732),
        'k': chr(7733),
        'L': chr(7738),
        'l': chr(7739),
        'N': chr(7752),
        'n': chr(7753),
        'R': chr(7774),
        'r': chr(7775),
        'T': chr(7790),
        't': chr(7791),
        'Z': chr(7828),
        'z': chr(7829),
        'h': chr(7830),
    }

class Dot(Accent):
    '''dot over the letter'''

    macro_name = '.'
    chars = {
        'C': chr(266),
        'c': chr(267),
        'E': chr(278),
        'e': chr(279),
        'G': chr(288),
        'g': chr(289),
        'I': chr(304),
        'Z': chr(379),
        'z': chr(380),
        'A': chr(550),
        'a': chr(551),
        'O': chr(558),
        'o': chr(559),
        'B': chr(7682),
        'b': chr(7683),
        'D': chr(7690),
        'd': chr(7691),
        'F': chr(7710),
        'f': chr(7711),
        'H': chr(7714),
        'h': chr(7715),
        'M': chr(7744),
        'm': chr(7745),
        'N': chr(7748),
        'n': chr(7749),
        'P': chr(7766),
        'p': chr(7767),
        'R': chr(7768),
        'r': chr(7769),
        'S': chr(7776),
        's': chr(7777),
        'T': chr(7786),
        't': chr(7787),
        'W': chr(7814),
        'w': chr(7815),
        'X': chr(7818),
        'x': chr(7819),
        'Y': chr(7822),
        'y': chr(7823),
    }

class d(Accent):
    '''dot under the letter'''

    chars = {
        'B': chr(7684),
        'b': chr(7684),
        'D': chr(7692),
        'd': chr(7693),
        'H': chr(7716),
        'h': chr(7717),
        'K': chr(7730),
        'k': chr(7731),
        'L': chr(7734),
        'l': chr(7735),
        'M': chr(7746),
        'm': chr(7747),
        'N': chr(7750),
        'n': chr(7751),
        'R': chr(7770),
        'r': chr(7771),
        'S': chr(7778),
        's': chr(7779),
        'T': chr(7788),
        't': chr(7789),
        'V': chr(7806),
        'v': chr(7807),
        'W': chr(7816),
        'w': chr(7817),
        'Z': chr(7826),
        'z': chr(7827),
        'A': chr(7840),
        'a': chr(7841),
        'E': chr(7864),
        'e': chr(7865),
        'I': chr(7882),
        'i': chr(7883),
        'O': chr(7884),
        'o': chr(7885),
        'U': chr(7908),
        'u': chr(7909),
        'Y': chr(7924),
        'y': chr(7925),
    }

class r(Accent):
    '''ring over the letter (for å there is also the special command \aa). 
    
    Invoke convert \r{a} to \aa'''

    # TODO: find unicode symbols for character
    chars = {}

    @classmethod
    def invoke(cls, job, tokens):
        new = super(r, cls).invoke(job, tokens)
        if new.letter == 'a':
            return aa()
        else:
            return new

class u(Accent):
    '''breve over the letter'''

    chars = {
        'A': chr(258),
        'a': chr(259),
        'E': chr(276),
        'e': chr(277),
        'G': chr(286),
        'g': chr(287),
        'I': chr(300),
        'i': chr(301),
        'O': chr(334),
        'o': chr(335),
        'U': chr(364),
        'u': chr(365),
    }

class v(Accent):
    '''caron/háček ("v") over the letter'''

    chars = {
        'C': chr(268),
        'c': chr(269),
        'D': chr(270),
        'd': chr(271),
        'E': chr(282),
        'e': chr(283),
        'L': chr(317),
        'l': chr(318),
        'N': chr(327),
        'n': chr(328),
        'R': chr(344),
        'r': chr(345),
        'S': chr(352),
        's': chr(353),
        'T': chr(356),
        't': chr(357),
        'Z': chr(381),
        'z': chr(382),
        'A': chr(461),
        'a': chr(462),
        'I': chr(463),
        'i': chr(464),
        'O': chr(465),
        'o': chr(466),
        'U': chr(467),
        'u': chr(468),
        'G': chr(486),
        'g': chr(487),
        'K': chr(488),
        'k': chr(489),
        'j': chr(496),
        'H': chr(542),
        'h': chr(543),
    }


class t(Accent):
    '''"tie" (inverted u) over the two letters'''

    chars = {}

class o(Symbol):
    '''slashed o (o with stroke)'''

    chars = {}

class i(Symbol):
    '''dotless i'''

class j(Symbol):
    '''dotless j'''

#
# Table 3.2: Non-English Symbols (see Characters.py)
#


class oe(Symbol): pass
class OE(Symbol): pass
class ae(Symbol): pass
class AE(Symbol): pass
class aa(Symbol): pass
class AA(Symbol): pass

class O(Symbol): pass
class L(Symbol): pass
class ss(Symbol): pass

#
# Special symbols
#

class dag(Symbol):
    str = chr(8224)

class ddag(Symbol):
    str = chr(8225)

class S(Symbol):
    str = chr(167)

class P(Symbol):
    str = chr(182)

class copyright(Symbol):  # @ReservedAssignment
    str = chr(169)

class pounds(Symbol):
    str = chr(163)

class textbar(Symbol):
    str = '|'

class textbackslash(Symbol):
    str = '\\'

class textgreater(Symbol):
    str = '>'

class textless(Symbol):
    str = '<'

class textendash(Symbol):
    str = '_'

class textemdash(Symbol):
    str = '__'

class texttrademark(Symbol):
    pass

class textregistered(Symbol):
    pass

class textexclamdown(Symbol):
    pass

class textquestiondown(Symbol):
    pass

class textcircled(Accent):
    pass

class textsuperscript(Accent):
    pass

#
# Escape characters
#
class EscapeChar(Symbol):
    @property
    def str(self):
        return self.macro_name

class Percent(Symbol):
    macro_name = '%'

class HashMark(Symbol):
    macro_name = '#'

class Dollar(Symbol):
    macro_name = '$'

class LBrace(Symbol):
    macro_name = '{'

class RBrace(Symbol):
    macro_name = '}'

class Underscore(Symbol):
    macro_name = '_'

class Ampersand(Symbol):
    macro_name = '&'


#===============================================================================
# C.5 Classes, Packages, and Page Styles (p176)
#===============================================================================

PACKAGE.add_commands(r'''
\documentclass[options:str]{package_name:str}
\documentstyle[options:str]{package_name:str}

% C.5.3 Page styles
\pagestyle{style}
\thispagestyle{style}
\markright{text}
\markboth{left}{right}
\pagenumbering{style}
\twocolumn[text]
\onecolumn

% C.5.4 The Title Page and Abstract
\maketitle
\title[toc]{data}
\author{data}
\date{data}
\thanks{data}
''')


class bibindent(DimenCommand):
    value = DimenCommand.new(0)

class columnsep(DimenCommand):
    value = DimenCommand.new(0)

class columnseprule(DimenCommand):
    value = DimenCommand.new(0)

class mathindent(DimenCommand):
    value = DimenCommand.new(0)

class usepackage(Command):
    argspec = '[options:dict]{names:list(str)}'

class RequirePackage(usepackage):
    pass

#
# C.5.3 Page Styles
#


#
# Style Parameters
#


class paperheight(DimenCommand):
    value = DimenCommand.new('11in')

class paperwidth(DimenCommand):
    value = DimenCommand.new('8.5in')

class oddsidemargin(DimenCommand):
    value = DimenCommand.new('1in')

class evensidemargin(DimenCommand):
    value = DimenCommand.new('1in')

class textheight(DimenCommand):
    value = DimenCommand.new('9in')

class textwidth(DimenCommand):
    value = DimenCommand.new('6.5in')

class topmargin(DimenCommand):
    value = DimenCommand.new(0)

class headheight(DimenCommand):
    value = DimenCommand.new('0.5in')

class headsep(DimenCommand):
    value = DimenCommand.new('0.25in')

class footskip(DimenCommand):
    value = DimenCommand.new('0.5in')

class marginparsep(DimenCommand):
    value = DimenCommand.new('0.25in')

class marginparwidth(DimenCommand):
    value = DimenCommand.new('0.75in')

class topskip(DimenCommand):
    value = DimenCommand.new(0)


# C.5.4 The Title Page and Abstract
class abstract(Environment):
    blockType = True

class titlepage(Environment):
    blockType = True


#
# Extras...
#
class ProvidesPackage(Command):
    args = 'name [ message ]'

class ProvidesClass(Command):
    pass

class DeclareOption(Command):
    args = 'name:str [ default:nox ] value:nox'

class PackageWarning(Command):
    args = 'name:str message:str'

class ProcessOptions(Command):
    args = '*'

class LoadClass(usepackage):
    args = '[ options:dict ] names:list:str'
    extension = '.cls'

class NeedsTeXFormat(Command):
    args = 'name:str date:str'

class InputIfFileExists(Command):
    args = 'file:str true:nox false:nox'
    def invoke(self, tex):
        a = self.parse(tex)
        try:
            tex.input(tex.kpsewhich(a['file']))
            tex.pushTokens(a['true'])
        except (IOError, OSError):
            tex.pushTokens(a['false'])
        return []

class IfFileExists(Command):
    args = 'file:str true:nox false:nox'
    def invoke(self, tex):
        a = self.parse(tex)
        try:
            tex.kpsewhich(a['file'])
            tex.pushTokens(a['true'])
        except (IOError, OSError):
            tex.pushTokens(a['false'])
        return []

#===============================================================================
# C.6.2 List-Making Environments
# C.6.3 The list and trivlist Enviroments
#===============================================================================
class item(Item):
    pass

class itemize(Itemize):
    pass

#===============================================================================
# C.6.4 Verbatim
#===============================================================================
class verbatim(Verbatim):
    pass

class verbatim_star(Verbatim):
    env_name = 'verbatim*'

class verb(Verb):
    pass

class verb_star(Verb):
    macro_name = 'verb*'

#===============================================================================
# C.10.2 The array and tabular Environments
#===============================================================================
class array(Tabular):
    pass

class tabular(Tabular):
    pass

# class tabularStar(tabular):
#    macroName = 'tabular*'
#    args = 'width:dimen [ pos:str ] colspec:nox'

# Style Parameters

class arraycolsep(DimenCommand):
    value = DimenCommand.new(0)

class tabcolsep(DimenCommand):
    value = DimenCommand.new(0)

class arrayrulewidth(DimenCommand):
    value = DimenCommand.new(0)

class doublerulesep(DimenCommand):
    value = DimenCommand.new(0)

class arraystretch(Command):
    str = '1'


#===============================================================================
# C.15 Font Selection (p225)
#===============================================================================
class TextFormat(Command):
    is_abstract = True

PACKAGE.add_commands(r'''
\md
\mdseries
\textmd{data}
\bf
\bfseries
\textbf{data}
\rm
\rmfamily
\textrm{data}
\sf
\sffamily
\textsf{data}
\tt
\ttfamily
\texttt{data}
\up
\upshape
\textup{data}
\it
\itshape
\textit{data}
\sl
\slshape
\textsl{data}
\sc
\scshape
\textsc{data}
\normalfont
\textnormal{data}
\tiny
\scriptsize
\footnotesize
\small
\normalsize
\large
\Large
\LARGE
\huge
\Huge
\symbol{number:int}
''', base=TextFormat)


#===============================================================================
# Text Alignment
#===============================================================================
class center(Environment):
    pass

class centering(center):
    pass

class flushleft(Environment):
    pass

class raggedright(flushleft):
    pass

class flushright(Environment):
    pass

class raggedleft(flushright):
    pass

class raggedbottom(Environment):
    pass
