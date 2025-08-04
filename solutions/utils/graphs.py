from enum import IntEnum
from itertools import product
from operator import itemgetter
from typing import Iterator, Literal, NamedTuple, Optional, overload

type GridPoint = tuple[int, int]
type Grid = dict[GridPoint, str]
type IntGrid = dict[GridPoint, int]

OFFSETS = sorted(product((-1, 0, 1), repeat=2), key=itemgetter(1))


def neighbors(
    center: GridPoint,
    num_directions=8,
    *,
    max_size: Optional[int] = None,
    max_x_size: Optional[int] = None,
    max_y_size: Optional[int] = None,
    diagonals=False,
    ignore_negatives=False,  # ignored, will remove
) -> Iterator[tuple[int, int]]:
    """
    given a point (2-tuple) it yields each neighboring point.
    Iterates from top left to bottom right, skipping any points as described below:

    * `num_directions`: Can get cardinal directions (4), include diagonals (8), or include self (9)
    * `ignore_negatives`: skips points where either value is less than 0
    * `diagonals`: only returns corners; only valid if supplied with `num_directions == 4`
    * `max_DIM_size`: if specified, skips points where the dimension value is greater than the max grid size in that dimension. If doing a 2D-List based (aka `(row,col)` grid) rather than a pure `(x,y)` grid, the max values should be `len(DIM) - 1`. Is mutually exclusive with `max_size`. Upper bounds imply a lower bound of 0.

    For a 2D list-based grid, neighbors will come out in (row, col) format.
    """
    assert num_directions in {4, 8, 9}
    if diagonals:
        assert num_directions == 4, "diagonals can only be used in 4-directional mode"

    # one or the other
    if max_size:
        assert not (max_x_size or max_y_size), "specify only max_size OR max_DIM_size"
    if max_x_size or max_y_size:
        assert not max_size, "specify only max_size OR max_DIM_size"

    is_bounded = max_size or max_x_size or max_y_size

    for offset_x, offset_y in OFFSETS:
        if diagonals and not (offset_x and offset_y):
            continue

        if num_directions == 4 and not diagonals and offset_x and offset_y:
            # diagonal; skip
            continue

        if num_directions != 9 and not (offset_x or offset_y):
            # skip self
            continue

        next_x, next_y = add_points(center, (offset_x, offset_y))

        if is_bounded and (next_x < 0 or next_y < 0):
            continue

        if max_size and (next_x > max_size or next_y > max_size):
            continue

        if max_x_size and (next_x > max_x_size):
            continue

        if max_y_size and (next_y > max_y_size):
            continue

        yield (next_x, next_y)


@overload
def parse_grid(raw_grid: list[str]) -> Grid: ...
@overload
def parse_grid(raw_grid: list[str], *, ignore_chars: str) -> Grid: ...
@overload
def parse_grid(
    raw_grid: list[str], *, int_vals: Literal[True], ignore_chars: str = ""
) -> IntGrid: ...
@overload
def parse_grid(
    raw_grid: list[str], *, int_vals: Literal[False], ignore_chars: str = ""
) -> Grid: ...


def parse_grid(
    raw_grid: list[str], *, int_vals: bool = False, ignore_chars: str = ""
) -> Grid | IntGrid:
    """
    returns 2-tuples of (row, col) with their value. Values are `str` by default, but can be ints with `int_vals=True`.

    `ignore_chars` is for grid characters that aren't valid landing spots, like walls.

    ```
    (0, 0) ------> (0, 9)
      |              |
      |              |
      |              |
      |              |
      V              V
    (9, 0) ------> (9, 9)
    ```
    """
    result = {}
    ignore = set(ignore_chars)

    for row, line in enumerate(raw_grid):
        for col, c in enumerate(line):
            if c in ignore:
                continue

            val = int(c) if int_vals else c

            result[row, col] = val

    return result


def add_points(a: GridPoint, b: GridPoint) -> GridPoint:
    """
    add a pair of 2-tuples together. Useful for calculating a new position from a location and an offset
    """
    return a[0] + b[0], a[1] + b[1]


def subtract_points(a: GridPoint, b: GridPoint) -> GridPoint:
    """
    returns `b - a` for 2-tuples. Useful for getting offset from neighbors.
    """
    return a[0] - b[0], a[1] - b[1]


def taxicab_distance(a: GridPoint, b: GridPoint) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


Rotation = Literal["CCW", "CW"]


class Direction(IntEnum):
    """
    A small class to help manage facing a direction on a grid.

    Initialize it facing a direction. Then you can rotate and get the offset that you'd use to step in that direction.

    ```
    facing = Direction(1) # east
    Direction.offset(facing) # (0, 1)
    Direction.rotate(facing, 'CW') # Direction(2)
    Direction.rotate(facing, 'CW') # Direction(3)
    Direction.rotate(facing, 'CW') # Direction(0)
    ```
    """

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @staticmethod
    def rotate(facing: "Direction", towards: Rotation) -> "Direction":
        offset = 1 if towards == "CW" else -1
        # cheaper to use singletons than recalculate dynamically every time
        return _DIRECTIONS[(facing.value + offset) % 4]

    @staticmethod
    def offset(facing: "Direction") -> GridPoint:
        return _ROW_COLL_OFFSETS[facing]


_DIRECTIONS = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]

_ROW_COLL_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}


class Position(NamedTuple):
    """
    Represents an immutable directional location in a grid. Methods return new `Position`s.

    ```
    cur = Position((0, 0), Direction.DOWN)
    cur.next_loc # (1, 0)
    cur.step() # Position((1, 0), Direction.DOWN)
    cur # Position((0, 0), Direction.DOWN)
    ```
    """

    loc: GridPoint
    """
    Your location in a `(row, col)` grid.
    """
    facing: Direction
    """
    Your current direction.
    """

    @property
    def next_loc(self) -> GridPoint:
        """
        Where you'd land, if you stepped.
        """
        return add_points(self.loc, Direction.offset(self.facing))

    def step(self) -> "Position":
        """
        Return a new Position based on stepping once in a direction.
        """
        return Position(self.next_loc, self.facing)

    def rotate(self, towards: Rotation) -> "Position":
        return Position(self.loc, Direction.rotate(self.facing, towards))
