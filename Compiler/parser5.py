"""Code parser."""
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


def p_programme(p):
    """
    programme : statement
    |  statement ';' programme ';'
    """
    try:
        p[0] = AST.ProgramNode([p[1]] + p[3].children)
    except Exception as e:
        p[0] = AST.ProgramNode(p[1])


def p_statement(p):
    """
    statement : assignation
        | structure
        | PRINT expression
    """
    try:
        p[0] = AST.PrintNode(p[2])
    except Exception as e:
        p[0] = p[1]


def p_structure(p):
    """structure : WHILE expression '{' programme '}' """
    p[0] = AST.WhileNode([p[2], p[4]])


def p_expression_op(p):
    """
    expression : expression ADD_OP expression
        | expression MUL_OP expression
    """
    p[0] = AST.OpNode(p[2], [p[1], p[3]])


def p_expression_num(p):
    """expression : NUMBER"""
    p[0] = AST.TokenNode(p[1])


def p_expression_var(p):
    """expression : IDENTIFIER"""
    p[0] = AST.TokenNode(p[1])


def p_expression_paren(p):
    """expression : '(' expression ')'"""
    p[0] = p[2]


def p_minus(p):
    """expression : ADD_OP expression %prec UMINUS"""
    p[0] = AST.OpNode(p[1], [p[2]])


def p_assign(p):
    """assignation : IDENTIFIER '=' expression"""
    vars[p[1]] = p[3]
    p[0] = AST.AssignNode([AST.TokenNode(p[1]), p[3]])


def p_error(p):
    """Catch errors."""
    print("Syntax error in line %d" % p.lineno)
    parser.errok()


def parse(program):
    """Parse programm."""
    return yacc.parse(program)


parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    result = yacc.parse(prog, debug=1)
    print(result)

    graph = result.makegraphicaltree()
    name = os.path.splitext(sys.argv[1])[0] + '−ast.pdf'
    graph.write_pdf(name)
    print("wrote ast to", name)
