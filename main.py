from formula import Formula


def main():
    formula = Formula("forall x. exists x. forall y. P(x, y)")
    formula.print_ast()
    print(formula.unparse())
    print(formula.ast.fresh("x"))


if __name__ == "__main__":
    main()
