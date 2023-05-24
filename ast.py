from tokenizer import Token


class ASTNode:
    def __init__(self, data, children=None):
        self.data: Token = data
        self.children: list[ASTNode] = children or []

    @property
    def left(self):
        if len(self.children) == 2:
            return self.children[0]
        return ASTNode

    @property
    def right(self):
        if len(self.children) == 2:
            return self.children[1]
        return ASTNode

    @property
    def token(self):
        return self.data.data

    def preorder(self, callback):
        callback(self)
        for child in self.children:
            child.preorder(callback)

    def print(self, indent=0):
        print(indent * "  " + str(self.data))
        for child in self.children:
            child.print(indent + 1)

    def unparse(self):
        if self.data.is_identifier():
            if len(self.children):
                return "{}({})".format(self.token, ", ".join([child.unparse() for child in self.children]))
            return self.token
        if self.data.is_symbol("v", "^", "->", "==", "!="):
            if len(self.left.children) < 2 or (self.token == self.left.token and not self.data.is_symbol("->"))\
                    or self.data.is_symbol("->") and self.left.data.is_symbol("v", "^"):
                left = self.left.unparse()
            else:
                left = f"({self.left.unparse()})"
            if len(self.right.children) < 2 or self.token == self.right.token\
                    or self.data.is_symbol("->") and self.right.data.is_symbol("v", "^"):
                right = self.right.unparse()
            else:
                right = f"({self.right.unparse()})"
            return f"{left} {self.token} {right}"
        if self.data.is_symbol("~"):
            return f"{self.token}{self.children[0].unparse()}"
        if self.data.is_symbol("exists", "forall"):
            return f"{self.token} {self.left.token}. {self.right.unparse()}"
        return "?"

    def __eq__(self, other):
        if not isinstance(other, ASTNode):
            return NotImplemented
        return self.data == other.data and len(self.children) == len(other.children)\
            and all(child == other_child for (child, other_child) in zip(self.children, other.children))


class ASTAnd(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right])


class ASTOr(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right])


class ASTNot(ASTNode):
    def __init__(self, symbol, formula):
        super().__init__(symbol, [formula])


class ASTImplication(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right])


class ASTEquality(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right])


class ASTInequality(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right])


class ASTQuantifier(ASTNode):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, [identifier, formula])


class ASTExists(ASTQuantifier):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, identifier, formula)


class ASTForAll(ASTQuantifier):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, identifier, formula)


class ASTVariable(ASTNode):
    def __init__(self, identifier):
        super().__init__(identifier)


class ASTPredicate(ASTNode):
    def __init__(self, identfier, arguments):
        super().__init__(identfier, arguments)


class ASTFunction(ASTNode):
    def __init__(self, identifier, arguments):
        super().__init__(identifier, arguments)
