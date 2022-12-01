# Base class for other solutions
import csv
import os
from enum import Enum, auto
from functools import wraps
from itertools import product
from operator import itemgetter
from pprint import pprint
from typing import (
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)


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
            f"\nRefusing to run slow function ({func.__name__}). "
            "Run `./advent` again with the `--slow` flag."
        )
        return None

    return wrapper


def print_answer(i: int, ans: int):
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
    _day: int

    def __init__(self, run_slow=False, debug=False, use_test_data=False):
        self.slow = run_slow  # should run slow functions?
        self.debug = debug
        self.use_test_data = use_test_data
        self.input = cast(I, self.read_input())
        if not self.input:
            raise ValueError(
                f"err, didn't read any input for {'test' if use_test_data else 'normal'} mode"
            )

    @property
    def year(self):
        if not hasattr(self, "_year"):
            raise NotImplementedError("explicitly define year")
        return self._year

    @property
    def day(self):
        if not hasattr(self, "_day"):
            raise NotImplementedError("explicitly define number")
        return self._day

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
                os.path.dirname(__file__),
                f"{self.year}/day_{self.day:02}/input{'.test' if self.use_test_data else ''}.txt",
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
        print(f"\n= Solutions for {self.year} Day {self.day}")
        res = self.solve()  # pylint: disable=assignment-from-no-return
        if res:
            for index, ans in enumerate(res):
                print_answer(index + 1, ans)
        else:
            for index in [1, 2]:
                solve_func = cast(
                    Optional[Callable[[], int]], getattr(self, f"part_{index}", None)
                )
                if solve_func:
                    print_answer(index, solve_func())
        print()

    def pp(self, *obj, newline=False):
        if self.debug:
            for o in obj:
                # custom printing for objects
                if hasattr(o, "pretty"):
                    print(o.pretty())
                elif isinstance(o, str):
                    print(o, end=" " if len(obj) > 1 else None)
                else:
                    pprint(o)
            if newline:
                print()

    def newline(self):
        if self.debug:
            print()


class TextSolution(BaseSolution[str]):
    """
    input is one solid block of text; the default
    """

    input_type = InputTypes.TEXT


class IntSolution(BaseSolution[int]):
    """
    input is a single int
    """

    input_type = InputTypes.INTEGER


class TSVSolution(BaseSolution[List[int]]):
    input_type = InputTypes.TSV


class StrSplitSolution(BaseSolution[List[str]]):
    """
    input is a str[], split by a specified separator (default newline)
        specify self.separator to tweak
    """

    input_type = InputTypes.STRSPLIT


class IntSplitSolution(BaseSolution[List[int]]):
    """
    input is a int[], split by a specified separator (default newline)
        specify self.separator to tweak
    """

    input_type = InputTypes.INTSPLIT


def answer(ans: Union[int, Tuple[int, int]]):
    """
    Decorator to assert the result of the function is a certain thing.
    This is specifically designed to be used on instance methods of BaseSolution.
    It only throws errors when _not_ using test data.

    Usage:
    ```py
    @answer(3)
    def f(i):
        return i

    f(1) # throws
    f(3) # returns 3 like normal
    ```
    """

    def deco(func):
        @wraps(func)
        # uses `self` because that's what's passed to the original solution function
        def wrapper(self: BaseSolution):
            result = func(self)
            # only assert the answer for non-test data
            if not self.use_test_data:
                assert result == ans, f"expected {result=} to equal {ans=}"
            return result

        return wrapper

    return deco


GridPoint = Tuple[int, int]
DIRECTIONS = sorted(product((-1, 0, 1), repeat=2), key=itemgetter(1))


def neighbors(
    center: GridPoint,
    num_directions=8,
    *,
    ignore_negatives: bool = False,
    max_size: int = 0,
) -> Iterator[Tuple[int, int]]:
    """
    given a point (2-tuple) it yields each neighboring point. Iterates from top left to bottom right, skipping any points as described below:

    * `num_directions`: Can get cardinal directions (4), include diagonals (8), or include self (9)
    * `ignore_negatives`: skips points where either value is less than 0
    * `max_size`: skips points where either value is greater than the max grid size. Currently assumes a square grid
    """
    assert num_directions in [4, 8, 9]

    for dx, dy in DIRECTIONS:
        if num_directions == 4 and dx and dy:
            # diagonal; skip
            continue

        if num_directions == 8 and not (dx or dy):
            # skip self
            continue

        rx = center[0] + dx
        ry = center[1] + dy

        if ignore_negatives and (rx < 0 or ry < 0):
            continue

        if max_size and (rx > max_size or ry > max_size):
            continue

        yield (rx, ry)
