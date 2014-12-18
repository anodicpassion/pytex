import ply.lex as lex  # @UnresolvedImport @UnusedImport

tokens = ['NAME', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EXCLAMATION',
          'LPAREN', 'RPAREN', 'COMMA', 'FLUSH']

t_ignore = ' \t'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_NAME = r'[a-zA-Z]+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_EXCLAMATION = r'\!'
t_FLUSH = r'\:\:'

def t_NUMBER(tok):
    r'\d+'
    tok.value = int(tok.value)
    return tok

lex.lex()
