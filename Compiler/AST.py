"""
AST module.

Petit module utilitaire pour la construction, la manipulation et la
représentation d'arbres syntaxiques abstraits.
"""

import pydot


class Node:
    """Node class."""

    count = 0
    type = 'Node (unspecified)'
    shape = 'ellipse'

    def __init__(self, children=None):
        """Init node."""
        self.ID = str(Node.count)
        Node.count += 1
        if not children:
            self.children = []
        elif hasattr(children, '__len__'):
            self.children = children
        else:
            self.children = [children]
        self.next = []

    def addNext(self, next):
        """Add next node to node."""
        self.next.append(next)

    def asciitree(self, prefix=''):
        """Get ascii tree from node."""
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if not isinstance(c, Node):
                result += "%s*** Error: Child of type %r: %r\n" % (
                    prefix,
                    type(c),
                    c
                )
                continue
            result += c.asciitree(prefix)
        return result

    def __str__(self):
        """To string method."""
        return self.asciitree()

    def __repr__(self):
        """Representate method."""
        return self.type

    def makegraphicaltree(self, dot=None, edgeLabels=True):
        """Make graphical tree."""
        if not dot:
            dot = pydot.Dot()
        dot.add_node(pydot.Node(self.ID, label=repr(self), shape=self.shape))
        label = edgeLabels and len(self.children) - 1
        for i, c in enumerate(self.children):
            c.makegraphicaltree(dot, edgeLabels)
            edge = pydot.Edge(self.ID, c.ID)
            if label:
                edge.set_label(str(i))
            dot.add_edge(edge)
        return dot

    def threadTree(self, graph, seen=None, col=0):
        """Make thread tree."""
        colors = ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan')
        if not seen:
            seen = []
        if self in seen:
            return
        seen.append(self)
        new = not graph.get_node(self.ID)
        if new:
            graphnode = pydot.Node(self.ID, label=repr(self), shape=self.shape)
            graphnode.set_style('dotted')
            graph.add_node(graphnode)
        label = len(self.next) - 1
        for i, c in enumerate(self.next):
            if not c:
                return
            col = (col + 1) % len(colors)
            color = colors[col]
            c.threadTree(graph, seen, col)
            edge = pydot.Edge(self.ID, c.ID)
            edge.set_color(color)
            edge.set_arrowsize('.5')
            # Les arr�tes correspondant aux coutures ne sont
            # pas prises en compte pour le layout du graphe.
            # Ceci permet de garder l'arbre dans sa repr�sentation
            # "standard", mais peut provoquer des surprises
            # pour le trajet parfois un peu tarabiscot� des
            # coutures...
            # En commantant cette ligne, le layout sera bien
            # meilleur, mais l'arbre nettement moins reconnaissable.
            edge.set_constraint('false')
            if label:
                edge.set_taillabel(str(i))
                edge.set_labelfontcolor(color)
            graph.add_edge(edge)
        return graph


class ProgramNode(Node):
    """ProgrammNode class."""

    type = 'Program'


class TokenNode(Node):
    """TokenNode class."""

    type = 'token'

    def __init__(self, tok):
        """Init TokenNode."""
        Node.__init__(self)
        self.tok = tok

    def __repr__(self):
        """Represent node."""
        return repr(self.tok)


class FunctionParametersNode(Node):
    """FunctionParametersNode class."""

    type = 'function parameters'

    def __init__(self, children):
        """Init FunctionParametersNode."""
        Node.__init__(self)
        self.children = children

    def __repr__(self):
        """Represent Node."""
        if len(self.children) < 1:
            return "No parameters"
        return "Function parameters"

    def __len__(self):
        """Object length."""
        return len(self.children)

    def __iter__(self):
        """Iterate through children."""
        return iter(self.children)


class FunctionNode(Node):
    """FunctionNode class."""

    type = 'function'

    def __init__(self, identifier, children):
        """Init FunctionNode."""
        Node.__init__(self)
        self.identifier = identifier
        self.children = children

    def __repr__(self):
        """Represent node."""
        if (len(self.children) > 1
                and isinstance(self.children[1], ProgramNode)):
            return "Function %s" % (self.identifier)
        return "Call function %s" % (self.identifier)


class OpNode(Node):
    """OpNode class."""

    def __init__(self, op, children):
        """Init OpNode."""
        Node.__init__(self, children)
        self.op = op
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1

    def __repr__(self):
        """Represent node."""
        return "%s (%s)" % (self.op, self.nbargs)


class AssignInitNode(Node):
    """AssignInitNode class."""

    def __init__(self, type_var, children):
        """Init AssignInitNode."""
        Node.__init__(self, children)
        self.type_var = type_var
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1

    def __repr__(self):
        """Represent node."""
        return "%s assign" % self.type_var


class AssignNode(Node):
    """AssignNode class."""

    type = '='


class PrintNode(Node):
    """PrintNode class."""

    type = 'print'


class WhileNode(Node):
    """WhileNode class."""

    type = 'while'


class IfConditionNode(Node):
    """IfConditionNode class."""

    def __init__(self, comp, children):
        """Init IfConditionNode."""
        Node.__init__(self, children)
        self.comp = comp
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1

    def __repr__(self):
        """Represent node."""
        return "%s (%s)" % (self.comp, self.nbargs)


class ForNode(Node):
    """ForNode class."""

    type = 'for'


class IfNode(Node):
    """IfNode class."""

    type = 'if'


class EntryNode(Node):
    """EntryNode class."""

    type = 'ENTRY'

    def __init__(self):
        """Init EntryNode."""
        Node.__init__(self, None)


def addToClass(cls):
    """
    Add Method to class.

    Décorateur permettant d'ajouter la fonction décorée en tant que
    méthode d'une classe.
    """
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator
