---
year: 2022
day: 18
title: "Boiling Boulders"
slug: "2022/day/18"
pub_date: "2022-12-31"
---

## Part 1

Given that our input is relatively small, I think we can get away with a quick and dirty solution today. We'll make a set of the 3D points from our input, then iterate the neighbors for each cube to see which are missing.

First, our input:

```py
GridPoint3D = tuple[int, int, int]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        points: set[GridPoint3D] = {
            tuple(map(int, line.split(","))) for line in self.input
        }
```

Next, a little helper to get the neighbors in 3D. My built-in function doesn't do 3D (yet), so I wrote a little one:

```py
from itertools import product
from typing import Iterable

...
def neighbors_3d(p: GridPoint3D) -> Iterable[GridPoint3D]:
    for idx, offset in product(range(3), (-1, 1)):
        copied = list(p)
        copied[idx] += offset
        yield tuple(copied)
```

Lastly, we count the number of neighbors that arne't in the set:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for p in points:
            for neighbor in neighbors_3d(p):
                if neighbor not in points:
                    total += 1

        return total
```

## Part 2

Part 2 is very similar to part 1, but we have to ignore blocks that aren't reachable from the exterior of the structure. To find those, we do a pretty standard [flood-fill algorithm](https://en.wikipedia.org/wiki/Flood_fill) to classify every point in the grid.

So, let's make a structure to track status of each point:

```py
from enum import Enum, auto

...
class PointState(Enum):
    UNREACHABLE = auto()
    ROCK = auto()
    REACHABLE = auto()

...
class Solution(StrSplitSolution):
    def part_2(self) -> int:
        # input parsing from part 1
        points = self.parse_points()

        grid: defaultdict[GridPoint3D, PointState] = defaultdict(
            lambda: PointState.UNREACHABLE
        )
        for p in points:
            grid[p] = PointState.ROCK
```

Now that we have our rock structure expressed in the grid, we can run the fill algorithm. We'll do a breadth-first search, which steps through reachable points and all all neighbors to the queue. It shares a lot of implementation details with the depth-first search we used to back our Dijkstra's algorithm in days [12](/writeups/2022/day/12/) and [16](/writeups/2022/day/16/). The only thing left to calculate is the max size of the grid (so we know when to stop checking out into space)

```py
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...

        size = 0
        for p in points:
            size = max(size, *p)
        size += 1  # grid that's 1 bigger than the biggest dimension
```

Now we're ready to begin! We'll start in the corner (`(0,0,0)`) and add neighbors to our queue (as long as we haven't seen them, they haven't been found already, and they're in bounds):

```py
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...

        seen: set[GridPoint3D] = set()
        queue: list[GridPoint3D] = [(0, 0, 0)]

        while queue:
            current = queue.pop()
            grid[current] = PointState.REACHABLE
            seen.add(current)

            for neighbor in neighbors_3d(current):
                if (
                    grid[neighbor] == PointState.UNREACHABLE
                    and neighbor not in seen
                    and all(-1 <= x <= size for x in neighbor)
                ):
                    queue.append(neighbor)
```

And finally, we re-run our part 1 with a slightly different condition. I couldn't think of a clever way to condense these (since they both have separate conditions), so we'll just re-write it:

```py
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...

        total = 0
        for p in points:
            for neighbor in neighbors_3d(p):
                if grid[neighbor] == PointState.REACHABLE:
                    total += 1

        return total
```
