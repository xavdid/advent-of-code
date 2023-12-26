---
year: 2023
day: 17
slug: 2023/day/17
title: "Clumsy Crucible"
pub_date: "2023-12-25"
---

## Part 1

When you see "efficient pathfinding", [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) is a good place to start! There are a number of other options (like [A\*](https://en.wikipedia.org/wiki/A*_search_algorithm)), but I've got a soft spot for this one.

Like [yesterday](/writeups/2023/day/16/), we'll be parsing a grid and "walking" around it. I've gone ahead and promoted that `Direction` enum to my graph utils so we'll be using it again. It'll cover our rotations and offsets:

```py
from enum import IntEnum

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
```

Dijkstra's is a simple and elegant algorithm. I've [covered](/writeups/2022/day/12/) [many](/writeups/2022/day/16/) [times](/writeups/2022/day/24/) before. Check those out if you want to know the nuts and bolts of the approach. Today I'm going to focus on what makes this puzzle unique: having to track direction and steps taken.

Normally Dijkstra is only concerned with the cost to reach a position. But because there are restrictions on how far we can travel today, we have to track our current heat level and direction (which informs which neighbors we can move to). Our `State` will be `tuple[int, Position, int]`, which holds:

- tracking cost (aka heat)
- a `Position` class that knows our location and direction (copied [yesterday](/writeups/2023/day/16/)'s `State` class and removed its `next_states`)
- the number of steps taken in this direction

Let's get the high level parts of our solution down:

```py
from heapq import heappop, heappush
...

State = tuple[int, Position, int]


class Solution(StrSplitSolution):
    def part_1(self) -> int:
        # bottom-right corner of the grid
        target = len(self.input) - 1, len(self.input[-1]) - 1
        grid = {k: int(v) for k, v in parse_grid(self.input).items()}

        # start walking both directions
        queue: list[State] = [
            (0, Position((0, 0), Direction.DOWN), 0),
            (0, Position((0, 0), Direction.RIGHT), 0),
        ]
        seen: set[tuple[Position, int]] = set()

        while queue:
            cost, pos, num_steps = heappop(queue)

            if pos.loc == target:
                return cost

            if (pos, num_steps) in seen:
                continue
            seen.add((pos, num_steps))

            # TODO: queue states

        return -1
```

We build a list of `State` objects and add/remove items using Python's built-in `heapq` class (a priority queue implementation; [docs](https://docs.python.org/3/library/heapq.html)). Whenever we consider a `State`, because the queue is always sorted, we know we have the cheapest way to reach that point (and direction and number of steps left).

If that state's location is the target, we're done and must have found the fastest way there! If we've been to this location after the same number of steps before, we can skip it (we must have been here at a worse cost, which isn't useful). We don't have to track direction because it doesn't matter how we landed on this position- we can always turn (at least). We finish the "checks" part by adding this point as visited and queue next steps.

To queue steps, we check if that move is valid. It's valid if it's in-grid and (if moving forward) we've gone less than 2 steps in this direction. That's not too bad thanks to the `step`, `rotate_and_step`, and Python's walrus operator (which lets us bind variables inside other expressions):

```py ins={11-12,14-15,17-18}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while queue:
            cost, pos, num_steps = heappop(queue)
            ...

            if (left := pos.rotate_and_step("CCW")).loc in grid:
                heappush(queue, (cost + grid[left.loc], left, 1))

            if (right := pos.rotate_and_step("CW")).loc in grid:
                heappush(queue, (cost + grid[right.loc], right, 1))

            if num_steps < 3 and (forward := pos.step()).loc in grid:
                heappush(queue, (cost + grid[forward.loc], forward, num_steps + 1))
```

Each time we turn, we reset `num_steps` back to `1`. Otherwise, if we're still under 3 steps, we increment `num_steps` and move forward. By only adding states that conform to the rules, we don't have to do any validity checking when _reaidng_ points, only writing them. This will think for a second or so and we'll have our answer for part 1!

## Part 2

Part 2 is much the same as part 1, but our parameters for the min and max travel distance have changed. We can actually do this is about 3 lines:

```py del={4} ins={5,34,36-37} ins="num_steps >= min_steps" ins="num_steps < max_steps and "
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def _solve(self, min_steps: int, max_steps: int) -> int:
        ...

        while queue:
            cost, pos, num_steps = heappop(queue)

            if pos.loc == target and num_steps >= min_steps: # 1
                return cost

            ...

            if (
                num_steps >= min_steps # 2
                and (left := pos.rotate_and_step("CCW")).loc in grid
            ):
                heappush(queue, (cost + grid[left.loc], left, 1))

            if (
                num_steps >= min_steps # 2
                and (right := pos.rotate_and_step("CW")).loc in grid
            ):
                heappush(queue, (cost + grid[right.loc], right, 1))

            if num_steps < max_steps and (forward := pos.step()).loc in grid: # 3
                heappush(queue, (cost + grid[forward.loc], forward, num_steps + 1))

        return -1

    def part_1(self) -> int:
        return self._solve(0, 3)

    def part_2(self) -> int:
        return self._solve(4, 10)
```

The changes:

1. we can only land on the target if we've gone the minimum number of steps
2. we can't turn unless we're past our minimum
3. we only step forward if we're under the minimum (just like part 1)

Not so bad, overall. Unfortunately, this runs both parts in ~ 8.5 seconds, which is way longer than I want. I could queue way fewer points if I jump forward by `min_steps` and collect the head along the way. I might also be able to get away with storing a simpler state, but some light experimentation with that hasn't been promising. I may circle back, but I may leave this one here for now.
