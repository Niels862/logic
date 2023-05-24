from formula import Formula


def main():
    formula = Formula("a v b")
    formula.print_ast()
    print(formula.unparse())
    print(formula == Formula("a or b"))


if __name__ == "__main__":
    main()
