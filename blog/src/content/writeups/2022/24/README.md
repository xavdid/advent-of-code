---
year: 2022
day: 24
title: "Blizzard Basin"
slug: "2022/day/24"
pub_date: "2023-07-28"
---

## Part 1

Whenever you see "fastest way to do X", it's a good bet we're going to use Dijkstra's algorithm like we did in [day 12](/writeups/2022/day/12/). I've covered this a number of times before, so I'll focus on what makes this problem unique.

First up, input! I started with a little `Blizzard` class. It needs to do 2 things:

- report its location
- step in its direction (and wrap if necessary)

That's easy enough using the same add-position-to-offset approach we've done before:

```py
from dataclasses import dataclass, field
from typing import Literal

GridPoint = tuple[int, int]

DIRECTIONS = Literal["<", ">", "v", "^"]
OFFSETS: dict[DIRECTIONS, GridPoint] = {
    "<": (0, -1),
    ">": (0, 1),
    "v": (1, 0),
    "^": (-1, 0),
}

@dataclass
class Blizzard:
    direction: DIRECTIONS
    position: GridPoint
    max_row: int = field(repr=False) # hidden from print statements
    max_col: int = field(repr=False) # hidden from print statements

    def move(self):
        offset_row, offset_col = OFFSETS[self.direction]

        self.position = (
            (self.position[0] + offset_row) % self.max_row,
            (self.position[1] + offset_col) % self.max_col,
        )
```

A blizzard only ever moves in one direction, so its moves are predictable. We can also supply the grid size and each blizzard will handling wrapping around the map at the right time.

Next, the actual grid. Rather than take the walls into account for the size of the grid, we'll ignore them and tread the start and end points as special cases. The grid parsing is therefore pretty straightforward:

```py
...

class Grid:
    blizzards: list[Blizzard] = []

    def __init__(self, raw_grid: str) -> None:
        rows = raw_grid.split("\n")
        self.max_rows = len(rows) - 2
        self.max_cols = len(rows[0]) - 2

        for row, line in enumerate(rows[1:-1]):
            for col, c in enumerate(line[1:-1]):
                if c not in OFFSETS:
                    continue

                self.blizzards.append(
                    Blizzard(c, (row, col), self.max_rows, self.max_cols)
                )
```

We have our list of blizzards and they're each able to move independently. They're on the `(row, col)` system that should be familiar (where `(0, 0)` is in the top left).

Next, let's consider our actual algorithm. Normally in Dijkstra's you have a set of `visited` nodes and a queue of sortable `(cost, node)` tuples. You traditionally only ever visit a node once, so you don't need any other info in the `visited` set. But to dodge blizzards, you may be retracing your steps (as shown in the example, where you're on `(0, 0)` in minutes 1 and 4). So we must track both the timestamp _and_ the location because `(1, (0, 0))` and `(4, (0, 0))` are distinct. This begets a new issue: time travel.

On an unchanging graph, you always know who your neighbors are. When you visit a node, it's easy to add the valid next steps: they are each neighbor at `time + 1`. But our graph is far from static, so the distinct points `(1, (0, 0))` and `(4, (0, 0))` have different sets of valid neighbors. This means that instead of maintaining a single `state` that shows all neighbors right now, we have to be able to look up neighbors for a point at a given timestamp. This means we'll need to track all states, not just the "current" one.

Before we can write that code, let's think about what data to store. We need to store the blizzard objects, since they know which direction to move when asked. But, there's nothing in the prompt about handling spaces where there are 2+ blizzards differently. At at given timestamp, we need to know the set of points which are occupied.

Will all that understanding in hand, we're ready to write some code:

```py
from heapq import heappop, heappush

...

Step = tuple[int, GridPoint]

class Grid:
    ...

    # the occupied points at a moment in time
    states: dict[int, set[GridPoint]] = {}
    steps_taken = 0

    def __init__(self, raw_grid: str) -> None:
        ...

        # after grid setup, get initial set of points
        self.states[0] = {b.position for b in self.blizzards}

    def state_at(self, time: int) -> set[GridPoint]:
        while time not in self.states:
            self.steps_taken += 1
            for b in self.blizzards:
                b.move()
            self.states[self.steps_taken] = {b.position for b in self.blizzards}

        return self.states[time]

    def run(self) -> int:
        start_point: GridPoint = (-1, -1)

        # time and expedition location
        queue: list[Step] = [(0, start_point)]
        visited: set[Step] = set()

        while queue:
            now = heappop(queue)
            if now in visited:
                continue
            visited.add(now)

            t, pos = now

            # gut check
            assert (
                pos not in self.states[t]
            ), f"Invalid! Occupied tile {pos} at time {t} at the same time a storm did"

            # TODO: add items to queue
            # something will hopefully return a time (our answer)

        raise ValueError("no solution found!")
```

That's a lot of code, but nothing to crazy! We:

- store states as a `dict` of `int` -> `set[GridPoint]`, so we can easily look up the state at any time
- we have a helper method (`state_at`) that caches the states and keeps track of how many times the blizzards have stepped (ensuring they're stored under the right key)
- we store a `start_point`, which exists outside the bounds of the grid (which otherwise starts at `(0, 0)`
- we have a basic Dijkstra implementation, which adds and removes items from a [priority queue](https://docs.python.org/3/library/heapq.html)
- we have an `assert` to make sure our logic is sound - we should never occupy a spot where there's currently a blizzard. Doing so is indicative of a bug (in code we haven't written yet)

Now, neighbor selection. In each case, we're going to look at `state_at[time + 1]` and add points to the queue if they're not in that set. We'll re-use the [neighbors](https://github.com/xavdid/advent-of-code/blob/513f070cd043b898d5b745e248ab0dd466d689f0/solutions/base.py#L300-L350) function to find current in-bound neighbors for each grid square. We also need special cases for the beginning and end (since those are outside the grid and won't be seen by `neighbors`). And of course, the ability to wait in place.

Here's what that all looks like:

```py
...

class Grid:
    ...

    def __init__(self, raw_grid: str) -> None:
        ...

        # the grid point _next_ to the exit, aka the bottom-right corner
        self.target: GridPoint = self.max_rows - 1, self.max_cols - 1

    ...

    def run(self) -> int:
        ...

        while queue:
            ...

            next_t = t + 1

            # if we're next to the exit, we can always move there (and are done)
            if pos == self.target:
                return next_t

            next_state = self.state_at(next_t)

            # from the starting position, there are only 2 options (neither of which could be visited yet)
            if pos == start_point:
                # we can _always_ wait on the starting point
                heappush(queue, (next_t, start_point))

                # maybe step out into the grid
                if (zeroes := (0, 0)) not in next_state:
                    heappush(queue, (next_t, zeroes))

                # nothing else to check, these are our options
                continue

            # otherwise, we must be in the grid somewhere, so we can only move to neighbors or wait
            # (or the ending, as covered above)

            # try waiting
            if pos not in next_state:
                heappush(queue, (next_t, pos))

            # try each orthogonal neighbor
            for next_move in neighbors(
                pos,
                num_directions=4,
                ignore_negatives=True,
                max_x_size=self.max_rows - 1,
                max_y_size=self.max_cols - 1,
            ):
                # don't move where there'll be a blizzard
                if next_move in next_state:
                    continue
                # don't re-add points we've tried
                if (potential_state := (next_t, next_move)) in visited:
                    continue

                # otherwise, give it a shot!
                heappush(queue, potential_state)
```

Nothing too unusual here now that setup is covered. We make a bunch of checks against the points in the next state. We also use a lot of args for the `neighbors` function to constrain our checks to `0 <= X <= max_X` (no looping or negatives). We have special cases for the start and end, but everything else is pretty standard. That's a wrap on part 1!

## Part 2

Before, we were always moving from `(0, 0)` (adjacent to our start placeholder, `(-1, -1)`) to the bottom-right corner (the max grid size). Now we'll have to make that dynamic (along with the starting time). Our `Grid` will still keep track of all the states between runs, so we're in pretty good shape. The biggest change is handling what point is considered adjacent to the starting point. We can keep using our starter placeholder, but we'll have to be a little more clever with that specific neighbor calculation.

Here's the updates we need to make:

```py
...

class Grid:
    ...

    top_left_point: GridPoint = 0, 0

    def __init__(self, raw_grid: str) -> None:
        ...

        self.bottom_right_point: GridPoint = self.max_rows - 1, self.max_cols - 1 # renamed

    # updated args
    def run(self, start_time: int, end_point: GridPoint) -> int:
        assert end_point in {self.top_left_point, self.bottom_right_point}
        ...

        queue: list[Step] = [(start_time, start_point)]

        while queue:
            ...

            # if we're next to the exit, we can always move there
            if pos == end_point:
                return next_t

            if pos == start_point:
                ...

                # the point you can move to from the start varies based on where you're headed
                if (
                    start_neighbor := self.top_left_point
                    if end_point == self.bottom_right_point
                    else self.bottom_right_point
                ) not in next_state:
                    heappush(queue, (next_t, start_neighbor))
                continue
```

The `assert` is important to ensure the staring point neighbor check below works. If there were more cases, the assert would fail and we could ensure we used something besides a ternary check.

Running the solution is pretty straightforward too:

```py
...

class Solution(TextSolution):
    def solve(self) -> tuple[int, int]:
        g = Grid(self.input)

        end_of_first_crossing = g.run(0, g.bottom_right_point)
        end_of_return_trip = g.run(end_of_first_crossing, g.top_left_point)
        end_of_second_crossing = g.run(end_of_return_trip, g.bottom_right_point)

        return end_of_first_crossing, end_of_second_crossing
```

By being able to start at any point in time and with a dynamic destination, we can run our original algorithm forwards and backwards. Do that 3 times and we have our answer(s)!
