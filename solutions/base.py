# Base class for other solutions
import csv
import os
from enum import Enum, auto
from functools import wraps
from itertools import product
from operator import itemgetter
from pprint import pprint

# pylint: disable=no-name-in-module
# missing TypeVarTuple and Unpack
from typing import (
    Callable,
    Generic,
    Iterator,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    cast,
    final,
    overload,
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


# almost always int, but occassionally str; None is fine to disable a part
ResultType = Union[int, str, None]


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


def print_answer(i: int, ans: ResultType):
    if ans is not None:
        print(f"\n== Part {i}")
        print(f"=== {ans}")


InputType = Union[str, int, list[int], list[str], list[list[int]]]
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

    def solve(self) -> tuple[ResultType, ResultType]:
        """
        Returns a 2-tuple with the answers.
            Used instead of `part_1/2` if one set of calculations yields both answers.
        """
        return self.part_1(), self.part_2()  # type: ignore

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

    @final
    def read_input(self) -> InputType:
        with open(
            os.path.join(
                os.path.dirname(__file__),
                f"{self.year}/day_{self.day:02}/input{'.test' if self.use_test_data else ''}.txt",
            ),
        ) as file:
            if self.input_type is InputTypes.TSV:
                reader = csv.reader(file, delimiter="\t")
                return [[int(i) for i in row] for row in reader]

            data = file.read().strip()
            if not data:
                raise ValueError("input file is empty")

            if self.input_type is InputTypes.TEXT:
                return data

            if self.input_type is InputTypes.INTEGER:
                return int(data)

            if (
                self.input_type is InputTypes.STRSPLIT
                or self.input_type is InputTypes.INTSPLIT
            ):
                # default to newlines
                parts = data.split(self.separator)

                if self.input_type == InputTypes.INTSPLIT:
                    return [int(i) for i in parts]

                return parts

            raise ValueError(f"Unrecognized input_type: {self.input_type}")

    @final
    def print_solutions(self):
        print(f"\n= Solutions for {self.year} Day {self.day}")
        result = self.solve()
        # make it more resistent to solve not returning a tuple during development
        try:
            for i, p in enumerate(result or []):
                print_answer(i + 1, p)
        except TypeError:
            print_answer(0, result)
        print()

    @final
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

    @final
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


class TSVSolution(BaseSolution[list[list[int]]]):
    input_type = InputTypes.TSV


class StrSplitSolution(BaseSolution[list[str]]):
    """
    input is a str[], split by a specified separator (default newline)
        specify self.separator to tweak
    """

    input_type = InputTypes.STRSPLIT


class IntSplitSolution(BaseSolution[list[int]]):
    """
    input is a int[], split by a specified separator (default newline)
        specify self.separator to tweak
    """

    input_type = InputTypes.INTSPLIT


# https://stackoverflow.com/a/65681955/1825390
SolutionType = TypeVar("SolutionType", bound=BaseSolution)
# what the functions that @answer wraps can return
OutputType = Union[ResultType, tuple[ResultType, ResultType]]

R = TypeVar("R")  # return type generic
Ts = TypeVarTuple("Ts")  # tuple items generic


# see: https://github.com/microsoft/pyright/discussions/4317#discussioncomment-4386187
@overload
def answer(
    ans: tuple[Unpack[Ts]],
) -> Callable[
    [Callable[[SolutionType], tuple[Unpack[Ts]]]],
    Callable[[SolutionType], tuple[Unpack[Ts]]],
]:
    ...


@overload
def answer(
    ans: R,
) -> Callable[[Callable[[SolutionType], R]], Callable[[SolutionType], R]]:
    ...


def answer(
    ans: R,
) -> Callable[[Callable[[SolutionType], R]], Callable[[SolutionType], R]]:
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

    def deco(func: Callable[[SolutionType], R]):
        @wraps(func)
        # uses `self` because that's what's passed to the original solution function
        def wrapper(self: SolutionType):
            result = func(self)
            # only assert the answer for non-test data
            if not self.use_test_data:
                assert result == ans, f"expected {result=} to equal {ans=}"
            return result

        return wrapper

    return deco


GridPoint = tuple[int, int]
DIRECTIONS = sorted(product((-1, 0, 1), repeat=2), key=itemgetter(1))


def neighbors(
    center: GridPoint,
    num_directions=8,
    *,
    ignore_negatives: bool = False,
    max_size: int = 0,
    max_x_size: int = 0,
    max_y_size: int = 0,
) -> Iterator[tuple[int, int]]:
    """
    given a point (2-tuple) it yields each neighboring point.
    Iterates from top left to bottom right, skipping any points as described below:

    * `num_directions`: Can get cardinal directions (4), include diagonals (8), or include self (9)
    * `ignore_negatives`: skips points where either value is less than 0
    * `max_DIM_size`: if specified, skips points where the dimension value is greater than the max grid size in that dimension. If doing a 2D-List based (aka `(row,col)` grid) rather than a pure `(x,y)` grid, the max values should be `len(DIM) - 1`. Is mutually exclusive with `max_size`.

    For a 2D list-based grid, neighbors will come out in (row, col) format.
    """
    assert num_directions in {4, 8, 9}
    # one or the other
    if max_size:
        assert not (max_x_size or max_y_size)
    if max_x_size or max_y_size:
        assert not max_size

    for dx, dy in DIRECTIONS:
        if num_directions == 4 and dx and dy:
            # diagonal; skip
            continue

        if num_directions != 9 and not (dx or dy):
            # skip self
            continue

        rx = center[0] + dx
        ry = center[1] + dy

        if ignore_negatives and (rx < 0 or ry < 0):
            continue

        if max_size and (rx > max_size or ry > max_size):
            continue

        if max_x_size and (rx > max_x_size):
            continue

        if max_y_size and (ry > max_y_size):
            continue

        yield (rx, ry)
