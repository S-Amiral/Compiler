"""Recursive interpreter package."""
import operator
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

ops = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne
}

vars = {}
local_vars = {}
fcts = {}


@addToClass(AST.ProgramNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute ProgramNode."""
    global local_vars
    for c in self.children:
        c.execute(call_type)
    local_vars = {}  # flush local variables at end of execution


@addToClass(AST.TokenNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute TokenNode."""
    if isinstance(self.tok, str) and self.tok[0] is not '"':
        try:
            return local_vars[self.tok][1]
        except KeyError:
            try:
                return vars[self.tok][1]
            except KeyError:
                print("*** Error: variable %s undefined!" % self.tok)
    return self.tok


@addToClass(AST.OpNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute OpNode."""
    args = [c.execute() for c in self.children]
    if len(args) == 1:
        args.insert(0, 0)
    return reduce(operations[self.op], args)


@addToClass(AST.AssignInitNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute AssignInitNode."""
    if call_type is "main":
        vars[self.children[0].tok] = (self.type_var,
                                      self.children[1].execute())
    else:
        local_vars[self.children[0].tok] = (
            self.type_var, self.children[1].execute())


@addToClass(AST.AssignNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute AssignNode."""
    if call_type is "main":
        vars[self.children[0].tok] = (
            vars[self.children[0].tok][0], self.children[1].execute())
    else:
        local_vars[self.children[0].tok] = (
            local_vars[self.children[0].tok][0], self.children[1].execute())


@addToClass(AST.PrintNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute PrintNode."""
    print(self.children[0].execute())


@addToClass(AST.WhileNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute WhileNode."""
    while(self.children[0].execute()):
        self.children[1].execute()


@addToClass(AST.IfNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute WhileNode."""
    if(self.children[0].execute()):
        self.children[1].execute()


@addToClass(AST.FunctionNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute FunctionNode."""
    if self.identifier not in fcts and len(self.children) > 0:
        fcts[self.identifier] = self.children  # [Function parameters, Program]
    elif self.identifier in fcts:
        args = self.children[0]  # passed args
        function_args = fcts[self.identifier][0]  # definition args

        try:  # check if function and call have same number of arguments
            assert len(args) is len(function_args)
        except AssertionError as e:
            exit("ERROR!\nThe function you are calling needs %s parameters!" %
                 len(function_args))
        if len(function_args) > 0:  # set local variables for function
            i = 0
            variable_type = function_args.children[0].type_var
            for i in range(len(args.children)):
                variable_name = function_args.children[i].children[0].tok
                local_vars[variable_name] = (
                    variable_type, args.children[i].execute())

        fcts[self.identifier][1].execute("fct")


@addToClass(AST.IfConditionNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute IfConditionNode."""
    op_func = ops[self.comp]
    return op_func(self.children[0].execute(), self.children[1].execute())


@addToClass(AST.ForNode)  # noqa: F811
def execute(self, call_type="main"):
    """Execute ForNode."""
    self.children[0].execute()
    while self.children[1].execute():
        self.children[3].execute()
        self.children[2].execute()


if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    ast = parse(prog)

    ast.execute()