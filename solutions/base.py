# Base class for other solutions
import csv
import os


class InputTypes:
    TEXT, INTEGER, TSV, ARRAY, INTARRAY, STRSPLIT, INT_SPLIT = list(range(7))


def slow(func):
    def wrapper(self):
        if self.slow:
            return func(self)

        print(
            f'\nRefusing to run slow function ({func.__name__}), run again with the "--slow" flag'
        )
        return None

    return wrapper


class BaseSolution(object):
    def __init__(self, run_slow=False):
        self.input = self.read_input(self.input_type)
        self.slow = run_slow  # should run slow functions?

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

    def part_1(self):
        """
        Returns the answer for part 1 of the puzzle.
            Only needed if there's not a unified solve method.
        """

    def part_2(self):
        """
        Returns the answer for part 1 of the puzzle.
            Only needed if there's not a unified solve method.
        """

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

            if input_type == InputTypes.INTEGER:
                # a single int
                num = file.read()
                return int(num.strip())

            if input_type == InputTypes.TSV:
                reader = csv.reader(file, delimiter="\t")
                input_ = []
                for row in reader:
                    input_.append([int(i) for i in row])
                return input_

            if input_type == InputTypes.ARRAY:
                # an array, where each line is a new item
                file_ = file.read()
                return file_.strip().split("\n")

            if input_type == InputTypes.INTARRAY:
                file_ = file.read()
                arr = file_.strip().split("\n")
                return [int(i) for i in arr]

            if input_type == InputTypes.STRSPLIT:
                file_ = file.read()
                arr = file_.strip().split(",")
                return arr

            if input_type == InputTypes.INT_SPLIT:
                # a space-separated list of ints
                file_ = file.read()
                arr = file_.strip().split(" ")
                return [int(i) for i in arr]

    def print_solutions(self):
        print("\n= Solutions for Day {}".format(self.number))
        res = self.solve()  # pylint: disable=assignment-from-no-return
        if res:
            for i, ans in enumerate(res):
                self.print_answer(i + 1, ans)
        else:
            for i in [1, 2]:
                solve_func = getattr(self, "part_{}".format(i), None)
                if solve_func:
                    self.print_answer(i, solve_func())  # pylint: disable=not-callable
        print()

    def print_answer(self, i, ans):
        if ans:
            print("\n== Part {}".format(i))
            print("=== {}".format(ans))
