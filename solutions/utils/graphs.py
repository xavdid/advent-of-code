from itertools import product
from operator import itemgetter
from typing import Iterator

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
