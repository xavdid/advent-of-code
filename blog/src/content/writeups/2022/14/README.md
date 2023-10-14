---
year: 2022
day: 14
title: "Regolith Reservoir"
slug: "2022/day/14"
pub_date: "2022-12-15"
---

## Part 1

I gotta be honest, [I don't like sand](https://www.youtube.com/watch?v=2tLf1JO5bvE). But, that wasn't going to stop me from enjoying today! The actual sand simulation seems tricky, so I'm just going to start with the inpu... oh no. Input parsing _also_ looks hard. I guess our [vacation is... over](https://www.youtube.com/watch?v=UxdimFWnJ4w).

Before we parse, we should take a second to consider how we'll store the walls (and eventually, the sand). We could make a huge 2D array like we've done in days past, but given that the source is at an `x` of `500`, there are probably more space efficient ways to do it. Looking at the puzzle, once a grain of sand has settled, there's no practical difference between that grain and a wall.[^1] So, we can get away with storing a bit `set` of `(x, y)` points which represent non-empty-space items (walls & sand). Lookups will be fast and it will simplify our logic (we don't need to handle walls and sand separately).

Now, the input itself. The tricky thing is that each line can be drawn in any direction; they're not strictly `left -> right` or `top -> bottom`. We won't be able to drop them right into a `range`. The good news is for each pair of points (that comprise a segment), either both `x` values or both `y` values will be identical. So we can code around that a bit to make our ranges. We'll also have to run everything through `min` and `max` so that we can use `range` correctly:

```py
from itertools import pairwise

Grid = set[GridPoint]
Walls = frozenset[GridPoint]

class Solution(StrSplitSolution):
    x_min = 1000
    x_max = 0
    y_max = 0

    # only modified in parse_walls
    walls: Walls = frozenset()

    def parse_walls(self) -> Grid:
        grid: Grid = set()
        for line in self.input:
            points = [tuple(map(int, p.split(","))) for p in line.split(" -> ")]
            for (x0, y0), (x1, y1) in pairwise(points):
                self.x_min = min(self.x_min, x0, x1)
                self.x_max = max(self.x_max, x0, x1)
                self.y_max = max(self.y_max, y0, y1)

                if x0 == x1:
                    # vertical line
                    for y in range(min(y0, y1), max(y0, y1) + 1):
                        grid.add((x0, y))
                else:
                    # horizontal line
                    for x in range(min(x0, x1), max(x0, x1) + 1):
                        grid.add((x, y0))

        # frozen so I don't modify it accidentally later
        self.walls = frozenset(grid)
        return grid
```

There's maybe a cleaner way to do this, but it worked the first time, so I kept it. The `+ 1` on the ranges ensure that the end of the range is inclusive of all points. I thought I could be clever and bank on the fact that the next range's start uses this range's end, but that doesn't hold true for the first and last segments. Better to do a few double-`add`s than be missing walls. I also added a running total to track min/max values of x and y, since we'll need those to print the grid (see below). Lastly, I learned about `itertools.pairwise` (available in Python 3.10), which is the rough equivalent of the `zip(some_list, some_list[1:])` that I mentioned the other day.

Next, printing the grid. Not strictly required, but an easy way to confirm our input is right. Plus, it'll let us debug better if something goes wrong later. Because we know the bounds of the grid, we can make ranges of them:

```py
...

SOURCE: GridPoint = (500, 0)

...

class Solution(StrSplitSolution):
    def print_grid(self, grid: Grid):
        for y in range(self.y_max + 2):
            for x in range(self.x_min - 1, self.x_max + 2):
                p = x, y
                if p == SOURCE:
                    print("+", end="")
                    continue

                if p in self.walls:
                    print("#", end="")
                elif p in grid:
                    print("o", end="")
                else:
                    print(".", end="")
            print()
```

We make use of `print`'s `end` kwarg to not automatically print a `\n` after each statement (which would mess up our grid). Next up, our solution!

I didn't have the whole solution in my head when I started writing, so I stepped through the bits that I knew. First, sand will fall (meaning its `y` value increments until its destination is blocked), at which point it will stop:

```py
from itertools import count, pairwise

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = self.parse_walls()

        for grain_num in count():
            x = 500
            for y in count(1):
                if (x, y) not in grid:
                    continue # tries next downward position

                grid.add((x, y - 1))
                break # starts next grain

                assert y < self.max_y + 3, "falling off the bottom!"
            assert grain_num < 25, "too many grains!"
```

Easy enough! If the point is empty, we keep going. If it's not, the sand rests at the point directly above us. We're making liberal use of `itertools.count`, which will iterate a counter for us; it's easier and safer than having to `+= 1` all over the place. We also add some `assert` statements to prevent runaway loops while we're working. Running a couple of iterations and printing the grid shows a small stack of sand forming, which is generally what we want.

Next up is the L/R logic. If our destination is occupied, can we land at either spot next to it? Because of our loop setup, that's only a couple of logic branches:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = self.parse_walls()

        for grain_num in count():
            x = 500
            for y in count(1):
                ...

                # try left
                if (x - 1, y) not in grid:
                    x -= 1
                    continue

                # try right
                if (x + 1, y) not in grid:
                    x += 1
                    continue

                ...
```

A couple more loops and we see our sand pooling like the example shows. Last thing is our exit command, which should trigger if `y` is greater than `y_max`. Whatever grain triggers this is the first one to fall into the abyss, so we should return the number of the grain before this one. Since we're 0-indexed, the math "just works" on the count. Here's part 1 in all its glory:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = self.parse_walls()


        for grain_num in count():
            x = 500
            for y in count(1):
                # falling off the world!
                if y > self.y_max:
                    return grain_num

                if (x, y) not in grid:
                    continue # tries next downward position

                if (x - 1, y) not in grid:
                    x -= 1
                    continue # tries next downward position with updated x

                if (x + 1, y) not in grid:
                    x += 1
                    continue # tries next downward position with updated x

                grid.add((x, y - 1))
                break # starts next grain
```

Not so bad once we got rolling.

## Part 2

On the surface, this change seems simple enough to understand. In addition to our parsed walls, we also need to add \*checks notes\* infinite walls at `y_max + 2`. Easy enough.

I started by adding logic checks around the `not in grid` lines to also check for `y >= self.y_max + 2`, but the logic got out of hand fast. What if we could have our set lie and say that everything touching the floor _was_ in the set? It sounds hard, but all it takes is something that _acts_ like a set. Let's make a (data)class:

```py
from dataclasses import dataclass

...

@dataclass
class Grid:
    _grid: set[GridPoint]
    floor: int

    def add(self, p: GridPoint):
        self._grid.add(p)

    def __contains__(self, item: GridPoint):
        return item[1] >= self.floor or item in self._grid
```

Because the only set operation we're doing is `in`, we don't have to re-implement everything.[^2] The only important thing is the `__contains__` operator, which powers the `x in y` expression. This change also hardly effects our grid parsing:

```py
...

class Solution(StrSplitSolution):
    ...

    def parse_walls(self) -> Grid:
        ...

        floor = self.y_max + 2
        self.walls = frozenset(grid.copy())
        return Grid(grid, floor)
```

We do need small tweaks to the solution so it handles both parts:

```py
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        grid = self.parse_walls()
        part_1 = -1

        for grain_num in count():
            x = SOURCE[0]
            for y in count(1):
                # end of part 1
                if part_1 == -1 and y > self.y_max:
                    part_1 = grain_num

                ...
```

If we returned `part_1` there, we would still have a working part 1 solution. But, we have one more change to make. We have to check if `SOURCE is in grid`:

```py
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        ...

        for grain_num in count():
            # end of part 2
            if SOURCE in grid:
                return part_1, grain_num
```

And that's it! Our grid lies exactly as much as we want it to, we can still print the scene nicely, and the solution runs quickly and without any recursion.

> _NOTE_: The above is a summary of my cleaned and edited part 2 solution. You can also read [my completed (but not edited) part 2 solution](https://github.com/xavdid/advent-of-code/blob/790483a834628af6ac5535675c8058cd81a1ad70/solutions/2022/day_14/solution.py), if you like reading messy code; sometimes it's nice to see the process.

[^1]: except for printing the grid, which we'll cover. That's not required for the solution though.
[^2]: if we did, it would be easier to subclass `set` itself and modify from there.
