from pysat.solvers import Glucose3
import time


class NumberlinkSatSolver:
    class Direction:
        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4

    def __init__(self, width: int, height: int, clues: [[]]):
        self.width = width
        self.height = height
        self.clues = clues
        self.characters = sorted(
            list(set([item for sublist in clues for item in sublist if item is not None and item.strip() != ''])))
        self.charNumber = len(self.characters)
        self.clauses = []

    def convertDirection(self, i: int, j: int, direction: int):
        return (i - 1) * 4 * self.width + (j - 1) * 4 + direction

    def convertLabel(self, i: int, j: int, character):
        charIndex = self.characters.index(character) + 1
        return self.width * self.height * 4 + (i - 1) * self.width * self.charNumber + (
                j - 1) * self.charNumber + charIndex

    def exactOneConstraint(self, variables: []):
        self.clauses.append(variables)
        for i in range(len(variables) - 1):
            for j in range(i + 1, len(variables)):
                self.clauses.append([-variables[i], -variables[j]])

    def exactTwoAmongFourConstraint(self, variables: []):
        for i in range(len(variables) - 2):
            for j in range(i + 1, len(variables) - 1):
                for k in range(j + 1, len(variables)):
                    self.clauses.append([variables[i], variables[j], variables[k]])

        for i in range(len(variables) - 2):
            for j in range(i + 1, len(variables) - 1):
                for k in range(j + 1, len(variables)):
                    self.clauses.append([-variables[i], -variables[j], -variables[k]])

    def isNumbered(self, i: int, j: int):
        cell = self.clues[i - 1][j - 1]
        return cell is not None and cell.strip() != ''

    def addClausesWithDirectionConstraint(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                variables = [self.convertDirection(i, j, self.Direction.LEFT),
                             self.convertDirection(i, j, self.Direction.RIGHT),
                             self.convertDirection(i, j, self.Direction.UP),
                             self.convertDirection(i, j, self.Direction.DOWN)]
                if (self.isNumbered(i, j)):
                    self.exactOneConstraint(variables)
                else:
                    self.exactTwoAmongFourConstraint(variables)
                if (i == 1):
                    self.clauses.append([-self.convertDirection(i, j, self.Direction.UP)])
                if (i == self.height):
                    self.clauses.append([-self.convertDirection(i, j, self.Direction.DOWN)])
                if (j == 1):
                    self.clauses.append([-self.convertDirection(i, j, self.Direction.LEFT)])
                if (j == self.width):
                    self.clauses.append([-self.convertDirection(i, j, self.Direction.RIGHT)])

    def addClausesWithLabelInCellConstraint(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                variables = [self.convertLabel(i, j, character) for character in self.characters]
                self.exactOneConstraint(variables)

    def addClausesWithLinkConstraint(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                for character in self.characters:
                    if (j > 1):
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.LEFT),
                             self.convertLabel(i, j - 1, character)])
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.LEFT),
                             self.convertDirection(i, j - 1, self.Direction.RIGHT)])
                    if j < self.width:
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.RIGHT),
                             self.convertLabel(i, j + 1, character)])
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.RIGHT),
                             self.convertDirection(i, j + 1, self.Direction.LEFT)])
                    if i > 1:
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.UP),
                             self.convertLabel(i - 1, j, character)])
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.UP),
                             self.convertDirection(i - 1, j, self.Direction.DOWN)])
                    if i < self.height:
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.DOWN),
                             self.convertLabel(i + 1, j, character)])
                        self.clauses.append(
                            [-self.convertLabel(i, j, character), -self.convertDirection(i, j, self.Direction.DOWN),
                             self.convertDirection(i + 1, j, self.Direction.UP)])

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
        result = result[:self.width * self.height * 4]
        result = ["─" if result[i] > 0 and result[i + 1] > 0 else
                  "┘" if (result[i] > 0 and result[i + 2] > 0) else
                  "┐" if (result[i] > 0 and result[i + 3] > 0) else
                  "└" if (result[i + 1] > 0 and result[i + 2] > 0) else
                  "┌" if (result[i + 1] > 0 and result[i + 3] > 0) else
                  "│" if (result[i + 2] > 0 and result[i + 3] > 0) else
                  None

                  for i in range(0, len(result), 4)]

        result = [result[i:i + self.width] for i in range(0, len(result), self.width)]
        result = [[result[i][j] if result[i][j] is not None else self.clues[i][j] for j, col in enumerate(row)]
                  for i, row in enumerate(result)]
        return result, satisfiable

    def solve(self):
        startTime = time.time()
        self.addClausesWithDirectionConstraint()
        self.addClausesWithLabelInCellConstraint()
        self.addClausesWithLinkConstraint()
        self.addClausesWithClues()
        numberOfClause = len(self.clauses)

        result, satisfiable = self.satSolving()
        stopTime = time.time()
        return Result(satisfiable, result, self.width * self.height * (4 + self.charNumber), numberOfClause,
                      (stopTime - startTime) * 1000)


class Result:
    def __init__(self, satisfiable: bool, result: [[]], numberOfVariable: int, numberOfClause: int,
                 timeInMilisecond: float):
        self.satisfiable = satisfiable
        self.result = result
        self.numberOfVariable = numberOfVariable
        self.numberOfClause = numberOfClause
        self.timeInMilisecond = timeInMilisecond
