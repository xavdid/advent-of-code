# Base class for other solutions
import csv
import os
from enum import Enum, auto
from pprint import pprint
from typing import Generic, List, TypeVar, Union, cast


class InputTypes(Enum):  # pylint: disable=too-few-public-methods
    # one solid block of text; the default
    TEXT = auto()
    # a single int
    INTEGER = auto()
    # tab-separated values.
    TSV = auto()
    # str[], split by a specified separator (default newline)
    STRSPLIT = auto()
    # int[], split by a split by a specified separator (default newline)
    INTSPLIT = auto()


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
        print(f"\n== Part {i}")
        print(f"=== {ans}")


InputType = Union[str, int, List[int], List[str]]
I = TypeVar("I", bound=InputType)


class BaseSolution(Generic[I]):
    separator = "\n"

    # Solution Subclasses define these
    # this uses `TEXT` as a default for backwards compatibility
    input_type: InputTypes = InputTypes.TEXT
    _year: int
    _number: int

    def __init__(self, run_slow=False, debug=False):
        self.input = cast(I, self.read_input())
        self.slow = run_slow  # should run slow functions?
        self.debug = debug

    @property
    def year(self):
        if not hasattr(self, "_year"):
            raise NotImplementedError("explicitly define year")
        return self._year

    @property
    def number(self):
        if not hasattr(self, "_number"):
            raise NotImplementedError("explicitly define number")
        return self._number

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

    def read_input(self) -> InputType:
        with open(
            os.path.join(
                os.path.dirname(__file__), f"{self.year}/day_{self.number}/input.txt"
            ),
        ) as file:
            if self.input_type is InputTypes.TEXT:
                return file.read().strip()

            if self.input_type is InputTypes.INTEGER:
                num = file.read()
                return int(num.strip())

            if self.input_type is InputTypes.TSV:
                reader = csv.reader(file, delimiter="\t")
                input_ = []
                for row in reader:
                    input_.append([int(i) for i in row])
                return input_

            if (
                self.input_type is InputTypes.STRSPLIT
                or self.input_type is InputTypes.INTSPLIT
            ):
                file_ = file.read().strip()
                # default to newlines
                parts = file_.split(self.separator)

                if self.input_type == InputTypes.INTSPLIT:
                    return [int(i) for i in parts]

                return parts

            raise ValueError(f"Unrecognized input_type: {self.input_type}")

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


class TextSolution(BaseSolution[str]):
    input_type = InputTypes.TEXT


class IntSolution(BaseSolution[int]):
    input_type = InputTypes.INTEGER


class StrSplitSolution(BaseSolution[List[str]]):
    input_type = InputTypes.STRSPLIT


class IntSplitSolution(BaseSolution[List[int]]):
    input_type = InputTypes.INTSPLIT
