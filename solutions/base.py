# Base class for other solutions
import csv
import os
from enum import Enum, auto
from pprint import pprint


class InputTypes(Enum):  # pylint: disable=too-few-public-methods
    TEXT = auto()  # one solid block of text; the default
    INTEGER = auto()  # a single int
    TSV = auto()  # tab-separated values.
    STRSPLIT = auto()  # str[], split by a specified separator (default newline)
    INTSPLIT = (
        auto()
    )  # int[], split by a split by a specified separator (default newline)


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
    if ans is not None:
        print("\n== Part {}".format(i))
        print("=== {}".format(ans))


class BaseSolution:
    input_type = InputTypes.TEXT
    separator = "\n"

    def __init__(self, run_slow=False, debug=False):
        self.input = self.read_input(self.input_type)
        self.slow = run_slow  # should run slow functions?
        self.debug = debug

    @property
    def year(self):
        raise NotImplementedError("explicitly define year")

    @property
    def number(self):
        raise NotImplementedError("explicitly define number")

    def solve(self):
        """
        Returns a 2-tuple with the answers.
            Used instead of `part_1/2` if one set of calculations yields both answers.
        """

    def part_1(self):
        """
        Returns the answer for part 1 of the puzzle.
            Only needed if there's not a unified solve method.
        """

    def part_2(self):
        """
        Returns the answer for part 2 of the puzzle.
            Only needed if there's not a unified solve method.
        """

    def read_input(self, input_type):  # pylint: disable=too-many-return-statements
        with open(
            os.path.join(
                os.path.dirname(__file__), f"{self.year}/day_{self.number}/input.txt"
            )
        ) as file:
            if input_type == InputTypes.TEXT:
                return file.read().strip()

            if input_type == InputTypes.INTEGER:
                num = file.read()
                return int(num.strip())

            if input_type == InputTypes.TSV:
                reader = csv.reader(file, delimiter="\t")
                input_ = []
                for row in reader:
                    input_.append([int(i) for i in row])
                return input_

            if input_type in {InputTypes.STRSPLIT, InputTypes.INTSPLIT}:
                file_ = file.read().strip()
                # default to newlines
                parts = file_.split(self.separator)

                if input_type == InputTypes.INTSPLIT:
                    return [int(i) for i in parts]

                return parts

            raise ValueError("Unrecognized input type")

    def print_solutions(self):
        print(f"\n= Solutions for {self.year} Day {self.number}")
        res = self.solve()  # pylint: disable=assignment-from-no-return
        if res:
            for index, ans in enumerate(res):
                print_answer(index + 1, ans)
        else:
            for index in [1, 2]:
                solve_func = getattr(self, f"part_{index}", None)
                if solve_func:
                    print_answer(index, solve_func())  # pylint: disable=not-callable
        print()

    def pp(self, *obj, newline=False):
        if self.debug:
            for o in obj:
                if hasattr(o, "pretty"):
                    print(o.pretty())
                elif isinstance(o, str):
                    print(o)
                else:
                    pprint(o)
            if newline:
                print()

    def newline(self):
        if self.debug:
            print()
