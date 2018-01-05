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
local_vars = {}
fcts = {}


@addToClass(AST.ProgramNode)
def execute(self):
    """Execute ProgramNode."""
    global local_vars
    for c in self.children:
        c.execute()
    local_vars = {}  # flush local variables at end of execution


@addToClass(AST.TokenNode)  # noqa: F811
def execute(self):
    """Execute TokenNode."""
    if isinstance(self.tok, str) and self.tok[0] is not '"':
        try:
            return local_vars[self.tok]
        except KeyError:
            try:
                return vars[self.tok]
            except KeyError:
                raise KeyError
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


@addToClass(AST.IfNode)  # noqa: F811
def execute(self):
    """Execute WhileNode."""
    if(self.children[0].execute()):
        self.children[1].execute()


@addToClass(AST.FunctionNode)  # noqa: F811
def execute(self):
    """Execute FunctionNode."""
    if self.identifier not in fcts and len(self.children) > 0:
        fcts[self.identifier] = self.children
    elif self.identifier in fcts:
        args = self.children
        function_args = fcts[self.identifier][0]

        try:  # check if function and call have same number of arguments
            assert len(args) is len(function_args)
        except AssertionError as e:
            exit("ERROR!\nThe function you are calling needs %s parameters!" %
                 len(function_args))

        if len(function_args) > 0:  # set local variables for function
            i = 0
            for i in range(len(args.children)):
                local_vars[function_args.children[i].tok
                           ] = args.children[i].execute()
        fcts[self.identifier][1].execute()


if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    ast = parse(prog)

    ast.execute()
