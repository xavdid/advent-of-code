---
year: 2024
day: 8
slug: "2024/day/8"
title: "Resonant Collinearity"
# concepts: []
pub_date: "2024-12-09"
---

## Part 1

Today feels like an exercise in reading comprehension more than anything else, but it's not too bad. We have to form a line between _each_ pair of matching ~~antennae~~ antennas and extrapolate one step in each direction.

The grid parsing is the same as [previous](/writeups/2024/day/4/) [days](/writeups/2024/day/6/), so nothing much there. The real work begins once we've turned our grid values into a set of frequencies (ignoring the `.` spots, since that's not a frequency). Iterating over each, we can build an iterator for all antenna that match our current frequency:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        frequencies = set(grid.values()) - {"."}

        antinode_locations = set()

        for frequency in frequencies:
            locations = (k for k, v in grid.items() if v == frequency)
```

Next, we use `itertools.combinations` to find every pair of matching antenna (without caring about order). For each of those pairs, we can find the offset between them by subtracting one from the other. With that offset (or slope!) in hand, we can extrapolate from each of our points, keeping the ones that are within the grid:

```py
from itertools import combinations

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for frequency in frequencies:
            ...

            for l, r in combinations(locations, 2):
                slope = subtract_points(l, r)

                for p in add_points(l, slope), subtract_points(r, slope):
                    if p in grid:
                        antinode_locations.add(p)

        return len(antinode_locations)
```

> The `add_points` and `subtract_points` functions are also from [day 4](/writeups/2024/day/4/); they're just utils for adding and subtracting 2-tuples.

Let's put some real numbers on this example to make sure we're understanding. Let's say we've got 2 points: `(2, 2)` and `(3, 3)`, our `l` and `r` respectively.

`l - r` is `(-1, -1)`, an offset which represents how to get from `r` to `l` (which has always seemed backwards to me, but it's how it works). If we add that offset to `l`, we'll move backwards to the point "behind" it, `(1, 1)`. If we took that point and subtracted the offset, we'd land back on `l`. Similarly, we can subtract that offset from `r` to take another step in the same direction as `l -> r`: `(4, 4)`.

The number of unique points we find this way is our puzzle answer!

## Part 2

Now, rather than stepping once, we step as long as we're still in the grid. Luckily, this only takes minor changes from our part 1 code. Instead of just checking one step, we'll set ourselves to keep walking in a direction until we hit the grid edge:

```py rem={3,14-16} add={4,17-22}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def part_2(self) -> int:
        ...

        for frequency in frequencies:
            locations = (k for k, v in grid.items() if v == frequency)

            for l, r in combinations(locations, 2):
                slope = subtract_points(l, r)

                for p in add_points(l, slope), subtract_points(r, slope):
                    if p in grid:
                        antinode_locations.add(p)
                for p, fn in (l, add_points), (r, subtract_points):
                    antinode_locations.add(p)

                    while (next_p := fn(p, slope)) in grid:
                        antinode_locations.add(next_p)
                        p = next_p

        return len(antinode_locations)
```

For each direction we want to move, we loop with our same step function from part 1, adding each element as we go. We also remember to add the starting node, since _every_ antenna location is also the antinode for everything else on the line.

This solution makes use of the walrus operator (`:=`) in a `while` loop, which is a convenient way to both update a variable and keep looping until a condition is met. We could also wrap that assignment in a `while True` with a `break` when we leave the grid, but I find this a little cleaner overall.
