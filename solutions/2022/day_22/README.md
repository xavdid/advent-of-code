# Day 22 (2022)

`Monkey Map` ([prompt](https://adventofcode.com/2022/day/22))

## Part 1

The odd-shaped grid caught me by surprise to start, but it didn't end up being too bad.

We can treat our grid as a big rectangle that circumscribes the actual points. Using our same `(row,col)` grid from before, we can lay this weird shape out more normally:

```
   000000000011111111
   012345678901234556
00         ...#
01         .#..
02         #...
03         ....
04 ...#.......#
05 ........#...
06 ..#....#....
07 ..........#.
08         ...#....
09         .....#..
10         .#......
11         ......#.
```

We'll use a `dict` that maps grid points to a boolean. If a point isn't in the `dict`, it's a blank space and we'll skip over it when moving (more on that soon). Otherwise, we can use a `bool` to represent whether we can walk on a given space.

Let's put this in a class:

```py
GridPoint = tuple[int, int]

class SparseGrid:
    def parse_grid(self, raw_grid: str) -> tuple[dict[GridPoint, bool], int, int]:
        rows = raw_grid.split("\n")
        max_rows = len(rows)
        max_cols = max(len(s) for s in rows)

        grid: dict[GridPoint, bool] = {}

        for row, line in enumerate(rows):
            for col, c in enumerate(line):
                if c == " ":
                    continue
                grid[(row, col)] = c == "."

        return grid, max_rows, max_cols
```

This handles the top half of the input, but we also need to parse the path, which is numbers and letters:

```py
class SparseGrid:
    ...

    def parse_path(self, s: str) -> list[Literal["L", "R"] | int]:
        return [int(c) if c.isdigit() else c for c in re.findall(r"\d+|\w", s)]
```

Regex to the rescue! It finds digits and letters without us having to worry about long numbers.

Wrap that all in an `__init__` method and we're off to the races:

```py
class SparseGrid:
    def __init__(self, raw_input: str) -> None:
        grid, path = raw_input.split("\n\n")

        self.grid, self.max_rows, self.max_cols = self.parse_grid(grid)
        self.path = self.parse_path(path)
    ...
```

There's two important pieces of state we need to maintain: our current location and our direction. We'll make like we did on [day 17](https://github.com/xavdid/advent-of-code/tree/main/solutions/2022/day_17) and add an offset to our location based on the direction we're facing. Rotating is a matter of wrapping an index around a list (using the modulo operator). Our starting location is the first `.` on the top row, so we can add that to `__init__`:

```py
OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class SparseGrid:
    offset_index = 0

    def __init__(self, raw_input: str) -> None:
        ...

        self.location: GridPoint = 0, raw_input.find(".")

    def rotate(self, direction: Literal["L", "R"]):
        x = -1 if direction == "L" else 1
        self.offset_index = (self.offset_index + x) % 4

    @property
    def offset(self):
        return OFFSETS[self.offset_index]
```

Finally, we're ready to actually process instructions. We've done a good job making our functions small and descriptive, so the actual work is pretty straightforward here:

```py
class SparseGrid:
    ...

    def run(self):
        for instruction in self.path:
            if isinstance(instruction, str):
                self.rotate(instruction)
            else:
                for _ in range(instruction):
                    ... # TODO

        return (
            # add 1 because our grid is 0-indexed
            1000 * (self.location[0] + 1)
            + 4 * (self.location[1] + 1)
            + self.offset_index
        )
```

All that remains is moving a specified number of times (if able). That last part is really the rub, specifically finding the next valid step. Luckily, we've made a distinction between points we can't step on (`False`) and points that don't exist at all (missing from the `dict`). We have to write a function to wrap around if we've left the grid entirely, but otherwise that'll do a lot of the heavy listing for us. It's not so bad:

```py
...

def add(loc: GridPoint, offset: GridPoint) -> GridPoint:
    return loc[0] + offset[0], loc[1] + offset[1]

class SparseGrid:
    ...

    def next_valid_loc(self) -> GridPoint:
        next_loc = add(self.location, self.offset)

        while next_loc not in self.grid:
            if next_loc[0] >= self.max_rows:
                next_loc = -1, next_loc[1]
            elif next_loc[1] >= self.max_cols:
                next_loc = next_loc[0], -1
            elif next_loc[0] < 0:
                next_loc = self.max_rows, next_loc[1]
            elif next_loc[1] < 0:
                next_loc = next_loc[0], self.max_cols

            next_loc = add(next_loc, self.offset)

        return next_loc
```

`next_valid_loc` walks in a set direction until it finds a point that's in the grid. It doesn't much care what the point is, just that we're back on the map.

This lets us fill in the rest of our `run` code:

```py
class SparseGrid:
    ...

    def run(self):
        for instruction in self.path:
            if isinstance(instruction, str):
                self.rotate(instruction)
            else:
                for _ in range(instruction):
                    # update location if the next in-grid location isn't a wall
                    # the walrus works even inside a dict lookup!
                    if self.grid[next_loc := self.next_valid_loc()]:
                        self.location = next_loc
                    else:
                        break

        return ...
```

Instantiating and running our `SparseGrid` is all that remains:

```py
class Solution(TextSolution):
    def part_1(self) -> int:
        return SparseGrid(self.input).run()
```

## Part 2
