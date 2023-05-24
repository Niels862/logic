from formula import Formula


def main():
    formula = Formula("a v b ^ c", False)
    formula.print_ast()
    print(formula.unparse())


if __name__ == "__main__":
    main()
