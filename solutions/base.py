# Base class for other solutions
import os


class InputTypes(object):
    TEXT, INTEGER, TSV, ARRAY, INTARRAY, STRSPLIT, INT_SPLIT = list(range(7))


def slow(f):
    def wrapper(self):
        if self.slow:
            return f(self)
        else:
            print(
                f'\nRefusing to run slow function ({f.__name__}), run again with the "--slow" flag'
            )

    return wrapper


class BaseSolution(object):
    def __init__(self, slow=False):
        self.input = self.read_input(self.input_type)
        self.slow = slow  # should run slow functions?

    @property
    def input_type(self):
        return InputTypes.TEXT

    @property
    def year(self):
        raise NotImplementedError("explicitly define year")

    @property
    def number(self):
        raise NotImplementedError("explicitly define number")

    def solve(self):
        """
        Returns a 2-tuple with the answers
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

            elif input_type == InputTypes.INT_SPLIT:
                # a space-separated list of ints
                f = file.read()
                arr = f.strip().split(" ")
                return [int(i) for i in arr]

    def print_solutions(self):
        print("\n= Solutions for Day {}".format(self.number))
        res = self.solve()
        if res:
            for i, ans in enumerate(res):
                self.print_answer(i + 1, ans)
        else:
            for i in [1, 2]:
                solve_func = getattr(self, "part_{}".format(i), None)
                if solve_func:
                    self.print_answer(i, solve_func())
        print()

    def print_answer(self, i, ans):
        if ans:
            print("\n== Part {}".format(i))
            print("=== {}".format(ans))
