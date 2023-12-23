---
year: 2023
day: 16
slug: 2023/day/16
title: "The Floor Will Be Lava"
pub_date: "2023-12-22"
---

## Part 1

We're parsing grids once again, so [Day 10](/writeups/2023/day/10/)'s `parse_grid` to the rescue. Today we'll forego ignoring any characters and instead store every valid point. We'll have to store many more keys but it'll greatly simplify any bounds checking we need to do.

My plan for part 1 is to brute force it. We'll walk along the path of the light until we run off the grid. If we keep track of the squares we pass through, we can build the `set` of points, our answer. Also, note that the paths are deterministic. That gives us two important properties:

1. A `State` can determine its next state(s) based solely on the character from the grid
2. Once we've seen a state (location + direction), we can bail; everything on that path will already have been accounted for.

Let's code this up!

```py
from dataclasses import dataclass
from enum import Enum

GridPoint = tuple[int, int]


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


@dataclass(frozen=True)
class State:
    loc: GridPoint
    facing: Direction

   def next_states(self, char: str) -> list["State"]:
        ... # TODO
```

Straightforward so far! We're finally using dataclasses, one of my [favorite Python features](https://xavd.id/blog/post/python-dataclasses-from-scratch/). It provides a nice, immutable (important so we can put these in a `set`) container that we can add methods to. We also group our directions in an `Enum` for easy readability and comparability.

Before we implement the rest of `State`, let's write the bones of our actual solution function so we know where we're headed.

Ultimately, we need to explore every light beam to its conclusion. Beams can split, so we'll queue up states we need to explore as we go. For each `State` in the queue, we'll add any in-bounds state(s) to the queue and keep going. Everything will eventually loop or hit a wall, at which point our queue will be empty and we can total up our result. Here's that code:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)

        seen: set[State] = set()
        queue: list[State] = [State((0, 0), Direction.RIGHT)]

        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)

            for next_state in current.next_states(grid[current.loc]):
                if next_state.loc in grid:
                    queue.append(next_state)

        return len({state.loc for state in seen})
```

I really like the separation of concerns here- `State` doesn't know anything about the grid or its bounds and the `grid` maintains no state. Also, here's the payoff for using a full grid instead of a sparse one: there's no tricky bounds checking to ensure `0 <= next_state[1] < len(self.input[0])`. We know every single valid point at the start, so if it's not in the grid, it must be out of bounds. We also handled bailing early for states we've seen and can count all the points we ever hit. Not bad, right? Now for the good stuff: calculating the next states.

A `State` knows its location and the direction it's facing. Given the character it's standing on, we can always calculate what happens next. Let's start with the easy one: when we're on a `.`, we take a step in our current direction. The new location can be derived from our current direction and a 1-unit offset that changes our `row` or `col`. Let's add those helpers:

```py ins={3-8,14-16,18-19,22-28}
...

ROW_COLL_OFFSETS: dict[Direction, GridPoint] = {
    Direction.UP: (-1, 0),
    Direction.RIGHT: (0, 1),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
}

class State:
    loc: GridPoint
    facing: Direction

    @property
    def next_loc(self) -> GridPoint:
        return add_points(self.loc, ROW_COLL_OFFSETS[self.facing])

    def step(self) -> "State":
        return State(self.next_loc, self.facing)

    def next_states(self, char: str) -> list["State"]:
        match char:
            case ".":
                return [self.step()]
            case _:
                raise ValueError(
                    f"Unable to calculate next step from {self} and {char=}"
                )
```

> Note that `add_points` is also from [Day 10](/writeups/2023/day/10/); I've added it to my utils for future use. It adds 2-tuples of `int`s together.

It's a fair number of lines to add in one go, but it's all fairly simple. I'm personally excited to use Python's new(ish) [structural pattern matching](https://peps.python.org/pep-0636/). Per usual, I added a default case to the end to make sure unknown states alert us (loudly).

Next, we'll handle the case where we pass through the pointy end of a splitter. It's the same result as above: we step forward with. Patterns can be matched conditionally, so we'll do that:

```py ins={10-14}
...

class State:
    ...

    def next_states(self, char: str) -> list["State"]:
        match char:
            ...

            # ignore the pointy end of a splitter
            case "-" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.step()]
            case "|" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.step()]
```

We can't use multiple conditionals in the same case, but that honestly helps readability.

Next is mirrors. I made a bunch of diagrams with my fingers to determine how simple we could make the logic and it turns out: pretty simple! A light traveling horizontally will always turn counterclockwise when it hits `/` and clockwise when they encounter `\`, which is a convenient pattern. Vertical light is the exact opposite.

So that's easy enough, but there's an issue. We calculate our next state based on our current position. If we keep standing on the mirror and rotate, we'll just spin indefinitely. Instead, we need to rotate and _then_ step to some new spot. This calls for rotation tech _and_ a new helper:

```py ins={3,11-14,24-25}
...

Rotation = Literal["CCW", "CW"]

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    @staticmethod
    def rotate(facing: "Direction", towards: Rotation) -> "Direction":
        offset = 1 if towards == "CW" else -1
        return Direction((facing.value + offset) % 4)

...

class State:
    ...

    def step(self) -> "State":
        return State(self.next_loc, self.facing)

    def rotate_and_step(self, towards: Rotation):
        return State(self.loc, Direction.rotate(self.facing, towards)).step()
```

`Direction.rotate` gets the `int` from the `Enum` and does the classic modulo math to turn through the cardinal directions before turning the int back into a `Direction`. `State.rotate_and_step` makes a `State` facing the direction before calling `step`, ensuring we're facing the way we expect before going anywhere.

Those in hand, our mirror logic is straightforward:

```py ins={10-50}
...

class State:
    ...

    def next_states(self, char: str) -> list["State"]:
        match char:
            ...

            # bounce off mirrors
            case "/" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate_and_step("CCW")]
            case "\\" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.rotate_and_step("CW")]
            case "/" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate_and_step("CW")]
            case "\\" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.rotate_and_step("CCW")]
```

All that remains is splitting, which is comprised entirely of things we've already built! Both vertical and horizontal light behave the same on a splitter they're not skipping: they duplicate, one in each direction. We've always returned lists for consistency's sake, and this is why:

```py ins={15-50}
...

class State:
    ...

    def next_states(self, char: str) -> list["State"]:
        match char:
            ...

            # ignore the pointy end of a splitter
            case "-" if self.facing in (Direction.LEFT, Direction.RIGHT):
                return [self.step()]
            case "|" if self.facing in (Direction.UP, Direction.DOWN):
                return [self.step()]
            # split on splitters we didn't pass over
            case "-" | "|":
                return [
                    self.rotate_and_step("CCW"),
                    self.rotate_and_step("CW"),
                ]
```

Because only the first case matches, any splitter we didn't skip we must be hitting the broad side of. So we don't have to check directionality at all.

And that'll actually do it for part 1! Our queue handles skipping duplicates and out-of-bounds and now our `State`s can step and replicate, so we'll get our answer.

## Part 2

In typical fashion, we're now running part 1 a bunch. Let's move it to a function:

```py del={4,7} ins={5,8,13}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def _solve(self, grid: Grid, start: State) -> int:
        seen: set[State] = set()
        queue: list[State] = [State((0, 0), Direction.RIGHT)]
        queue: list[State] = [start]
        ...

    def part_1(self) -> int:
        grid = parse_grid(self.input)
        return self._solve(grid, State((0, 0), Direction.RIGHT))
```

Now we work our way around the edge of the grid, calling `_solve` (our part 1 code) from every possible start location:

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        grid = parse_grid(self.input)

        assert len(self.input) == len(self.input[0]), "not a square grid!"
        grid_size = len(self.input)

        return max(
            # top, facing down
            *(
                self._solve(grid, State((0, col), Direction.DOWN))
                for col in range(grid_size)
            ),
            # right, facing left
            *(
                self._solve(grid, State((row, grid_size - 1), Direction.LEFT))
                for row in range(grid_size)
            ),
            # bottom, facing up
            *(
                self._solve(grid, State((grid_size - 1, col), Direction.UP))
                for col in range(grid_size)
            ),
            # left, facing right
            *(
                self._solve(grid, State((row, 0), Direction.RIGHT))
                for row in range(grid_size)
            ),
        )
```

It's important for this specific code that we ensure the grid is square. Otherwise, we'd have to use different lengths for the top and sides (which would be fine, but it's good to codify assumptions). Past that, it's some fairly typical comprehensions.

It takes ~ 4.6 seconds, but it gets the right answer! That's outside the time budget I like to give myself though, so let's see if we can speed it up.

## Gotta Go Fast

My [project template](https://github.com/xavdid/advent-of-code-python-template) has built-in support for profiling a solution, so let's see what we get:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      441    3.052    0.007   12.891    0.029 solution.py:94(_solve)
15568960/9363181    1.701    0.000    2.376    0.000 {built-in method builtins.hash}
  3491401    1.286    0.000    1.286    0.000 <string>:2(__init__)
  3157398    1.116    0.000    4.066    0.000 solution.py:52(step)
  9363181    1.025    0.000    1.633    0.000 enum.py:1251(__hash__)
  6205779    0.984    0.000    3.155    0.000 <string>:2(__hash__)
  3157398    0.934    0.000    1.779    0.000 solution.py:48(next_loc)
  3072491    0.654    0.000    5.404    0.000 solution.py:60(next_states)
```

It makes sense that most of the program's time is spent in `_solve`, that's where our loops are. We can also see that we're spending a lot of time:

1. `hash`ing things (`built-in method builtins.hash`), which also shows up as `enum.py:1251(__hash__)` and `<string>:2(__hash__)`
2. calculating next states (`step`, `next_loc`, etc)

The built-in `hash` function is used when adding objects to `dict`s or `set`s. An object's hash is deterministic, so it's how Python determines uniqueness. This is why items used as `dict` keys or `set` items must be immutable and why the error for violating this is `TypeError: unhashable type`.

Reading this, I was a little confused- I didn't think I was hashing any strings. The only thing that was being stored in a set (in volume) was my `State`, which is a tuple and an `enum`. Well, it turns out that by default, `Enum`s are hashed [based on their name](https://github.com/python/cpython/blob/c3f92f6a7513340dfe2d82bfcd38eb77453e935d/Lib/enum.py#L1278-L1279), meaning I was storing `'UP'`, `'DOWN'`, etc. Our first performance improvement is swapping `Enum` to `IntEnum`, which will hash based on the member's numerical value (which is much faster):

```py del={1,6} ins={2,7}
from enum import Enum
from enum import IntEnum

...

class Direction(Enum):
class Direction(IntEnum):
    ...
```

No other code changes are required, this Just Works. It brings my runtime to ~ 3.8 seconds, roughly a 17% increase.

Another tactic is to switch from dataclasses to `NamedTuple`s. The former is written in Python while the latter is in C (which is basically always faster). That's also a drop-in replacement:

```py del={1,6,7} ins={8} ins=", NamedTuple"
from dataclasses import dataclass
from typing import Literal, NamedTuple

...

@dataclass(frozen=True)
class State:
class State(NamedTuple):
    ...
```

Doing that by itself (and keeping regular `Enum`) got me to ~ 3.5 seconds of runtime (24% faster). Doing _both_ gets us to ~ 2.8 seconds, a respectable 39% speed increase over our first attempt. This is an improvement, but it's still a little slow for my taste.

Besides hashing, the other place we were spending a lot of time budget was calculating the next state. A given position and direction will _always_ generate the same next state, regardless of where we started the run. What if we could save some of that work between runs? What if we just... slapped a cache on that thing?

```py ins={1,8}
from functools import cache
...

@dataclass(frozen=True)
class State:
    ...

    @cache
    def next_states(self, char: str) -> list["State"]:
        ...
```

The caching happens at the `class` level, so it's shared between runs. _That_ 1-line change (by itself) gets us down to ~ 2.6 seconds (43% improved), marginally our best yet. But why settle?

The best news is that none of these solutions are mutually exclusive. Apply them all (`IntEnum`, `NamedTuple`, and `@cache`) and we hit ~ 1.1 second, a full 75% faster than our initial solution. We could probably get it even faster with the `Pool` trick from [Day 12](/writeups/2023/day/12/), but I think this is finally plenty fast.
