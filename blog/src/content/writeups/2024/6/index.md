---
year: 2024
day: 6
slug: "2024/day/6"
title: "Guard Gallivant"
# concepts: []
pub_date: "2024-12-05"
---

## Part 1

Another grid! We'll parse it with the grid parser I mentioned [on day 4](/writeups/2024/day/4), which means we have a `dict[tuple[int, int], str]`, where each key is a `(row, col)` tuple. We can track the direction we're facing as the offset we add to the current location when we step:

```py
from itertools import cycle

from ...utils.graphs import parse_grid

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        OFFSETS = cycle([(-1, 0), (0, 1), (1, 0), (0, -1)])
        offset = next(OFFSETS)
```

Rather than track the current direction with an index we have to `% 4` after incrementing, we'll use `itertools.cycle`, which is an infinite generator that loops over its input. So every time we call `next(OFFSETS)`, we get the next direction in the rotation.

Next, we find our starting location from the grid and start our set of places we've stepped; we use a set because we can cross our own path, but the answer is only interested in unique locations:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        loc = next(k for k, v in grid.items() if v == "^")
        visited = {loc}
```

Now, the loop! We step once in our given direction (using `add_points`, also from [day 4](/writeups/2024/day/4)). If we've left the grid, we `break` and return the path length. If the next point is a `#`, we rotate instead of moving. Otherwise, we update our current location, add it to the path, and loop again:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while True:
            next_loc = add_points(loc, offset)
            if next_loc not in grid:
                break

            if grid[next_loc] == "#":
                offset = next(OFFSETS)
            else:
                visited.add(next_loc)
                loc = next_loc

        return len(visited)
```

## Part 2

Now we hit another classic CS problem: cycle detection! This will require some re-tooling of our part 1 code. Before, we only cared about the unique spots we walked over. For part 2, we need to track both location and direction, since crossing a path perpendicularly doesn't imply a loop. But, I like to reuse code, so we'll have to adapt the part 1 code in such a way that it still works for part 1.

Part 1 only cares about the unique locations we visited. We can track directions too, but will have to deduplicate things before returning. Let's put most of part 1 in a function and add the direction tracking without changing anything else:

```py rem={8,19,23,29} ins={3,9,20,24,30}
...

def track_guard(grid: Grid) -> int:
    OFFSETS = cycle([(-1, 0), (0, 1), (1, 0), (0, -1)])
    offset = next(OFFSETS)

    loc = next(k for k, v in grid.items() if v == "^")
    visited = {loc}
    visited: set[tuple[GridPoint, GridPoint]] = {(loc, offset)}

    while True:
        next_loc = add_points(loc, offset)
        if next_loc not in grid:
            break

        if grid[next_loc] == "#":
            offset = next(OFFSETS)
        else:
            visited.add(next_loc)
            visited.add((next_loc, offset))
            loc = next_loc

    return len(visited)
    return len({l for l, _ in visited})

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        ... # the part 1 logic was moved above
        return track_guard(grid)
```

Ok, so part 1 still passes and we'll be able to track a guard's path through any grid. This is a great first step! We added the direction to our `visited` set, but ignore it when calculating the length, so there's not significant changes yet.

Next, we should actually track loops. Besides just returning, our function now needs to communicate whether it returned because the guard exited or got caught in a loop. To know that, we actually have to track whether we're in a loop, which is as simple as bailing if we're going to step onto the exact same _position_ we've been in before. That also changes our return signature slightly:

```py rem={3,19,23,29} ins={4,12,14-17,20,24,30-32}
...

def track_guard(grid: Grid) -> int:
def track_guard(grid: Grid) -> tuple[bool, int]:
    ...

    while True:
        ...

        if grid[next_loc] == "#":
            offset = next(OFFSETS)
            visited.add((loc, offset))
        else:
            to_add = next_loc, offset
            if to_add in visited:
                # loop!
                return False, 0

            visited.add((next_loc, offset))
            visited.add(to_add)
            loc = next_loc

    return len({l for l, _ in visited})
    return True, len({l for l, _ in visited})

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        return track_guard(grid)
        exited, path_len = track_guard(grid)
        assert exited
        return path_len
```

That's loop detection working, but we're not actually throwing our guard for any loops yet. Let's fix that. An obstacle could go anywhere that doesn't already have one, so let's try brute forcing the problem and track the guard after dropping an obstacle on every possible location:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        grid = parse_grid(self.input)

        possible_obstacle_locations = 0
        for loc in grid:
            if grid[loc] != '.':
                continue

            grid[loc] = "#" # try the grid with an obstacle here
            exited, _ = track_guard(grid)
            if not exited:
                possible_obstacle_locations += 1
            grid[loc] = "." # and reset it afterwards!

        return possible_obstacle_locations
```

And that... works! But it took ~ 30 seconds to run on my machine, which is way too long. After playing with it a bit, I realized we don't have to try obstacles on every single grid location. It's only worth trying places that the guard walked in part 1. We have that info already... but it'll take a little more refactoring.

First, `track_guard` will return the actual path walked, which requires small changes in part 1:

```py rem={3,18,23,29,32} ins={4,19,24,30,33}
...

def track_guard(grid: Grid) -> tuple[bool, int]:
def track_guard(grid: Grid) -> tuple[bool, set[GridPoint]]:
    ...

    while True:
        ...

        if grid[next_loc] == "#":
            ...

        else:
            ...

            if to_add in visited:
                # loop!
                return False, 0
                return False, set()

            ...

    return True, len({l for l, _ in visited})
    return True, {l for l, _ in visited}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        exited, path_len = track_guard(grid)
        exited, path = track_guard(grid)
        assert exited
        return path_len
        return len(path)
```

Next, we can use that path as our set to check in part 2. That means we'll transition from `part_1` and `part_2` methods to a unified `solve` method. When using my [project template](https://github.com/xavdid/advent-of-code-python-template), `solve` is expected to return answers for both parts, which is useful when they share logic like this:

```py rem={4,9,12-13,15,19} ins={5,10,16,20}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        exited, path = track_guard(grid)
        assert exited
        return len(path)
        initial_path_size = len(path)

    def part_2(self) -> int: # methods are combined now
        grid = parse_grid(self.input)
        possible_obstacle_locations = 0
        for loc in grid:
        for loc in path:
            ... # unchanged

        return possible_obstacle_locations
        return initial_path_size, possible_obstacle_locations
```

And there we go! That's down to ~7 seconds, which is within my bounds of acceptable.
