from NumberlinkSatSolverV2 import NumberlinkSatSolver

if __name__ == '__main__':
    WIDTH = 18
    HEIGHT = 10

    FILE_NAME = "numberlink_18x10.txt"

    clues = []
    with open(FILE_NAME, "r") as f:
        for line in f.readlines():
            clue = line.strip().split("|")
            assert len(clue) == WIDTH
            clues.append(clue)
    assert len(clues) == HEIGHT

    solver = NumberlinkSatSolver(WIDTH, HEIGHT, clues)
    result = solver.solve()

    print(f"Satisfiable: {result.satisfiable}")
    print(f"Variables: {result.numberOfVariable}")
    print(f"Clauses: {result.numberOfClause}")
    print(f"Execution time (ms): {result.timeInMilisecond}")

    if(result.satisfiable):
        print()
        for row in result.result:
            print("".join(row))
