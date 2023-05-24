from formula import Formula, Model, Language


def main():
    formula = Formula("forall x. P(x, 1, add(x, 1))", True)
    formula.ast.print()
    model = Model(range(2), {
        "1": lambda: 1,
        "add": lambda x, y: (x + y) % 2
    }, {
        "P": lambda x, y, z: (x + y) % 2 == z
    })
    print(formula.ast.value({}, model))


if __name__ == "__main__":
    main()
