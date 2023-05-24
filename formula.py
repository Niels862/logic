from parser import Parser, ASTValidationError


class Formula:
    def __init__(self, string, first_order, language=None):
        self.string = string
        self.first_order = first_order
        self.ast = Parser(string).parse()
        self.language = language or Language()
        if first_order and self.ast.is_term:
            raise ASTValidationError(self.ast)
        self.ast.validate(first_order)
        self.ast.validate_language(self.language, language is None)

    def print_ast(self):
        self.ast.print()

    def unparse(self):
        return self.ast.unparse()


class Model:
    def __init__(self, universe, functions=None, predicates=None):
        self.universe = universe
        self.functions = functions or {}
        self.predicates = predicates or {}


class Language:
    def __init__(self, function_arities=None, predicate_arities=None):
        self.function_arities = function_arities or {}
        self.predicate_arities = predicate_arities or {}
