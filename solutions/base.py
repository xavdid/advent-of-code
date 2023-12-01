"""
This is the Base class, which handles basic input parsing and answer verification.

See README.md for how to use it; you shouldn't need to edit it directly.

If something in here is giving you trouble, please file an issue:

https://github.com/xavdid/advent-of-code-python-template/issues
"""

from enum import Enum, auto
from functools import wraps
from pathlib import Path
from pprint import pprint
from typing import (
    Callable,
    Generic,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    cast,
    final,
    overload,
)


class AoCException(Exception):
    """
    custom error class for issues related to creating/running solutions
    """

    pass


class InputTypes(Enum):
    # one solid block of text; the default
    TEXT = auto()
    # a single int
    INTEGER = auto()
    # str[], split by a specified separator (default newline)
    STRSPLIT = auto()
    # int[], split by a split by a specified separator (default newline)
    INTSPLIT = auto()


# almost always int, but occasionally str; None is fine to disable a part
ResultType = Union[int, str, None]


def print_answer(i: int, ans: ResultType):
    if ans is not None:
        print(f"\n== Part {i}")
        print(f"=== {ans}")


InputType = Union[str, int, list[int], list[str], list[list[int]]]
I = TypeVar("I", bound=InputType)


class BaseSolution(Generic[I]):
    separator = "\n"

    # Solution Subclasses define these
    input_type: InputTypes = InputTypes.TEXT
    _year: int
    _day: int

    def __init__(self, run_slow=False, is_debugging=False, use_test_data=False):
        self.slow = run_slow  # should run slow functions?
        self.is_debugging = is_debugging
        self.use_test_data = use_test_data

        self.input = cast(I, self.read_input())

    @property
    def year(self):
        if not hasattr(self, "_year"):
            raise NotImplementedError("explicitly define Solution._year")
        return self._year

    @property
    def day(self):
        if not hasattr(self, "_day"):
            raise NotImplementedError("explicitly define Solution._day")
        return self._day

    def solve(self) -> tuple[ResultType, ResultType]:
        """
        Returns a 2-tuple with the answers.
            Used instead of `part_1/2` if one set of calculations yields both answers.
        """
        return self.part_1(), self.part_2()

    def part_1(self):
        """
        Returns the answer for part 1 of the puzzle. Only needed if there's not a unified solve method.
        """

    def part_2(self):
        """
        Returns the answer for part 2 of the puzzle. Only needed if there's not a unified solve method.
        """

    @final
    def read_input(self) -> InputType:
        """
        handles locating, reading, and parsing input files
        """
        input_file = Path(
            # __file__ is the solution base
            Path(__file__).parent,
            # the 4-digit year
            str(self.year),
            # padded day folder
            f"day_{self.day:02}",
            # either the real input or the test input
            f"input{'.test' if self.use_test_data else ''}.txt",
        )
        if not input_file.exists():
            raise AoCException(
                f'Failed to find an input file at path "./{input_file.relative_to(Path.cwd())}". You can run `./start --year {self.year} {self.day}` to create it.'
            )

        data = input_file.read_text().strip("\n")

        if not data:
            raise AoCException(
                f'Found a file at path "./{input_file.relative_to(Path.cwd())}", but it was empty. Make sure to paste some input!'
            )

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
    def run_and_print_solutions(self):
        result = self.solve()
        print(f"= Solutions for {self.year} Day {self.day}")
        try:
            if result:
                p1, p2 = result
                print_answer(1, p1)
                print_answer(2, p2)
            print()
        except TypeError as exc:
            raise ValueError(
                "unable to unpack 2-tuple from `solve`, got", result
            ) from exc

    @final
    def debug(self, *objects, trailing_newline=False):
        """
        helpful debugging utility. Does nothing if `./advent` isn't passed the --debug flag

        Takes any number of objects and pretty-prints them. Can add a trailing newline to create separation between blocks
        """
        if not self.is_debugging:
            return

        for o in objects:
            pprint(o)

        if trailing_newline:
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


class StrSplitSolution(BaseSolution[list[str]]):
    """
    input is a str[], split by a specified separator (default newline); specify self.separator to tweak
    """

    input_type = InputTypes.STRSPLIT


class IntSplitSolution(BaseSolution[list[int]]):
    """
    input is a int[], split by a specified separator (default newline); specify self.separator to tweak
    """

    input_type = InputTypes.INTSPLIT


# https://stackoverflow.com/a/65681955/1825390
SolutionClassType = TypeVar("SolutionClassType", bound=BaseSolution)
# what the functions that @answer wraps can return
OutputType = Union[ResultType, tuple[ResultType, ResultType]]


def slow(
    func: Callable[[SolutionClassType], OutputType]
) -> Callable[[SolutionClassType], OutputType]:
    """
    A decorator for solution methods that blocks their execution (and returns without error)
    if the the function is manually marked as "slow". Helpful if running many solutions at once,
    so one doesn't gum up the whole thing.
    """

    def wrapper(self: SolutionClassType):
        if self.slow or self.use_test_data:
            return func(self)

        print(
            f"\nRefusing to run slow function ({func.__name__}). "
            "Run `./advent` again with the `--slow` flag."
        )
        return None

    return wrapper


# these types ensure the return type of the function matches `@answer`
# see: https://github.com/microsoft/pyright/discussions/4317#discussioncomment-4386187
R = TypeVar("R")  # return type generic
Ts = TypeVarTuple("Ts")  # tuple items generic


@overload
def answer(
    expected: tuple[Unpack[Ts]],
) -> Callable[
    [Callable[[SolutionClassType], tuple[Unpack[Ts]]]],
    Callable[[SolutionClassType], tuple[Unpack[Ts]]],
]:
    ...


@overload
def answer(
    expected: R,
) -> Callable[[Callable[[SolutionClassType], R]], Callable[[SolutionClassType], R]]:
    ...


def answer(
    expected: R,
) -> Callable[[Callable[[SolutionClassType], R]], Callable[[SolutionClassType], R]]:
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

    def deco(func: Callable[[SolutionClassType], R]):
        @wraps(func)
        # uses `self` because that's what's passed to the original solution function
        def wrapper(self: SolutionClassType):
            result = func(self)
            # only assert the answer for non-test data
            if not self.use_test_data and result is not None:
                if result != expected:
                    _, year, day, _ = self.__module__.split(".")
                    raise AoCException(
                        f"Failed @answer assertion for {year} / {day} / {func.__name__}:\n  returned: {result}\n  expected: {expected}"
                    )
            return result

        return wrapper

    return deco
