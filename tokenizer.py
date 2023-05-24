from collections import namedtuple
from string import ascii_letters

Symbol = namedtuple("Symbol", ("name", "synonyms"))


class Token:
    def __init__(self, tokentype, data, read_data, part):
        self.type = tokentype
        self.data = data
        self.read_data = read_data
        self.part = part

    def is_symbol(self, *symbol):
        return self.type == "sym" and self.data in symbol

    def is_identifier(self):
        return self.type == "id"

    def squigles(self):
        if self.part < 0:
            return ""
        return " " * self.part + "^" * len(self.read_data)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.data == other.data and self.type == other.type

    def __str__(self):
        return f"'{self.data}' ({self.type}, {self.part})"


class TokenList:
    def __init__(self):
        self.data: list[Token] = []
        self.pos = 0
        self.stack = []

    def peek_at(self, i):
        if i < len(self.data):
            return self.data[i]
        return Token("sym", "EOF", "", -1)

    def print(self):
        print(self.pos, end=" ")
        for i, element in enumerate(self.data[self.pos:]):
            if i:
                print(", ", end="")
            print(element, end="")
        print()

    def add(self, element):
        self.data.append(element)

    def peek(self, i=0) -> Token:
        return self.peek_at(self.pos + i)

    def discard(self):
        self.pos += 1

    def get(self) -> Token:
        self.pos += 1
        return self.peek_at(self.pos - 1)


def symbol_token(string: str, length):
    symbols = [
        Symbol("^", ["^", "and", "&"]),
        Symbol("v", ["v", "or", "|"]),
        Symbol("->", ["->", "implies"]),
        Symbol("~", ["~", "not"]),
        Symbol("forall", ["forall", "A"]),
        Symbol("exists", ["exists", "E"]),
        Symbol("==", ["==", "equals"]),
        Symbol("!=", ["!=", "=/="]),
        Symbol("(", ["("]),
        Symbol(")", [")"]),
        Symbol(".", ["."]),
        Symbol(",", [","])
    ]
    for symbol in symbols:
        for name in symbol.synonyms:
            if string.startswith(name):
                return string[len(name):], Token("sym", symbol.name, name, length - len(string))
    return string, None


def identifier_token(string, length):
    identifier = ""
    while string and string[0] in ascii_letters:
        identifier += string[0]
        string = string[1:]
    if identifier:
        return string, Token("id", identifier, identifier, length - len(string) - len(identifier))
    return string, None


def tokenize(string):
    tokens = TokenList()
    length = len(string)
    while string:
        string, token = symbol_token(string, length)
        if not token:
            string, token = identifier_token(string, length)
        if not token:
            raise ValueError(string)
        tokens.add(token)
        string = string.lstrip()
    return tokens
