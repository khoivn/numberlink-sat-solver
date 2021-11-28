from NumberlinkSatSolver import NumberlinkSatSolver
import os

if __name__ == '__main__':
    folder = "samples"
    for file in sorted(os.listdir(folder)):
        path = os.path.join(folder, file)
        underscore_index = file.index("_")
        x_index = file.index("x")
        dot_index = file.index(".")
        width = int(file[underscore_index + 1: x_index])
        height = int(file[x_index + 1: dot_index])

        print(width, height, end="\t")

        clues = []
        with open(path, "r") as f:
            for line in f.readlines():
                clue = [c if c != '.' else '' for c in list(line.strip())]
                assert len(clue) == width
                clues.append(clue)
        assert len(clues) == height

        solver = NumberlinkSatSolver(width, height, clues)
        result = solver.solve()

        # print(f"Satisfiable: {result.satisfiable}")
        print(result.numberOfVariable, end="\t")
        print(result.numberOfClause, end="\t")
        print(result.timeInMilisecond)

        # if (result.satisfiable):
        #     print()
        #     for row in result.result:
        #         print("".join(row))
