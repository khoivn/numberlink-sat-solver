from pysat.solvers import Glucose3
import time


class NumberlinkSatSolver:
    # class Direction:
    #     LEFT = 1
    #     RIGHT = 2
    #     UP = 3
    #     DOWN = 4

    def __init__(self, width: int, height: int, clues: [[]]):
        self.width = width
        self.height = height
        self.clues = clues
        self.characters = sorted(
            list(set([item for sublist in clues for item in sublist if item is not None and item.strip() != ''])))
        self.charNumber = len(self.characters)
        self.clauses = []

    # def convertDirection(self, i: int, j: int, direction: int):
    #     return (i - 1) * 4 * self.width + (j - 1) * 4 + direction

    def convertLabel(self, i: int, j: int, character: str):
        charIndex = self.characters.index(character) + 1
        return (i - 1) * self.width * self.charNumber + (j - 1) * self.charNumber + charIndex

    def exactOneConstraint(self, variables: []):
        self.clauses.append(variables)
        for i in range(len(variables) - 1):
            for j in range(i + 1, len(variables)):
                self.clauses.append([-variables[i], -variables[j]])

    def exactTwoConstraint(self, variables: []):
        if len(variables) == 4:
            return self.exactTwoAmongFourConstraint(variables)
        elif len(variables) == 3:
            return self.exactTwoAmongThreeConstraint(variables)
        elif len(variables) == 2:
            return self.exactTwoAmongTwoConstraint(variables)
        return []

    def exactTwoAmongFourConstraint(self, variables: []):
        clauses = []
        for i in range(len(variables) - 2):
            for j in range(i + 1, len(variables) - 1):
                for k in range(j + 1, len(variables)):
                    clauses.append([variables[i], variables[j], variables[k]])
                    clauses.append([-variables[i], -variables[j], -variables[k]])
        return clauses

    def exactTwoAmongThreeConstraint(self, variables: []):
        clauses = []
        for i in range(len(variables) - 1):
            for j in range(i + 1, len(variables)):
                clauses.append([variables[i], variables[j]])
        clauses.append([-v for v in variables])
        return clauses

    def exactTwoAmongTwoConstraint(self, variables: []):
        clauses = []
        for v in variables:
            clauses.append([v])
        return clauses

    def isNumbered(self, i: int, j: int):
        cell = self.clues[i - 1][j - 1]
        return cell is not None and cell.strip() != ''

    # def addClausesWithDirectionConstraint(self):
    #     for i in range(1, self.height + 1):
    #         for j in range(1, self.width + 1):
    #             variables = [self.convertDirection(i, j, self.Direction.LEFT),
    #                          self.convertDirection(i, j, self.Direction.RIGHT),
    #                          self.convertDirection(i, j, self.Direction.UP),
    #                          self.convertDirection(i, j, self.Direction.DOWN)]
    #             if (self.isNumbered(i, j)):
    #                 self.exactOneConstraint(variables)
    #             else:
    #                 self.exactTwoAmongFourConstraint(variables)
    #             if (i == 1):
    #                 self.clauses.append([-self.convertDirection(i, j, self.Direction.UP)])
    #             if (i == self.height):
    #                 self.clauses.append([-self.convertDirection(i, j, self.Direction.DOWN)])
    #             if (j == 1):
    #                 self.clauses.append([-self.convertDirection(i, j, self.Direction.LEFT)])
    #             if (j == self.width):
    #                 self.clauses.append([-self.convertDirection(i, j, self.Direction.RIGHT)])

    def addClausesWithLabelInCellConstraint(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                variables = [self.convertLabel(i, j, character) for character in self.characters]
                self.exactOneConstraint(variables)

    def findAdjacents(self, i: int, j: int, character: str):
        variables = []
        if j > 1:
            variables.append(self.convertLabel(i, j - 1, character))
        if j < self.width:
            variables.append(self.convertLabel(i, j + 1, character))
        if i > 1:
            variables.append(self.convertLabel(i - 1, j, character))
        if i < self.height:
            variables.append(self.convertLabel(i + 1, j, character))
        return variables

    def addClausesWithLinkConstraint(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.isNumbered(i, j):
                    character = self.clues[i - 1][j - 1]
                    variables = self.findAdjacents(i, j, character)
                    self.exactOneConstraint(variables)
                    continue
                for character in self.characters:
                    self.clauses += [[-self.convertLabel(i, j, character)] + clause for clause in
                                     self.exactTwoConstraint(self.findAdjacents(i, j, character))]

    def addClausesWithClues(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.isNumbered(i, j):
                    self.clauses.append([self.convertLabel(i, j, self.clues[i - 1][j - 1])])

    def satSolving(self):
        g = Glucose3()

        for c in self.clauses:
            g.add_clause(c)

        satisfiable = g.solve()
        if not satisfiable:
            return None, satisfiable

        result = g.get_model()
        result = [self.characters[next(k + 1 for k, l in enumerate(result[i:i + self.charNumber]) if l > 0) - 1] for i
                  in range(0, len(result), self.charNumber)]
        result = [result[i:i + self.width] for i in range(0, len(result), self.width)]
        new_result = []
        for i, row in enumerate(result):
            new_row = []
            next_row = result[i + 1] if i < self.height - 1 else None
            prev_row = result[i - 1] if i > 0 else None
            for j, cell in enumerate(row):
                right_cell = row[j + 1] if j < self.width - 1 else None
                left_cell = row[j - 1] if j > 0 else None
                top_cell = prev_row[j] if prev_row != None else None
                bottom_cell = next_row[j] if next_row != None else None
                new_cell = "─" if cell == left_cell and cell == right_cell else \
                    "┘" if cell == left_cell and cell == top_cell else \
                        "┐" if cell == left_cell and cell == bottom_cell else \
                            "└" if cell == right_cell and cell == top_cell else \
                                "┌" if cell == right_cell and cell == bottom_cell else \
                                    "│" if cell == top_cell and cell == bottom_cell else cell
                new_row.append(new_cell)
            new_result.append(new_row)
        return new_result, satisfiable

    def solve(self):
        startTime = time.time()
        self.addClausesWithLabelInCellConstraint()
        self.addClausesWithLinkConstraint()
        self.addClausesWithClues()
        numberOfClause = len(self.clauses)

        result, satisfiable = self.satSolving()
        stopTime = time.time()
        return Result(satisfiable, result, self.width * self.height * self.charNumber, numberOfClause,
                      (stopTime - startTime) * 1000)


class Result:
    def __init__(self, satisfiable: bool, result: [[]], numberOfVariable: int, numberOfClause: int,
                 timeInMilisecond: float):
        self.satisfiable = satisfiable
        self.result = result
        self.numberOfVariable = numberOfVariable
        self.numberOfClause = numberOfClause
        self.timeInMilisecond = timeInMilisecond
