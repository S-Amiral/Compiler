"""Recursive interpreter package."""
import sys
from functools import reduce

import AST
from AST import addToClass
from parser5 import parse

operations = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
}


vars = {}


@addToClass(AST.ProgramNode)
def execute(self):
    """Execute ProgramNode."""
    for c in self.children:
        c.execute()


@addToClass(AST.TokenNode)  # noqa: F811
def execute(self):
    """Execute TokenNode."""
    if isinstance(self.tok, str):
        try:
            return vars[self.tok]
        except KeyError:
            print("*** Error: variable %s undefined!" % self.tok)
    return self.tok


@addToClass(AST.OpNode)  # noqa: F811
def execute(self):
    """Execute OpNode."""
    args = [c.execute() for c in self.children]
    if len(args) == 1:
        args.insert(0, 0)
    return reduce(operations[self.op], args)


@addToClass(AST.AssignNode)  # noqa: F811
def execute(self):
    """Execute AssignNode."""
    vars[self.children[0].tok] = self.children[1].execute()


@addToClass(AST.PrintNode)  # noqa: F811
def execute(self):
    """Execute PrintNode."""
    print(self.children[0].execute())


@addToClass(AST.WhileNode)  # noqa: F811
def execute(self):
    """Execute WhileNode."""
    while(self.children[0].execute()):
        self.children[1].execute()


if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    ast = parse(prog)

    ast.execute()
