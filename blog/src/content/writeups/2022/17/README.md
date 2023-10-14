---
year: 2022
day: 17
title: "Pyroclastic Flow"
slug: "2022/day/17"
pub_date: "2022-12-27"
---

## Part 1

Welcome to day 17! [That music](https://www.youtube.com/watch?v=NmCCQxVBfyM) sure sounds familiar...

On the surface, these falling blocks should be easy enough to simulate. We can define an `(x, y)` grid starting in the bottom left like so:

```
C = (0, 3)  D = (6, 3)

    |C.....D|
    |.......|
    |.......|
    |A.....B|
    +-------+

A = (0, 0)  B = (6, 0)
```

We'll want a `Block` class that consists of a points that we have move left/right/down as needed:

```py
from dataclasses import dataclass
from typing import Literal

GridPoint = tuple[int, int]
Points = set[GridPoint]

Direction = Literal["<", ">", "down"]
OFFSETS: dict[Direction, tuple[int, int]] = {"<": (-1, 0), ">": (1, 0), "down": (0, -1)}

@dataclass
class Block:
    points: set[GridPoint]

    def moved_points(self, direction: Literal["<", ">", "down"]) -> Points:
        o_x, o_y = OFFSETS[direction]
        return {(x + o_x, y + o_y) for x, y in self.points}
```

Next, we need an easy way to build a `Block` in the proper shape. We can do that with custom subclasses that generate their points based on the shape of the block:

```py
...

class Horiz(Block):
    def __init__(self, y: int):
        super().__init__({(x, y) for x in range(2, 6)})


class Plus(Block):
    def __init__(self, y: int):
        super().__init__({(3, y + 2), (2, y + 1), (3, y + 1), (4, y + 1), (3, y)})


class Angle(Block):
    def __init__(self, y: int):
        super().__init__({(2, y), (3, y), (4, y), (4, y + 1), (4, y + 2)})


class Vert(Block):
    def __init__(self, y: int):
        super().__init__({(2, y) for y in range(y, y + 4)})


class Square(Block):
    def __init__(self, y: int):
        super().__init__({(2, y), (3, y), (2, y + 1), (3, y + 1)})
```

Each block starts 2 off the left wall and its height is based on the current max height of the tower (which will get to in a sec).

Next, we our loop where we spawn blocks, blow them around, and move them down until they settle. We'll want to loop through the wind directions _and_ keep track of the next block. We can use `itertools.cycle`, which is a generator that will loop over an iterable indefinitely. We also want to track that points that comprise settled blocks and our current max height:

```py
from itertools import cycle
...

class Solution(TextSolution):
    def part_1(self) -> int:
        wind = cycle(self.input)
        blocks = cycle([Horiz, Plus, Angle, Vert, Square])
        settled: set[GridPoint] = set()
        max_y = -1
```

Now, we can drop exactly `2022` blocks. We'll be manually calling the `next` function to get the next item from our two infinite generators. Here's what that looks ike:

```py
...

def is_in_range(p: GridPoint) -> bool:
    return 0 <= p[0] < 7 and p[1] >= 0


def all_in_range(points: Points) -> bool:
    return all(map(is_in_range, points))

class Solution(TextSolution):
    def part_1(self) -> int:
        for _ in range(2022):
            block = next(blocks)(max_y + 4)  # "3 above" means + 4

            while True:
                # L/R
                new_points = block.moved_points(cast(Direction, next(wind)))
                if new_points.isdisjoint(settled) and all_in_range(new_points):
                    block.points = new_points

                # down
                new_points = block.moved_points("down")
                if new_points.isdisjoint(settled) and all_in_range(new_points):
                    block.points = new_points
                else:
                    break
```

For each move, we check both that the new points are in the walls _and_ don't intersect any of the existing settled blocks; good thing we have a big `set` of those! Note that we only break out of the loop in the second case, when there was a downward motion.

Lastly, we add our about-to-settle blocks to the set and re-calculate the height of the tower:

```py
...

@dataclass
class Block:
    ...

    @property
    def highest_point(self) -> int:
        return max(y for _, y in self.points)

class Solution(TextSolution):
    def part_1(self) -> int:
        for _ in range(2022):
            ...

            # |= is the equivalent of +=, but uses `set_a | set_b` instead of `+`
            settled |= block.points
            max_y = max(max_y, block.highest_point)

        # an extra 1, since we're storing the 0-indexed top point of the tower,
        # not the actual height
        return max_y + 1
```

## Part 2

Well, whenever you write `range(1_000_000_000_000)`, you know you're in for a bad time. Instead of actually running our loop again in full, we have to find when the tower repeats. At some point, the shape of the tower _must_ repeat. If we find that point, we can save ourselves _many_ loops.

To find the loop, we have to track the state of the tower each time we drop a new block. As we start a block, if we've been in this state before, we can see how many blocks are in each loop and do some math. A starting state is unique based on:

- the block shape
- our progress through the wind instructions
- the top row of the tower

If all 3 of those are the same as we've seen before, then the block we're about to drop will fall the same and so will all the others after it (until we loop again). So, we need to track all those values:

```py
...

class Solution(TextSolution):
    # our part 1 code, moved into a method
    def simulate_blocks(self, num_blocks: int) -> int:
        ...
        # wrap in `enumerate`, so we can track our process through the list
        wind = cycle(enumerate(self.input))
        wind_index = 0

        # renamed from `settled`
        settled_points: set[GridPoint] = set()

        settled_lines: dict[int, str] = {-1: "1111111"}  # floor
        max_y = -1  # below the floor

        # block_name, wind_index, top_row_value => block_num, max_y
        start_states: dict[tuple[str, int, str], tuple[int, int]] = {}

        def line_value(line: int) -> str:
            return "".join(str(int((x, line) in settled_points)) for x in range(7))

        ...
```

This includes a function to translate a `y` value into a 7-digit string, representing the state of that row. With those initialized, we can store states as we drop blocks:

```py
...

@dataclass
class Block:
    ...

    @property
    def name(self):
        return self.__class__.__name__ # 'Horiz', 'Plus', etc

...

class Solution(TextSolution):
    def simulate_blocks(self, num_blocks: int) -> int:
        ...

        for block_number in range(num_blocks):
            block = next(blocks)(max_y + 4)  # "3 above" means + 4

            state = (block.name, wind_index, settled_lines.get(max_y, "not found"))

            start_states[state] = (block_number, max_y)

            while True:
                # drop blocks; pt 1
                ...

            # update settled_points, max_y
            ...

            settled_lines[max_y] = line_value(max_y)
```

As we go, we're generating the `state` before we drop the block and saving the current state of the top of the tower (# blocks, height). We also update state of the top of the tower (it may have changed based on the block we just dropped).

Next, we have to check our state against the previous states. If we've found a match, we can calculate the size of the loop:

```py
...

class Solution(TextSolution):
    def simulate_blocks(self, num_blocks: int) -> int:
        ...

        for block_number in range(num_blocks):
            ...

            state = ...

            if (previous_state := start_states.get(state)) and block.name == "Horiz":
                blocks_per_loop = block_number - previous_state[0]
                height_per_loop = max_y - previous_state[1]

                print(
                    f"Loop starting at block #{block_number}. Consists of {blocks_per_loop} blocks, which add {height_per_loop} height each. Current height is {max_y.}"
                )

            ...
```

Running this on the test input gives us `Loop starting at block #55. Consists of 35 blocks, which add 53 height each. Current height is 88`. Now that we know the pattern, we can skip as many loops as we want. Knowing this, let's work through part 1 of the example, since "1 trillion" is harder to reason about.

We know we need the height after `2022` blocks. Starting with block number `55`, we can skip `35` blocks at a time and instead add `53` to the height of the tower. If we divide the number of blocks remaining by the size of our loop, we know how many loops we can safely skip. In our case, that's `(2022 - 55) // 35`, or `56`. So, instead of starting block `55`, we can skip straight to block `55 + 56 * 35`, which is `2015`. We also have to (eventually) add `56 * 53` (`2968`) to our height.

Now that we've skipped ahead, we keep dropping blocks like normal until we get to the requested number. Those 7 remaining blocks (`2022 - 2015`) add an additional `11` height to the `88` we had before the skip. All together, that's `11 + 88 + 2968`, plus the `1` to convert from index to actual height, and we've got `3068`, the example answer form part 1!

If that all makes sense, we can code it up!

```py
...

class Solution(TextSolution):
    def simulate_blocks(self, num_blocks: int) -> int:
        ...

        height_to_add = 0

        ...

        # switch from `range` to a manual tracker, so we jump
        block_number = 0
        while block_number < num_blocks:
            ...

            state = ...

            if (
                (previous_state := start_states.get(state))
                and block.name == "Horiz"
                and height_to_add == 0
            ):
                blocks_per_loop = block_number - previous_state[0]
                loops_to_skip = (num_blocks - block_number) // blocks_per_loop
                block_number += loops_to_skip * blocks_per_loop

                height_per_loop = max_y - previous_state[1]
                height_to_add = loops_to_skip * height_per_loop

            elif height_to_add == 0:
                # only track these before we've found a loop
                start_states[state] = (block_number, max_y)

            # drop blocks
            ...

        # settle blocks, update tracking variables
        ...

        return max_y + height_to_add + 1

    def part_1(self) -> int:
        return self.simulate_blocks(2022)

    def part_2(self) -> int:
        return self.simulate_blocks(1_000_000_000_000)
```

And that'll do it! Definitely took some time to wrap our heads around, but it ultimately wasn't too bad.
