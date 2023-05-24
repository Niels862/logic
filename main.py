from formula import Formula


def main():
    formula = Formula("(a -> b) v (b -> a)")
    formula.print_ast()
    print(formula.unparse())


if __name__ == "__main__":
    main()
