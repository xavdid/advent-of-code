# Base class for other solutions
import os


class InputTypes(object):
    TEXT, INTEGER, TSV, ARRAY, INTARRAY, STRSPLIT = list(range(6))


class BaseSolution(object):
    def __init__(self, number, load_input=True):
        self.number = number
        if load_input:
            self.input = self.read_input(self.input_type)

    @property
    def input_type(self):
        return InputTypes.TEXT

    @property
    def year(self):
        raise NotImplementedError("explicitly define year")

    def solve(self):
        """
        Returns a 2-tuple with each answer
        """
        pass

    def part_1(self):
        """
        Returns the answer for part 1 of the puzzle.
            Only needed if there's not a unified solve method.
        """
        pass

    def part_2(self):
        """
        Returns the answer for part 1 of the puzzle.
            Only needed if there's not a unified solve method.
        """
        pass

    def read_input(self, input_type):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "{}/inputs/{}.txt".format(self.year, self.number),
            )
        ) as file:
            if input_type == InputTypes.TEXT:
                # one solid block of text
                return file.read()

            elif input_type == InputTypes.INTEGER:
                # a single int
                i = file.read()
                return int(i.strip())

            elif input_type == InputTypes.TSV:
                import csv

                reader = csv.reader(file, delimiter="\t")
                input_ = []
                for row in reader:
                    input_.append([int(i) for i in row])
                return input_

            elif input_type == InputTypes.ARRAY:
                # an array, where each line is a new item
                f = file.read()
                return f.strip().split("\n")

            elif input_type == InputTypes.INTARRAY:
                f = file.read()
                arr = f.strip().split("\n")
                return [int(i) for i in arr]

            elif input_type == InputTypes.STRSPLIT:
                f = file.read()
                arr = f.strip().split(",")
                return arr

    def print_solutions(self):
        print("= Solutions for Day {}".format(self.number))
        res = self.solve()
        if res:
            for i, ans in enumerate(res):
                self.print_answer(i + 1, ans)
        else:
            for i in [1, 2]:
                solve_func = getattr(self, "part_{}".format(i), None)
                if solve_func:
                    self.print_answer(i, solve_func())

    def print_answer(self, i, ans):
        if ans:
            print("\n== Part {}".format(i))
            print("=== {}".format(ans))
