r'''BNF Grammar

expr    : expr PLUS term
        | expr MINUS term
        | func
        | term
term    : term TIMES factor
        | term DIVIDE factor
        | factor
func    : NAME LPAREN expr RPAREN
        | NAME LPAREN args RPAREN
args    : args COMMA expr
factor  : NUMBER 
        | NAME
        | fat
        | func
fat     : factor EXCLAMATION
        | LPAREN expr RPAREN EXCLAMATION
'''
if __name__ == '__main__':
    import pytex.alttex.var_command; __package__ = 'pytex.alttex.var_command'


from . import lexer
import ply.yacc as yacc
import sympy as sp
tokens = lexer.tokens

KNOWN_NAMES = {
    'pi': sp.pi,
    'e': sp.E,
    'cos': sp.cos,
}

def p_final(p):
    '''final : expr FLUSH filters'''
    p[0] = (p[1], p[3])

def p_final_simple(p):
    '''final : expr'''
    p[0] = (p[1], None)

def p_filters(p):
    '''filters : filters FLUSH func
               | filters FLUSH NAME'''
    p[0] = p[1] + (p[3],)

def p_filters_simple(p):
    '''filters : func
               | NAME'''
    p[0] = (p[1],)

def p_expr_plus(p):
    '''expr : expr PLUS term'''
    if isinstance(p[1], tuple) and p[1][0] == '+':
        p[0] = p[1] + (p[3],)
    else:
        p[0] = ('+', p[1], p[3])

def p_expr_minus(p):
    '''expr : expr MINUS term'''
    if isinstance(p[1], tuple) and p[1][0] == '-':
        p[0] = p[1] + (p[3],)
    else:
        p[0] = ('-', p[1], p[3])

def p_expr_term(p):
    '''expr : term'''
    p[0] = p[1]

def p_term_mul(p):
    '''term : term TIMES factor'''
    if isinstance(p[1], tuple) and p[1][0] == '*':
        p[0] = p[1] + (p[3],)
    else:
        p[0] = ('*', p[1], p[3])

def p_term_div(p):
    '''term : term DIVIDE factor'''
    p[0] = ('/', p[1], p[3])

def p_term_factor(p):
    '''term : factor
            | func'''
    p[0] = p[1]

def p_func(p):
    '''func : NAME LPAREN args RPAREN'''
    if isinstance(p[3], tuple):
        p[0] = (p[1],) + p[3]
    else:
        p[0] = (p[1], p[3])

def p_args_comma(p):
    '''args : args COMMA expr'''

    if isinstance(p[1], tuple):
        value = p[1] + (p[3],)
    else:
        value = (p[1], p[3])
    p[0] = value

def p_args_expr(p):
    '''args : expr'''
    p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER
              | NAME
              | fat
              | func'''
    p[0] = p[1]

def p_fat_factor(p):
    '''fat : factor EXCLAMATION'''
    p[0] = ('!', p[1])

def p_fat_group(p):
    '''fat : LPAREN expr RPAREN EXCLAMATION'''
    p[0] = ('!', p[2])

yacc.yacc()
parse = yacc.parse  # @UndefinedVariable
