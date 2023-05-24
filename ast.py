from tokenizer import Token


class ASTValidationError(Exception):
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return f"'{self.node.unparse()}'"


class LanguageValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ASTNode:
    def __init__(self, data, children, is_term, is_formula):
        self.data: Token = data
        self.children: list[ASTNode] = children or []
        self.is_term = is_term
        self.is_formula = is_formula

    @property
    def left(self):
        if len(self.children) == 2:
            return self.children[0]
        raise ValueError("Cannot access 'left' of non-binary Node")

    @property
    def right(self):
        if len(self.children) == 2:
            return self.children[1]
        raise ValueError("Cannot access 'right' of non-binary Node")

    @property
    def child(self):
        if len(self.children) == 1:
            return self.children[0]
        raise ValueError("Cannot access 'child' of non-unary Node")

    @property
    def token(self):
        return self.data.data

    @property
    def arity(self):
        return len(self.children)

    def validate(self, first_order):
        return False

    def validate_language(self, language, fill_in):
        return all(child.validate_language(language, fill_in) for child in self.children)

    def print(self, indent=0):
        print(indent * "  " + str(self.data))
        for child in self.children:
            child.print(indent + 1)

    def unparse(self):
        return "?"

    def value(self, valuation):
        pass

    def substitute_references(self, identifier, reference):
        for child in self.children:
            child.substitute_references(identifier, reference)

    def fresh(self, identifier):
        return all(child.fresh(identifier) for child in self.children)

    def __eq__(self, other):
        if not isinstance(other, ASTNode):
            return NotImplemented
        return self.data == other.data and len(self.children) == len(other.children)\
            and all(child == other_child for (child, other_child) in zip(self.children, other.children))


class ASTBinary(ASTNode):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, [left, right], False, True)

    def validate(self, first_order):
        if (not first_order or (self.left.is_formula and self.right.is_formula))\
                and self.left.validate(first_order) and self.right.validate(first_order):
            return True
        raise ASTValidationError(self)

    def unparse(self):
        if self.left.is_term or isinstance(self.left, ASTPredicate)\
                or (self.token == self.left.token and not self.data.is_symbol("->"))\
                or (self.data.is_symbol("->") and self.left.data.is_symbol("v", "^")):
            left = self.left.unparse()
        else:
            left = f"({self.left.unparse()})"
        if self.right.is_term or isinstance(self.right, ASTPredicate)\
                or self.token == self.right.token\
                or (self.data.is_symbol("->") and self.right.data.is_symbol("v", "^")):
            right = self.right.unparse()
        else:
            right = f"({self.right.unparse()})"
        return f"{left} {self.token} {right}"


class ASTAnd(ASTBinary):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, left, right)

    def value(self, valuation):
        return self.left.value(valuation) and self.right.value(valuation)


class ASTOr(ASTBinary):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, left, right)

    def value(self, valuation):
        return self.left.value(valuation) or self.right.value(valuation)


class ASTImplication(ASTBinary):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, left, right)

    def value(self, valuation):
        value_left = self.left.value(valuation)
        return not value_left or (value_left and self.right.value(valuation))


class ASTEquality(ASTBinary):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, left, right)

    def validate(self, first_order):
        if first_order and self.left.is_term and self.right.is_term \
                and self.left.validate(first_order) and self.right.validate(first_order):
            return True
        raise ASTValidationError(self)

    def value(self, valuation):
        return self.left.value(valuation) == self.right.value(valuation)


class ASTInequality(ASTBinary):
    def __init__(self, symbol, left, right):
        super().__init__(symbol, left, right)

    def validate(self, first_order):
        if first_order and self.left.is_term and self.right.is_term \
                and self.left.validate(first_order) and self.right.validate(first_order):
            return True
        raise ASTValidationError(self)

    def value(self, valuation):
        return self.left.value(valuation) != self.right.value(valuation)


class ASTNot(ASTNode):
    def __init__(self, symbol, formula):
        super().__init__(symbol, [formula], False, True)

    def validate(self, first_order):
        if self.child.is_formula and self.child.validate(first_order):
            return True
        raise ASTValidationError(self)

    def unparse(self):
        return f"{self.token}{self.children[0].unparse()}"

    def value(self, valuation):
        return not self.child.value(valuation)


class ASTQuantifier(ASTNode):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, [formula], False, True)
        self.identifier = identifier
        self.child.substitute_references(identifier, 0)

    def validate(self, first_order):
        if first_order and self.child.is_formula and self.child.validate(first_order):
            return True
        raise ASTValidationError(self)

    def substitute_references(self, identifier, reference):
        self.child.substitute_references(identifier, reference + 1)

    def unparse(self):
        return f"{self.token} {self.identifier.data}. {self.child.unparse()}"


class ASTExists(ASTQuantifier):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, identifier, formula)

    def value(self, valuation):
        return NotImplemented


class ASTForAll(ASTQuantifier):
    def __init__(self, symbol, identifier, formula):
        super().__init__(symbol, identifier, formula)

    def value(self, valuation):
        return NotImplemented


class ASTVariable(ASTNode):
    def __init__(self, identifier):
        super().__init__(identifier, [], True, False)
        self.dereferenced = None

    def validate(self, first_order):
        return True

    def substitute_references(self, identifier, reference):
        if self.token == identifier.data:
            self.dereferenced = self.data.copy()
            self.data.data = reference

    def fresh(self, identifier):
        return not self.token == identifier

    def unparse(self):
        if isinstance(self.token, int):
            return self.dereferenced.data
        return self.token

    def value(self, valuation):
        return valuation.variables[self.token]


class ASTPredicate(ASTNode):
    def __init__(self, identfier, arguments):
        super().__init__(identfier, arguments, False, True)

    def validate(self, first_order):
        if first_order and all(child.is_term and child.validate(first_order) for child in self.children):
            return True
        raise ASTValidationError(self)

    def validate_language(self, language, fill_in):
        if fill_in and self.token not in language.predicate_arities:
            language.predicate_arities[self.token] = self.arity
        elif self.token not in language.predicate_arities:
            raise LanguageValidationError(f"Predicate '{self.token}' not in language")
        elif language.predicate_arities[self.token] != self.arity:
            raise LanguageValidationError(
                f"Arity mismatch for Predicate '{self.token}': {language.predicate_arities[self.token]} != {self.arity}"
            )
        return all(child.validate_language(language, fill_in) for child in self.children)

    def unparse(self):
        return "{}({})".format(
            self.token, ", ".join(child.unparse() for child in self.children)
        )

    def value(self, valuation):
        return valuation.predicates[self.token](*(child.value(valuation) for child in self.children))


class ASTFunction(ASTNode):
    def __init__(self, identifier, arguments):
        super().__init__(identifier, arguments, True, False)

    def validate(self, first_order):
        if first_order and all(child.is_term and child.validate(first_order) for child in self.children):
            return True
        raise ASTValidationError(first_order)

    def validate_language(self, language, fill_in):
        if fill_in and self.token not in language.function_arities:
            language.function_arities[self.token] = self.arity
        elif self.token not in language.function_arities:
            raise LanguageValidationError(f"Function '{self.token}' not in language")
        elif language.function_arities[self.token] != self.arity:
            raise LanguageValidationError(
                f"Arity mismatch for Function '{self.token}': {language.function_arities[self.token]} != {self.arity}"
            )
        return all(child.validate_language(language, fill_in) for child in self.children)

    def unparse(self):
        return "{}({})".format(
            self.token, ", ".join(child.unparse() for child in self.children)
        )

    def value(self, valuation):
        return valuation.functions[self.token](*(child.value(valuation) for child in self.children))
