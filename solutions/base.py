# Base class for other solutions
import csv
import os


class InputTypes:  # pylint: disable=too-few-public-methods
    TEXT, INTEGER, TSV, ARRAY, INTARRAY, STRSPLIT, INTSPLIT = list(range(7))


ARRAY_TYPES = set(
    [InputTypes.ARRAY, InputTypes.INTARRAY, InputTypes.STRSPLIT, InputTypes.INTSPLIT]
)


def slow(func):
    def wrapper(self):
        if self.slow:
            return func(self)

        print(
            f'\nRefusing to run slow function ({func.__name__}), run again with the "--slow" flag'
        )
        return None

    return wrapper


def print_answer(i, ans):
    if ans:
        print("\n== Part {}".format(i))
        print("=== {}".format(ans))


class BaseSolution:
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

    @property
    def separator(self):
        raise NotImplementedError("explicitly define separator to use an XSPLIT method")

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

    def read_input(self, input_type):  # pylint: disable=too-many-return-statements
        # pylint: disable=bad-continuation
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

            if input_type in ARRAY_TYPES:
                file_ = file.read().strip()
                if input_type in [InputTypes.ARRAY, InputTypes.INTARRAY]:
                    separator = "\n"
                else:
                    separator = self.separator

                parts = file_.split(separator)
                if input_type in [InputTypes.INTARRAY, InputTypes.INTSPLIT]:
                    return [int(i) for i in parts]
                return parts

            raise ValueError("Unrecognized input type")

    def print_solutions(self):
        print("\n= Solutions for Day {}".format(self.number))
        res = self.solve()  # pylint: disable=assignment-from-no-return
        if res:
            for i, ans in enumerate(res):
                print_answer(i + 1, ans)
        else:
            for i in [1, 2]:
                solve_func = getattr(self, "part_{}".format(i), None)
                if solve_func:
                    print_answer(i, solve_func())  # pylint: disable=not-callable
        print()
