from tokenizer import tokenize
from ast import ASTNode


class ParsingError(Exception):
    def __init__(self, string, token, msg):
        self.string = string
        self.token = token
        self.msg = msg

    def __str__(self):
        return f"\n{self.string}\n{self.token.squigles()}\nParsingError: {self.msg}"


class Parser:
    def __init__(self, string):
        self.string = string
        self.tokens = tokenize(string)

    def parse(self):
        ast = self.parse_quantifier()
        if not self.tokens.peek().is_symbol("EOF"):
            raise ParsingError(self.string, self.tokens.peek(), f"Unexpected token: {self.tokens.peek()}")
        return ast

    def expect_identifier(self):
        if not self.tokens.peek().is_identifier():
            raise ParsingError(self.string, self.tokens.peek(), f"Expected identifier, got {self.tokens.peek()}")
        return self.tokens.get()

    def expect_symbol(self, *symbol):
        if not self.tokens.peek().is_symbol(*symbol):
            raise ParsingError(
                self.string, self.tokens.peek(), "Expected {}, got {}".format(
                    " or ".join([f"'{sym}'" for sym in symbol]),
                    self.tokens.peek()
                )
            )
        return self.tokens.get()

    def parse_term(self):
        if self.tokens.peek().is_symbol("("):
            return self.parse_bracketed_formula()
        if self.tokens.peek().is_identifier():
            identifier = self.tokens.get()
            if self.tokens.peek().is_symbol("("):
                self.tokens.discard()
                node = ASTNode(identifier, self.parse_args_list())
                self.expect_symbol(")")
                return node
            return ASTNode(identifier)
        if self.tokens.peek().is_symbol("~"):
            return self.parse_unary()
        raise ParsingError(self.string, self.tokens.peek(), f"Expected term, got {self.tokens.peek()}")

    def parse_unary(self):
        if self.tokens.peek().is_symbol("~"):
            symbol = self.tokens.get()
            return ASTNode(symbol, [self.parse_term()])
        return self.parse_term()

    def parse_equality(self):
        node = self.parse_term()
        if self.tokens.peek().is_symbol("==", "!="):
            symbol = self.tokens.get()
            return ASTNode(symbol, [node, self.parse_term()])
        return node

    def parse_args_list(self):
        args = []
        if self.tokens.peek().is_symbol(")"):
            return args
        args.append(self.parse_term())
        while self.tokens.peek().is_symbol(","):
            self.tokens.discard()
            args.append(self.parse_term())
        return args

    def parse_bracketed_formula(self):
        self.expect_symbol("(")
        ast = self.parse_quantifier()
        self.expect_symbol(")")
        return ast

    def parse_quantifier(self):
        if not self.tokens.peek().is_symbol("forall", "exists"):
            return self.parse_implication()
        op = self.tokens.get()
        var = self.expect_identifier()
        self.expect_symbol(".")
        return ASTNode(op, [ASTNode(var), self.parse_quantifier()])

    def parse_implication(self):
        node = self.parse_and_or()
        while self.tokens.peek().is_symbol("->"):
            symbol = self.tokens.get()
            right = self.parse_implication()
            node = ASTNode(symbol, [node, right])
        return node

    def parse_and_or(self):
        node = self.parse_equality()
        while self.tokens.peek().is_symbol("^", "v"):
            symbol = self.tokens.get()
            right = self.parse_and_or()
            node = ASTNode(symbol, [node, right])
        return node
