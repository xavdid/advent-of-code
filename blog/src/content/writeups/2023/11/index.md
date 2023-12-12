---
year: 2023
day: 11
title: "Cosmic Expansion"
slug: 2023/day/11
pub_date: "2023-12-11"
---

## Part 1

As least for part 1, all we need from the grid is the locations of the `#`. We can make a slight modification to our grid parser [from yesterday](https://advent-of-code.xavd.id/writeups/2023/day/10/):

```py ins=", ignore_chars: str = ''" ins={14,18,19}
def parse_grid(raw_grid: list[str], ignore_chars: str = '') -> Grid:
    """
    returns 2-tuples of (row, col) with their value

    (0, 0) ------> (0, 9)
      |              |
      |              |
      |              |
      |              |
      |              V
    (9, 0) ------> (9, 9)
    """
    result = {}
    ignore = set(ignore_chars)

    for row, line in enumerate(raw_grid):
        for col, c in enumerate(line):
            if c in ignore:
                continue
            result[row, col] = c

    return result
```

If we call `.keys()` on the result of `parse_grid`, we'll have a list of every relevant point. Those are ultimately the points we'll measure between. But first, expansion!

First, we need the empty rows and columns. We can make a `set` of every possible column number and remove from it the column from every point; we'll do the same for rows:

```py
def empty_lines(grid: list[GridPoint], grid_size: int, dim: int) -> set[int]:
    return set(range(grid_size)) - {p[dim] for p in grid}
```

Next, the expansion. For each point, each of its dimensions needs to increase by the number of empty lines before it. We know which lines are empty, so we can filter that list to only include lines with an index lower than each dimension:

```py
def expand_points(val: int, empty_lines: set[int]) -> int:
    return len(tuple(filter(lambda i: i < val, empty_lines)))
```

The last thing we'll need is the distance between two points on a grid! This is a simple formula known as the taxicab (or Manhattan) distance:

```py
def taxicab_distance(a: GridPoint, b: GridPoint) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

Now, let's put it all together!

```py
from itertools import combinations

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid_size = len(self.input)
        grid = list(parse_grid(self.input, ignore_chars=".").keys())

        rows_to_expand = empty_lines(grid, grid_size, dim=0)
        cols_to_expand = empty_lines(grid, grid_size, dim=1)

        expanded_points = {
            (
                row + expand_points(row, rows_to_expand),
                col + expand_points(col, cols_to_expand),
            )
            for row, col in grid
        }

        return sum(taxicab_distance(a, b) for a, b in combinations(expanded_points, 2))
```

Once we have our expanded points, we get every pair of them using `itertools.combinations` and we're all set!

## Part 2

I had an linking about what part 2 might be, so I structured the above to make this transition easier on us. We need to make 3 changes:

1. move all of part 1 into a function
2. add a multiplier to `expand_points`
3. call our new function

The only tricky thing is the multiplier value. In part 1, lines got `2x` as big, so we added `1 * len(...)` to each dimension. To get 1 million times bigger, we'll add `999,999 * len(...)` (not `1M`, which is what I tried first).

Here are those changes:

```py ins=", multiplier: int" ins=" * (multiplier - 1)" ins=", multiplier" ins=" _solve" ins={22,25}
...

def expand_points(val: int, empty_lines: set[int], multiplier: int) -> int:
    return len(tuple(filter(lambda i: i < val, empty_lines))) * (multiplier - 1)


class Solution(StrSplitSolution):
    def _solve(self, multiplier: int) -> int:
        ...

        expanded_points = {
            (
                row + expand_points(row, rows_to_expand, multiplier),
                col + expand_points(col, cols_to_expand, multiplier),
            )
            for row, col in grid
        }

        return sum(taxicab_distance(a, b) for a, b in combinations(expanded_points, 2))

    def part_1(self) -> int:
        return self._solve(2)

    def part_2(self) -> int:
        return self._solve(1_000_000)
```

And that'll do it! Today plays nicely into one of my AoC rules of thumb: store only what you need and resort to math when the numbers get big (instead of iterating over large ranges).
