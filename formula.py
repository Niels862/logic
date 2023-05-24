from parser import Parser


class Formula:
    def __init__(self, string):
        self.string = string
        self.ast = Parser(string).parse()

    def print_ast(self):
        self.ast.print()

    def unparse(self):
        return self.ast.unparse()

    def __eq__(self, other):
        if not isinstance(other, Formula):
            return NotImplemented
        return self.ast == other.ast
