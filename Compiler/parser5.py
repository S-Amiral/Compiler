import os
import sys

import ply.yacc as yacc

import AST
from lex5 import tokens  # noqa: F401

operations = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
}

precedence = (
    ('left', 'ADD_OP'),
    ('left', 'MUL_OP'),
    ('right', 'UMINUS'),
)

vars = {}
fcts = {}


def p_programme(p):
    """ programme : statement
    |  statement programme """
    try:
        p[0] = AST.ProgramNode([p[1]] + p[2].children)
    except Exception as e:
        p[0] = AST.ProgramNode(p[1])


def p_statement(p):
    """ statement : assign
        | structure
        | condition
        | fct
        | PRINT expression ';' """
    try:
        p[0] = AST.PrintNode(p[2])
    except Exception as e:
        p[0] = p[1]


def p_condition_if(p):
    """ condition_if : expression '<' expression
        | expression '>' expression
        | expression EQUALS expression
        | expression LESSTHAN expression
        | expression GREATTHAN expression
        | expression NOTEQUAL expression
        """
    p[0] = AST.IfConditionNode(p[2], [p[1], p[3]])


def p_condition(p):
    """ condition : IF '(' condition_if ')' '{' programme '}' """
    p[0] = AST.IfNode([p[3], p[6]])


def p_structure_while_cond(p):
    """ structure : WHILE '(' condition_if ')' '{' programme '}' """
    p[0] = AST.WhileNode([p[3], p[6]])


def p_structure(p):
    """ structure : WHILE expression '{' programme '}' """
    p[0] = AST.WhileNode([p[2], p[4]])


def p_for(p):
    """ structure : FOR '(' fct_assign ';' condition_if ';' \
    fct_assign ')' '{' programme '}' """
    p[0] = AST.ForNode([p[3], p[5], p[7], p[10]])


def p_fct_def(p):
    """
    fct : DEF IDENTIFIER '(' ')' '{' programme '}'
    """
    fcts[p[2]] = [None, p[6]]
    p[0] = AST.FunctionNode(p[2], [AST.FunctionParametersNode([]), p[6]])


def p_fct_def_params(p):
    """
    fct : DEF IDENTIFIER '(' fct_expression ')' '{' programme '}'
    """
    fcts[p[2]] = [p[4], p[7]]
    p[0] = AST.FunctionNode(p[2], [AST.FunctionParametersNode(p[4]), p[7]])


def p_fct(p):
    """
    fct : IDENTIFIER '(' ')' ';'
    """
    if p[1] in fcts:
        p[0] = AST.FunctionNode(p[1], [AST.FunctionParametersNode([])])
    else:
        exit("Syntax error near line %s\n>> Function \"%s\" was not declared" %
             (p.lineno(1), p[1]))
        raise SyntaxError(p)


def p_fct_params(p):
    """
    fct : IDENTIFIER '(' fct_expression ')' ';'
    """
    if p[1] in fcts:
        p[0] = AST.FunctionNode(p[1], [AST.FunctionParametersNode(p[3])])
    else:
        exit("Syntax error near line %s\n>> Function \"%s\" was not declared" %
             (p.lineno(1), p[1]))
        raise SyntaxError(p)


def p_fct_expression(p):
    """
    fct_expression : expression
        | expression ',' fct_expression
    """
    try:
        p[0] = list()
        p[0].append(p[1])
        try:
            p[0].extend(p[3])
        except TypeError as e:
            p[0].append(p[3])
    except Exception as e:
        p[0] = list()
        p[0].append(p[1])


def p_expression_op(p):
    """expression : expression ADD_OP expression
            | expression MUL_OP expression"""
    p[0] = AST.OpNode(p[2], [p[1], p[3]])


def p_expression_bool(p):
    """ expression : TRUE
            | FALSE """
    p[0] = AST.TokenNode(p[1])


def p_expression_num(p):
    """ expression : NUMBERAL """
    p[0] = AST.TokenNode(p[1])


def p_expression_string(p):
    """expression : STRING"""
    p[0] = AST.TokenNode(p[1])


def p_expression_var(p):
    """ expression : IDENTIFIER """
    p[0] = AST.TokenNode(p[1])


def p_expression_paren(p):
    """expression : '(' expression ')' """
    p[0] = p[2]


def p_minus(p):
    """ expression : ADD_OP expression %prec UMINUS"""
    p[0] = AST.OpNode(p[1], [p[2]])


def p_variable_type(p):
    """ variable_type : NUMBER
    | STRING
    | BOOL """
    p[0] = p[1]


def p_expression_fct(p):
    """ expression : variable_type IDENTIFIER """
    vars[p[2]] = (p[1], None)
    p[0] = AST.AssignInitNode(p[1], [AST.TokenNode(p[2]), AST.TokenNode(None)])


def p_assign_semicolon(p):
    """assign : assignation ';'"""
    p[0] = p[1]


def p_assign_fct(p):
    """fct_assign : assignation """
    p[0] = p[1]


def p_assign_number(p):
    """ assignation : NUMBER IDENTIFIER '=' expression """
    vars[p[2]] = ('NUMBER', p[4])
    p[0] = AST.AssignInitNode(p[1], [AST.TokenNode(p[2]), p[4]])


def p_assign_string(p):
    """ assignation : STRING IDENTIFIER '=' TEXT """
    vars[p[2]] = ('STRING', p[4])
    p[0] = AST.AssignInitNode(p[1], [AST.TokenNode(p[2]), AST.TokenNode(p[4])])


def p_assign_bool(p):
    """ assignation : BOOL IDENTIFIER '=' TRUE
        | BOOL IDENTIFIER '=' FALSE
    """
    vars[p[2]] = ('BOOL', p[4])
    p[0] = AST.AssignInitNode(p[1], [AST.TokenNode(p[2]), AST.TokenNode(p[4])])


def p_assign(p):
    """ assignation : IDENTIFIER '=' expression """
    try:
        vars[p[1]] = (vars[p[1]][0], p[3])
        p[0] = AST.AssignNode([AST.TokenNode(p[1]), p[3]])
    except KeyError as e:
        exit("Syntax error near line %s\n>> Token \"%s\" was not declared" %
             (p.lineno(1), p[1]))
        raise SyntaxError(p)


def p_expression_text(p):
    """expression : TEXT"""
    p[0] = AST.TokenNode(p[1])


def p_error(p):
    if p:
        tok = parser.token()
        print("Syntax error at token \"%s\" near line %s" % (p.type, p.lineno))
        # Just discard the token and tell the parser it's okay.
        parser.errok()
        return tok
    else:
        print("Syntax error at EOF")


def parse(program):
    return yacc.parse(program)


parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import time

    prog = open(sys.argv[1]).read()
    result = yacc.parse(prog, debug=1)
    time.sleep(1)
    print(result)
    graph = result.makegraphicaltree()
    file_index = 0
    extension = '−ast.pdf'
    oldname = os.path.splitext(sys.argv[1])[0]
    while os.path.exists(oldname + str(file_index) + extension):
        file_index += 1
    name = oldname + str(file_index) + extension
    graph.write_pdf(name)
    print("wrote ast to", name)
