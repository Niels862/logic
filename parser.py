from tokenizer import tokenize
from ast import *
from string import ascii_lowercase, ascii_uppercase, digits


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
        self.function = lambda identifier: all(c in ascii_lowercase + digits for c in identifier)
        self.predicate = lambda identifier: all(c in ascii_uppercase for c in identifier)

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
                args = self.parse_args_list()
                if self.function(identifier.data):
                    node = ASTFunction(identifier, args)
                elif self.predicate(identifier.data):
                    node = ASTPredicate(identifier, args)
                else:
                    raise ParsingError(
                        self.string, identifier,
                        f"Identifier '{identifier.data}' does not match function or predicate map",
                    )
                self.expect_symbol(")")
                return node
            return ASTVariable(identifier)
        if self.tokens.peek().is_symbol("~"):
            return self.parse_unary()
        raise ParsingError(self.string, self.tokens.peek(), f"Expected term, got {self.tokens.peek()}")

    def parse_unary(self):
        if self.tokens.peek().is_symbol("~"):
            symbol = self.tokens.get()
            return ASTNot(symbol, self.parse_term())
        return self.parse_term()

    def parse_equality(self):
        node = self.parse_term()
        if self.tokens.peek().is_symbol("==", "!="):
            symbol = self.tokens.get()
            if symbol.is_symbol("=="):
                return ASTEquality(symbol, node, self.parse_term())
            return ASTInequality(symbol, node, self.parse_term())
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
        symbol = self.tokens.get()
        identifier = self.expect_identifier()
        self.expect_symbol(".")
        if symbol.is_symbol("exists"):
            return ASTExists(symbol, identifier, self.parse_quantifier())
        return ASTForAll(symbol, identifier, self.parse_quantifier())

    def parse_implication(self):
        node = self.parse_and_or()
        while self.tokens.peek().is_symbol("->"):
            symbol = self.tokens.get()
            right = self.parse_implication()
            node = ASTImplication(symbol, node, right)
        return node

    def parse_and_or(self):
        node = self.parse_equality()
        found_and = found_or = False
        while self.tokens.peek().is_symbol("^", "v"):
            symbol = self.tokens.get()
            right = self.parse_term()
            if symbol.is_symbol("v"):
                found_or = True
                node = ASTOr(symbol, node, right)
            else:
                found_and = True
                node = ASTAnd(symbol, node, right)
            if found_and and found_or:
                raise ParsingError(
                    self.string, symbol, f"Operators 'and' and 'or' should be explicitly grouped",
                )
        return node
