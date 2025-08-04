---
year: 2024
day: 16
slug: "2024/day/16"
title: "Reindeer Maze"
# concepts: ["Dijkstra"]
pub_date: "2025-08-03"
---

## Part 1

We're tasked finding the shortest path to a specific point, so it's time to mix a depth-first search with a priority queue! It'll look a bit like [day 10](/writeups/2024/day/10/), but with some new twists.

Each node in this graph (since that what these grids are, just a bunch of interconnected nodes) has a cost to reach based on the number of steps and rotations it is from the start. If we keep a sorted list of the cost needed to reach each point, then each time we visit a never-before-seen node, we'll know the cheapest way to get there. If that node is the target, we'll have solved the problem!

Unlike most pathfinding problems, we care about direction in addition to location. So we'll need to pull in some code for tracking our direction and rotating when needed. Let's get to it!

First, the utils. We need a way to track the direction we're facing and where we'll end up if we step in that direction. I've got a nice little `Direction` enum that I can slot into a `Position` class:

```py
from enum import IntEnum
from typing import Literal, NamedTuple

from ...utils.graphs import GridPoint # tuple[int, int]

Rotation = Literal["CCW", "CW"]


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @staticmethod
    def rotate(facing: "Direction", towards: Rotation) -> "Direction":
        offset = 1 if towards == "CW" else -1
        return Direction((facing.value + offset) % 4)

    @staticmethod
    def offset(facing: "Direction") -> GridPoint:
        return _ROW_COLL_OFFSETS[facing]


_ROW_COLL_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}


class Position(NamedTuple):
    loc: GridPoint
    facing: Direction

    @property
    def next_loc(self) -> GridPoint:
        return add_points(self.loc, Direction.offset(self.facing))

    def step(self) -> "Position":
        return Position(self.next_loc, self.facing)

    def rotate(self, towards: Rotation) -> "Position":
        return Position(self.loc, Direction.rotate(self.facing, towards))
```

These play nicely with my `(row, col)`-based [graph utils](/writeups/2024/day/4/). Plus they're children of `tuple` so they're immutable and can be used as `dict` keys, which is about to be very convenient. Let's initialize some data!

```py
from ...utils.graphs import parse_grid

type State = tuple[int, Position]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        visited: set[Position] = set()

        grid = parse_grid(self.input, ignore_chars="#")
        start = Position(next(k for k, v in grid.items() if v == "S"), Direction.RIGHT)
        queue: list[State] = [(0, start)]
```

Pretty standard as far as DFS goes, excepting the additional data in `State`. Putting the cost in the first element of the tuple means our states are always sorted by cost, which is convenient.

Now the main loop. We'll pop the cheapest unvisited position, mark it as visited, and add its neighbors and their respective costs to the queue. Python has a great [priority queue package](https://docs.python.org/3/library/heapq.html) that makes this pretty simple:

```py
from heapq import heappop, heappush
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while queue:
            cost, position = heappop(queue)

            if position in visited:
                continue

            visited.add(position)

            next_pos = position.step()
            if next_pos.loc in grid and next_pos not in visited:
                heappush(queue, (cost + 1, next_pos))

            for direction in "CW", "CCW":
                if (next_pos := position.rotate(direction)) not in visited:
                    heappush(queue, (cost + 1000, next_pos))
```

I'm making pretty heavy use of the [walrus operator](https://realpython.com/python-walrus-operator/) to calculate variables and use them in conditionals immediately, but the actual operation is simple. We have 3 possible things we can do: step forward, rotate clockwise, or rotate counterclockwise. Before we can queue a move, we need to ensure that next state is:

1. not visited
2. (if moving) in the grid

If all those things are true, we use `heappush` to efficiently enqueue that next state. We keep visiting the cheapest node until we've found our target and return that cost.

We'll keep checking positions until we've found the target at which point we can return our result:

```py ins={10-11}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while queue:
            cost, position = heappop(queue)

            if grid[position.loc] == 'E':
                return cost

            visited.add(position)
            ...
```

## Part 2

Now we need to find _all_ optimal paths, not just the first one. An approach using [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) might have been useful, since then we'd know the cost from the start to every position. But we're too far in now!

Instead, we can amend `State` to include all of the locations we've been to. All that takes is some little tweaks. We can reuse our part 1 code:

```py rem={3,7,12,17,22} ins={4,8,13,18,23}
...

type State = tuple[int, Position]
type State = tuple[int, Position, tuple[GridPoint, ...]]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        ...

        while queue:
            cost, position = heappop(queue)
            cost, position, path = heappop(queue)
            ...

            if next_pos.loc in grid and next_pos not in visited:
                heappush(queue, (cost + 1, next_pos, path))
                heappush(queue, (cost + 1, next_pos, path + (position.loc,)))

            for direction in "CW", "CCW":
                if (next_pos := position.rotate(direction)) not in visited:
                    heappush(queue, (cost + 1000, next_pos))
                    heappush(queue, (cost + 1000, next_pos, path))
```

Using a `tuple` instead of a `list` is a dumb little optimization that saves a bit of time, but it also ensures we're not mutating state where we don't intend to (that is, each `State` gets a fresh copy of the `path`). Also note that only move operations modify the path, since a rotate doesn't introduce any additional locations.

Next, we have to change our exit conditions. Instead of returning from our loop when we find the target, we want to add our path to the best seats if (and only if!) it was an optimal path. Only problem is, we also need to know with paths are optimal.

Luckily, our code still finds the shortest path. Once we've found _a_ shortest path, we know that any other paths must have the same cost to be considered optimal. We can use that as our cost to beat:

```py rem={15,17} ins={1,8,9,16,18-20,24}
from math import inf
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        best_seats: set[GridPoint] = set()
        lowest_cost = inf
        ...

        while queue:
            ...

            if grid[position.loc] == 'E':
            if grid[position.loc] == "E" and cost <= lowest_cost:
                return cost
                lowest_cost = cost
                best_seats |= set(path) | {position.loc}
                continue

            ...

        return int(lowest_cost), len(best_seats)
```

So rather than stopping when we find a path, we store our visited paths and keep going. Then at the end, we just take the length of all the best seats. This works! It takes ~7 seconds to run though, which is a little slow for my liking.

There's one small tweak left to make. Once we've found an optimal path, the entire front of our queue will be additional positions of that ending location (because they're all sorted that way- any non-optimal paths will be after the optimal ones). So, how can we use that info to exit early?

Once we've set `lowest_cost` to something less than `inf`, we know that the optimal solution has been found. As a result, we don't have to keep exploring if we're no longer standing on the target and can safely `break`:

```py ins={17,18}
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        lowest_cost = inf
        ...

        while queue:
            ...

            if grid[position.loc] == "E" and cost <= lowest_cost:
                ...
                continue

            if lowest_cost < inf:
                break

            visited.add(position)
            ...
```

That cuts my runtime down to about 3 seconds, which is close enough for today!
