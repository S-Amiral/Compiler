import ply.lex as lex

reserved_words = (
    'while',
    'print',
    'if',
    'for',
    'number',
    'string',
    'bool',
    'true',
    'false',
    'def'
)

tokens = (
    'NUMBERAL',
    'ADD_OP',
    'MUL_OP',
    'IDENTIFIER',
    'EQUALS',
    'LESSTHAN',
    'GREATTHAN',
    'NOTEQUAL',
    'TEXT'
) + tuple(map(lambda s: s.upper(), reserved_words))

literals = '();=}{<>",'


def t_TEXT(t):
    r'".*?"'
    return t


def t_NOTEQUAL(t):
    r'!='
    return t


def t_LESSTHAN(t):
    r'<='
    return t


def t_GREATTHAN(t):
    r'>='
    return t


def t_EQUALS(t):
    r'=='
    return t


def t_ADD_OP(t):
    r'[+-]'
    return t


def t_MUL_OP(t):
    r'[*/]'
    return t


def t_NUMBERAL(t):
    r'\d+(\.\d+)?'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Line %d: Problem while parsing %s!" % (t.lineno, t.value))
        t.value = 0
    return t


def t_STRING(t):
    r'"(.*)"'
    return t


def t_IDENTIFIER(t):
    r'[A-Za-z_]\w*'
    if t.value in reserved_words:
        t.type = t.value.upper()
    return t

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Compute column.
#     input is the input text string
#     token is a token instance


def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


t_ignore = ' \t'


# Error handling rule

def t_error(t):
    print("Illegal character '%s'" % repr(t.value[0]))
    t.lexer.skip(1)


lex.lex()

if __name__ == "__main__":
    import sys

    prog = open(sys.argv[1]).read()

    lex.input(prog)

    while 1:
        tok = lex.token()
        if not tok:
            break
        print("line %d: %s(%s)" % (tok.lineno, tok.type, tok.value))