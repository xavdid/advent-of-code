---
year: 2024
day: 4
slug: "2024/day/4"
title: "Ceres Search"
# concepts: []
pub_date: "2024-12-04"
---

## Part 1

Advent of Code and grids, name a more classic duo.

To save some time today, We'll be using some of the grid helper functions I've honed over the years, which I'll explain briefly.

For most AoC puzzles where the input is a grid, I use `(row, col)` coordinates for every character (starting in the top left):

```
(0, 0) ------> (0, 9)
  |              |
  |              |
  |              |
  |              |
  V              V
(9, 0) ------> (9, 9)
```

It takes a little getting used to if you always think in `(x, y)` coordinates, but it lines up nicely with the indexes in a 2-D list (`list[list[str]]`). That said, I don't actually use lists to store grids anymore.

Instead, I use a sparse `dict` whose keys are the aforementioned `(row, col)` 2-tuples and values are the character at that location. That approach lets me omit any walls or inaccessible locations from the grid entirely, simplifying "can I move to this position" calculations.

The code for this is straightforward:

```py
GridPoint = tuple[int, int]
Grid = dict[GridPoint, str]

def parse_grid(raw_grid: list[str]) -> Grid:
    """
    returns 2-tuples of (row, col) with their value
    """
    result = {}

    for row, line in enumerate(raw_grid):
        for col, c in enumerate(line):
            result[row, col] = c

    return result
```

Which parses the sample input as:

```py
{(0, 0): 'M',
 (0, 1): 'M',
 (0, 2): 'M',
 (0, 3): 'S',
 (0, 4): 'X',
 (0, 5): 'X',
 (0, 6): 'M',
 (0, 7): 'A',
 (0, 8): 'S',
 (0, 9): 'M',
 (1, 0): 'M',
 (1, 1): 'S',
 (1, 2): 'A',
 ...
}
```

My next most used function is `neighbors`. It takes a center `GridPoint` plus a bunch of options and yields all the neighboring points for that configuration. It works like most of my grid operations do- by adding a `GridPoint` to an offset to get a new point. Adding is simple:

```py
def add_points(a: GridPoint, b: GridPoint) -> GridPoint:
    return a[0] + b[0], a[1] + b[1]
```

The full neighbor generation is written with `(x, y)` variable names (because it works for Cartesian grids as well) but works the same for `(row, col)` grids. The full thing is [on GitHub](https://github.com/xavdid/advent-of-code/blob/140c7462682356db6adaba9522c28d39020b3366/solutions/utils/graphs.py#L12-L71) but the gist is:

```py
# all 9 possible offsets
OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), ...]

def neighbors(
    center: GridPoint,
    num_directions=8,
    *, # all further arguments must be specified via a keyword for readability
    max_size: Optional[int] = None,
    diagonals=False,
) -> Iterator[tuple[int, int]]:
    assert num_directions in {4, 8, 9}

    for offset_x, offset_y in OFFSETS:
        if diagonals and not (offset_x and offset_y):
            # orthogonal; skip
            continue

        if num_directions == 4 and not diagonals and offset_x and offset_y:
            # diagonal; skip
            continue

        if num_directions != 9 and not (offset_x or offset_y):
            # skip self
            continue

        next_x, next_y = add_points(center, (offset_x, offset_y))

        # max size implies a min size
        if max_size and (next_x < 0 or next_y < 0):
            continue

        if max_size and (next_x > max_size or next_y > max_size):
            continue

        yield (next_x, next_y)
```

> NOTE: these functions aren't included with [my template](https://github.com/xavdid/advent-of-code-python-template) to encourage you to create your own instead. But, you're welcome to copy them if the suit your needs!

Those in hand, we can actually solve part 1. We need to look for any `X` in our grid and see if any of its neighbors is an `M`. If it is, we figure out which direction we stepped and step twice more, ensuring we find `A` and `S` as expected. There's not a lot to it:

```py
def subtract_points(a: GridPoint, b: GridPoint) -> GridPoint:
    return a[0] - b[0], a[1] - b[1]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        for center, letter in grid.items():
            if letter != "X":
                continue

            for neighbor in neighbors(center, max_size=len(self.input) - 1):
                if grid[neighbor] != "M":
                    continue

                # we've stepped towards an M from an X. So, find our offset and keep moving in this direction.
                offset = subtract_points(neighbor, center)

                if (
                    grid.get((maybe_a := add_points(neighbor, offset))) == "A"
                    and grid.get(add_points(maybe_a, offset)) == "S"
                ):
                    total += 1

        return total
```

The only real trick was getting our `offset` back from the `neighbor`. I added a small `subtract_points` to reverse the addition, allowing us to continue traveling in the same direction as we've already stepped. Past that, it's just some `if` statements to verify the characters and a quick use of the [walrus operator](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions) to capture the intermediate `maybe_a` value.

## Part 2

In order to find `X-MAS`, we'll need some small logical tweaks and a new set of arguments for `neighbors`. We'll be starting on `A`s and we only care about the 4 diagonal neighbors. For each `A` neighbor that's an `M`, we'll find our offset again. But then, we'll step the _opposite_ direction from center (instead of the same direction from neighbor) to ensure there's an `S` on the other side. If we do that successfully exactly twice, then we increment a counter:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        grid = parse_grid(self.input)

        total = 0
        for center, letter in grid.items():
            if letter != "A":
                continue

            num_mas = 0
            for neighbor in neighbors(
                center,
                max_size=len(self.input) - 1,
                num_directions=4,
                diagonals=True,
            ):
                if grid[neighbor] != "M":
                    continue

                # we've got an M. Is there an S in the opposite direction?
                offset = subtract_points(center, neighbor)

                if grid.get(add_points(center, offset)) == "S":
                    num_mas += 1

            if num_mas == 2:
                total += 1

        return total
```

Today, more than most, I think we recognized the value of goo helper methods. It's definitely worth developing your own for things you commonly come back to.

If you need inspiration, I found this [tricks and snippets thread](https://old.reddit.com/r/adventofcode/comments/1gsl4fm/share_your_favorite_tricks_and_snippets/) on Reddit to be quite enlightening!
