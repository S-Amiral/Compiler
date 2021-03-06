"""Compiler package."""
import os
import sys

import AST
from AST import addToClass
from parser5 import parse

types = {
    'number': 'num',
    'string': 'string'
}

cond_while_index = 1
cond_for_index = 1
cond_if_index = 1
register_index = 0
last_mult = -1
cmpt = 0
retour = ""

func = {}
register_mult = []
register_add = []


@addToClass(AST.ProgramNode)  # noqa: F811
def compile(self):
    """Compile ProgrammNode."""
    byte_code = ""
    for c in self.children:
        byte_code += c.compile()
    return byte_code


@addToClass(AST.TokenNode)  # noqa: F811
def compile(self):
    """Compile TokenNode."""
    return "%s" % self.tok


@addToClass(AST.PrintNode)  # noqa: F811
def compile(self):
    """Compile PrintNode."""
    return "\tsay %s" % self.children[0].tok + "\n\n"


@addToClass(AST.OpNode)  # noqa: F811
def compile(self):
    """Compile OpNode."""
    global register_index, register_mult, register_add, cmpt, retour, last_mult

    byte_code = ""
    operator = True

    for c in self.children:

        number = c.compile()

        if self.op is '-' and len(self.children) is 1:
            number = '-' + number

        # operator permet de ne pas effectué deux fois le même noeud
        if operator:
            # priorité aux multiplications et divisions
            if self.op is '*' or self.op is '/':
                byte_code += "\n\t$N%s = " % register_index

                if cmpt < 1:
                    byte_code += number
                else:
                    byte_code += "$N%s" % (register_index-1)

                byte_code += ' ' + self.op + ' '
                byte_code += self.children[1].compile()

                if register_index not in register_mult:
                    register_mult.append(register_index)

                cmpt += 1
                register_index += 1
            else:
                cmpt = 0

            operator = False
        # puis traitement des additions et soustractions
        if self.op is '+' or self.op is '-':
            register_add.append(number + ' ' + self.op)

    if register_mult:
        if last_mult != register_mult[-1]:
            last_mult = register_mult[-1]
        else:
            register_add.append("$N%s" % register_mult[-1] + ' ' + self.op)

    retour += byte_code

    return retour


@addToClass(AST.IfConditionNode)  # noqa: F811
def compile(self):
    """Compile IfConditionNode."""
    byte_code = "if " + self.children[0].compile()
    byte_code += " " + self.comp + " "
    byte_code += self.children[1].compile()

    return byte_code


@addToClass(AST.IfNode)  # noqa: F811
def compile(self):
    """Compile IfNode."""
    global cond_if_index

    start_tag = "COND%s" % cond_if_index
    end_tag = "COND%s_END" % cond_if_index

    go_start = "goto " + start_tag + "\n\t"
    go_end = "goto " + end_tag + "\n\t"

    byte_code = "\t" + self.children[0].compile() + " "
    byte_code += go_start + go_end + start_tag + ":\n"
    byte_code += self.children[1].compile() + "\t"
    byte_code += end_tag + ":\n\t"

    return byte_code


@addToClass(AST.AssignInitNode)  # noqa: F811
def compile(self):
    """Compile AssignInitNode."""
    global register_index, register_add, register_mult, retour

    byte_code = "\t.local " + types[self.type_var]
    byte_code += " " + self.children[0].tok + "\n\t"

    register_type = ""

    val = self.children[1].compile()

    if '"' not in val:
        register_type = "$N"
    else:
        register_type = "$S"

    if len(register_add) > 1:
        # correspond aux opérations faites avant
        # d'initialiser le résultat à la variable
        byte_code += val + "\n\t"
        byte_code += register_type + "%s = " % register_index
        byte_code += register_add[0] + " " + register_add[1]
        byte_code = byte_code[:-1]
        byte_code += "\n\t"
        register_add = register_add[2:]
        # register_index += 1
        for term in register_add:
                byte_code += "$N%s = " % (register_index + 1)
                byte_code += term + " $N%s" % register_index
                byte_code += "\n\t"
                register_index += 1
    else:
        byte_code += register_type + "%s = " % register_index
        byte_code += val + "\n\t"

    byte_code += "\n\t" + self.children[0].tok + " = "
    byte_code += register_type + "%s" % register_index
    byte_code += "\n\n"

    # reset le retour des multiplications
    retour = ""
    # reset le tableau des additions
    register_add = []
    # reset le tableau des multiplications
    register_mult = []

    register_index += 1

    return byte_code


@addToClass(AST.AssignNode)  # noqa: F811
def compile(self):
    """Compile AssignNode."""
    global register_index, register_add, register_mult, retour

    register_type = ""
    byte_code = ""

    val = self.children[1].compile()

    if '"' not in val:
        register_type = "$N"
    else:
        register_type = "$S"

    if len(register_add) > 1:
        # correspond aux opérations faites avant
        # d'initialiser le résultat à la variable
        byte_code = val + "\n\t"
        byte_code += register_type + "%s = " % register_index
        byte_code += register_add[0] + " " + register_add[1]
        byte_code = byte_code[:-1]
        byte_code += "\n\t"
        register_add = register_add[2:]
        # register_index += 1
        for term in register_add:
                byte_code += "$N%s = " % (register_index + 1)
                byte_code += term + " $N%s" % register_index
                byte_code += "\n\t"
                register_index += 1
    else:
        byte_code += register_type + "%s = " % register_index
        byte_code += val + "\n\t"

    byte_code += "\n\t" + self.children[0].tok + " = "
    byte_code += register_type + "%s" % register_index
    byte_code += "\n\n"

    # reset le retour des multiplications
    retour = ""
    # reset le tableau des additions
    register_add = []
    # reset le tableau des multiplications
    register_mult = []

    register_index += 1

    return byte_code


@addToClass(AST.WhileNode)  # noqa: F811
def compile(self):
    """Compile WhileNode."""
    global cond_while_index

    byte_code = ""

    # prepare tags
    start_tag = "WLOOP%s" % cond_while_index
    end_tag = "WLOOP%s_DONE" % cond_while_index

    # inc index in case there are more while
    cond_while_index += 1

    cond_byte_code = self.children[0].compile()
    cond_byte_code += " goto " + start_tag
    body_byte_code = self.children[1].compile()

    byte_code = "\t" + start_tag + ":" + "\n"
    byte_code += body_byte_code + "\t" + cond_byte_code
    byte_code += "\n\tgoto " + end_tag + "\n\t"
    byte_code += end_tag + ":\n"

    return byte_code + "\n"


@addToClass(AST.ForNode)  # noqa : F811
def compile(self):
    """Compile ForNode."""
    global cond_for_index

    start_tag = "FLOOP%s" % cond_for_index
    end_tag = "FLOOP%s_DONE" % cond_for_index

    cond_for_index += 1

    # cond of for
    cond_byte_code = self.children[1].compile()
    cond_byte_code += " goto " + start_tag
    # body of for
    body_byte_code = self.children[3].compile()
    # incrementation
    inc_byte_code = self.children[2].compile()

    # init for variable
    byte_code = self.children[0].compile() + "\t"
    byte_code += start_tag + ":" + "\n"
    byte_code += body_byte_code + "\t" + inc_byte_code
    byte_code += "\t" + cond_byte_code + "\n\tgoto "
    byte_code += end_tag + "\n\t" + end_tag + ":\n"

    return byte_code + "\n"


@addToClass(AST.FunctionNode)  # noqa : F811
def compile(self):
    """Compile FunctionNode."""
    byte_code = ""

    if len(self.children) > 1:
        func_name = self.identifier
        func_body = self.children[1].compile()

        byte_code = "\n.sub '" + func_name + "'\n"
        if len(self.children[0]) > 0:
            for c in self.children[0]:
                byte_code += "\t.param " + types[c.type_var]
                byte_code += " " + c.children[0].tok + "\n"

        byte_code += func_body
        byte_code += ".end\n"

        func[func_name] = byte_code
    else:
        byte_code = "\t'" + self.identifier + "' ("

        if len(self.children[0]) > 0:
            for c in self.children[0]:
                byte_code += "%s" % c.tok + ","
            byte_code = byte_code[:-1]
        byte_code += ")\n"

        return byte_code + "\n"

    return ""


if __name__ == "__main__":
    prog = open(sys.argv[1]).read()
    ast = parse(prog)
    compiled = ".sub main\n" + ast.compile() + ".end\n"
    name = os.path.splitext(sys.argv[1])[0] + '.pir'
    outfile = open(name, 'w')
    for f in func.values():
        compiled += f
    outfile.write(compiled)
    outfile.close()
    # ast.execute()
    print("Wrote output to ", name)