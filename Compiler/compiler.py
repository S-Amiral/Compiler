"""Compiler package."""
import os
import sys

import AST
from AST import addToClass
from parser5 import parse

operations = {
    '+': 'ADD\n',
    '-': 'SUB\n',
    '*': 'MUL\n',
    '/': 'DIV\n',
}

cond_index = 1

vars = {}


@addToClass(AST.ProgramNode)
def compile(self):
    """Compile ProgrammNode."""
    byte_code = ""
    for c in self.children:
        byte_code += c.compile()
    return byte_code


@addToClass(AST.TokenNode)  # noqa: F811
def compile(self):
    """Compile TokenNode."""
    byte_code = ""
    if isinstance(self.tok, str):
        byte_code += "PUSHV %s\n" % self.tok
    else:
        byte_code += "PUSHC %s\n" % self.tok
    return byte_code


@addToClass(AST.PrintNode)  # noqa: F811
def compile(self):
    """Compile PrintNode."""
    return self.children[0].compile() + "PRINT\n"


@addToClass(AST.OpNode)  # noqa: F811
def compile(self):
    """Compile OpNode."""
    byte_code = ""

    for c in self.children:
        byte_code += c.compile()
    if self.op is '-' and len(self.children) is 1:
        byte_code += 'USUB\n'
    else:
        byte_code += operations[self.op]
    return byte_code


@addToClass(AST.AssignNode)  # noqa: F811
def compile(self):
    """Compile AssignNode."""
    return self.children[1].compile() + "SET %s\n" % self.children[0].tok


@addToClass(AST.WhileNode)  # noqa: F811
def compile(self):
    """Compile WhileNode."""
    global cond_index

    # prepare tags
    cond_tag = "cond%s" % cond_index
    body_tag = "body%s" % cond_index

    # inc index in case there are more while
    cond_index += 1

    start_byte_code = "JMP " + cond_tag + "\n"

    body_byte_code = body_tag + ": " + self.children[1].compile()
    cond_byte_code = cond_tag + ": " + self.children[0].compile()

    end_byte_code = "JINZ " + body_tag + "\n"

    byte_code = start_byte_code + body_byte_code
    byte_code += cond_byte_code + end_byte_code

    return byte_code


if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    compiled = ast.compile()
    name = os.path.splitext(sys.argv[1])[0] + '.vw'
    outfile = open(name, 'w')
    outfile.write(compiled)
    outfile.close()
    # ast.execute()
    print("Wrote output to ", name)
