# Day 11 (2020)

`Seating System` ([Prompt](https://adventofcode.com/2020/day/11))

## Part 1

Advent of Code is the poster child for referencing well known Computer Science concepts, and today is no different. Today's beneficiary is [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

After a first read, the key code will be getting the adjacent squares for a point. To hold our points, we'll need a grid. You might think it'd be a 2-D `list`, but we can get away with `List[str]`; Python's `string`s do everything we would need out of a `list`.

Our grid will look a little odd for those expecting regular `(X, Y)` coordinates from math class. `(0, 0)` is the top left corner of the grid. `X` increases in value to the right and `Y` increases in value going down. The biggest curve is that the `row` comes first, since that's how we'll access it in code. Here's a quick diagram:

```
#    y, x
#
#    0 x-> 4
#    y .L..L
#    | .L...
#    V .....
#      ..L..
#    4 ....L
```

There are `L`s at:

- `(0, 1)`
- `(0, 4)`
- `(1, 1)`
- `(3, 2)`
- `(4, 4)`

It's represented in code as:

```py
a = [
  '.L..L',
  '.L...',
  '.....',
  '..L..',
  '....L',
]
```

And we can access points in a natural way:

```py
a[0][1] # => 'L'
```

Anyway, let's break some ground.

Using `InputTypes.STRSPLIT`, there's no extra input parsing needed! So [that was a freebie](https://memegenerator.net/img/instances/67476777.jpg). We'll start with a `Grid` class:

```py
class Grid:
    def __init__(self, grid: List[str]) -> None:
        self.grid = grid
        self.next_grid = []

        self.max_x = len(self.grid[0])
        self.max_y = len(self.grid)
```

We also want a representation of the floor types since it keeps us nice and organized:

```py
from enum import Enum

# inherit from str so it prints nicely
class Tile(str, Enum):
    FLOOR = "."
    EMPTY_SEAT = "L"
    OCCUPIED_SEAT = "#"
```

Next, we need to be able to look up the tile at a point, taking into account the boundaries of the grid:

```py
from functools import cache

@cache
def tile_at(self, y, x) -> Tile:
    if y < 0 or x < 0 or x == self.max_x or y == self.max_y:
        return Tile.FLOOR
    # converts str to Tile, only needed on the first pass, but mostly harmless otherwise
    return Tile(self.grid[y][x])
```

Straightforward enough so far! `@cache` will help us greatly since there's a lot of repeated work in this one.

We also need a function to count all the occupied seats around a point:

```py
def num_occupied_adjacent(self, y, x) -> int:
    # clockwise from 12
    directions = [
        (y - 1, x),
        (y - 1, x + 1),
        (y, x + 1),
        (y + 1, x + 1),
        (y + 1, x),
        (y + 1, x - 1),
        (y, x - 1),
        (y - 1, x - 1),
    ]

    return Counter([self.tile_at(*direction) for direction in directions])[
        Tile.OCCUPIED_SEAT
    ]
```

A couple of tricks to note here:

- `tile_at(*direction)` is a shorthand for `tile_at(y, x)` when `direction == (y, x)`
- Python's `Counter` class, which takes an iterable, counts occurances of each items, and provides dictionary-like lookup.

Now that we've got our util functions in place, we can get to the meat of the loop. Given a tile, we should calculate what it'll change to:

```py
def next_tile(self, y, x) -> Tile:
    tile = self.grid[y][x]
    # floors never change, skip the rest of computation
    if tile == Tile.FLOOR:
        return Tile.FLOOR

    num_occupied_adjacent = self.num_occupied_adjacent(y, x)
    if tile == Tile.EMPTY_SEAT and num_occupied_adjacent == 0:
        return Tile.OCCUPIED_SEAT
    if (
        tile == tile.OCCUPIED_SEAT
        and num_occupied_adjacent >= self.change_threshold
    ):
        return Tile.EMPTY_SEAT
    return tile
```

Finally, the function to calculate each step:

```py
def step(self) -> bool:
    """
    Returns `True` if further steps are needed, `False` otherwise
    """
    for y in range(self.max_y):
        new_row = []
        for x in range(self.max_x):
            new_row.append(self.next_tile(y, x))
        self.next_grid.append(new_row)

    if self.grid == self.next_grid:
        return False

    self.grid = self.next_grid
    self.next_grid = []
    self.tile_at.cache_clear()
    return True
```

The only line of note is that `self.tile_at.cache_clear()`. We need to bust the cache each step so the function doesn't return the previous grid's results.

Before we wrap up, we need a way to count a given tile type in the grid. Plus, it never hurts to be able to easily print the grid:

```py
def print_grid(self):
    print()
    print("\n".join(["".join(row) for row in self.grid]))

def count_tiles(self):
    res = Counter()
    for row in self.grid:
        res.update(row)
    return res
```

Finally, our actual solution:

```py
def part_1(self) -> int:
    grid = Grid(self.input)

    while grid.step():
        pass

    return grid.count_tiles()[Tile.OCCUPIED_SEAT]
```

Though this ends up being a lot of code, none of it is particularly complex. You could do it in far fewer lines if you used strings instead of `Enum` and kept everything in one big loop. But brevity shouldn't come at the expense of maintainability (even for puzzle code).

This day is also notable for being the slowest running so far. While most programs finish almost instantly, this takes ~ `5.5` seconds on my machine. Totally within acceptible limits, but interesting nonetheless.

### Speed Optimizations

We can always go faster (though you [probably don't need to](https://blog.codinghorror.com/why-arent-my-optimizations-optimizing/)). There are two big ways to speed this up.

Firstly, we can improve `next_tile` by bailing as soon as possible. If a tile is `empty` and we find a single adjacent tile, we can bail early. Similarly, as soon as an occupied tile sees 4 other occupied ones, we can exit early.

The "worst" case is that we have to look at all 8 tiles to verify that either there are 0 tiles (empty -> occupied) or there aren't enough to meet the treshold.

Secondly, we can ditch the enums. It hurts readability a little and can be a source of bugs (comparing a string to an invalid `string`, like `tile == ','`), but there does end up being a performance impact.

Here's the final next tile loop:

```py
def next_tile(self, y, x) -> str:
    tile = self.grid[y][x]
    if tile == ".":
        return "."

    num_occupied_adjacent = 0
    for adj_tile in self.adjacent_tiles(y, x):
        if adj_tile == "#":
            # it has to have 0 to change from L, so we can bail early
            if tile == "L":
                return "L"

            num_occupied_adjacent += 1
            # stop as soon as we hit the treshold
            if num_occupied_adjacent == 4 and tile == "#":
                return "L"

    # at this point, it's either an empty that has no occupieds next to it,
    # or an occupied that didn't meet threshold
    return "#"
```

A more efficient loop runs my solution in `3.84s` and using `string` instead of `Enum` drops it to `2.54s`. Not relevant for the purposes of AoC, but thinking through ways to speed up loops in core code is a valuable practice.

## Part 2
