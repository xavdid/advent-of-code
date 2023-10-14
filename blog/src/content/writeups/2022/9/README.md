---
year: 2022
day: 9
title: "Rope Bridge"
slug: "2022/day/9"
pub_date: "2022-12-10"
---

## Part 1

Though it may look like we want to create a grid today, we don't actually need to. Instead, each rope knot will have a position, represented by a 2-tuple. The starting position is `(0,0)` and `x` and `y` increase to the right and up, respectively (just like the grid you learned in grade school).

Past that, I wasn't quite sure where to start; the prompt described the algorithm well enough, but I didn't have a clear picture in my head of how to solve the whole thing. So, I started adding functions for what I knew I'd need and would see where that took me.

I knew that I'd have 2 ropes objects, and I'd be adding offsets to them to move them around. So, I needed a way to translate the instructions into offsets:

```py
from typing import Tuple

GridPoint = Tuple[int, int]

def get_offset(direction: str) -> GridPoint:
    if direction == "U":
        return 0, 1
    if direction == "R":
        return 1, 0
    if direction == "D":
        return 0, -1
    if direction == "L":
        return -1, 0

    raise ValueError("unrecognized direction")
```

Next, our `RopeEnd` class, representing a bit of the rope that moves. It takes a starting position, can repeat its location, and can move around. We'll use a dataclass, one of my [favorite Python features](https://xavd.id/blog/post/python-dataclasses-from-scratch/):

```py
from dataclasses import dataclass

...

@dataclass
class RopeEnd:
    x: int
    y: int

    @property
    def loc(self):
        return self.x, self.y

    def move(self, offset: GridPoint):
        self.x += offset[0]
        self.y += offset[1]
```

Now we can start filling in our solution:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        head = RopeEnd(0, 0)
        tail = RopeEnd(0, 0)
        locations: Set[Tuple[int, int]] = {(0, 0)}

        for line in self.input:
            direction, distance_str = line.split()
            head_offset = get_offset(direction)
            for _ in range(int(distance_str)):
                head.move(head_offset)

                # TODO


        return len(locations)
```

This is our basic setup- the head of rope moves around following the instructions. Moves are calculated as a `GridPoint` plus an offset (which is also a 2-tuple).

What remains is deciding when tail needs to move. Based on the prompt, the tail should move when the head is 2 away in any direction. We can build that into our class, plus a method to get the distance between two points:

```py
@dataclass
class RopeEnd:
    ...

    def offset(self, other: "RopeEnd") -> Tuple[int, int]:
        return self.x - other.x, self.y - other.y

    def too_far(self, other: "RopeEnd") -> bool:
        x, y = self.offset(other)
        return abs(x) > 1 or abs(y) > 1
```

The last piece we need is to calculate the tail's offset once we know we should move, which is part that took me the longest. There are two major cases:

1. the offset is a combination of (maybe negative) `2` and `0`, so the tail needs to move `1` in a single direction
2. the offset is a combination of `2` and `1` (each of which could be negative). The tail should move `1` in each direction (either or both of which could be negative).

So, I wrote a function to cover each case:

```py
def squish_offset(i: int) -> int:
    if i == 0:
        return 0

    if i > 0:
        return i - 1

    return i + 1


def squish_big_offset(i: int) -> int:
    mult = 1 if i > 0 else -1
    if abs(i) == 2:
        return (abs(i) - 1) * mult
    return i
```

It's not the most elegant, but it _does_ work. We'll clean it up later. Lastly, we call it:

```py
def get_catchup_offset(head: RopeEnd, tail: RopeEnd) -> Tuple[int, int]:
    x, y = head.offset(tail)
    # either (2, 0) or (2, 1) in any order, with negatives
    assert (
        abs(x) == 2 or abs(y) == 2
    ), f"should be at most 2 away in any one direction (got {x, y})"
    if x == 0 or y == 0:
        return squish_offset(x), squish_offset(y)

    assert abs(x) == 1 or abs(y) == 1
    return squish_big_offset(x), squish_big_offset(y)
```

I sprinkled some assertions in to make sure I was calling the function with what I expect.

Finally, we can string it all together:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
       ...

        for line in self.input:
            ...
            for _ in range(int(distance_str)):
                head.move(head_offset)
                if head.too_far(tail):
                    tail_offset = get_catchup_offset(head, tail)
                    tail.move(tail_offset)
                    locations.add(tail.loc)

        return len(locations)
```

Each time head moves, we check if tail should move. If it does, we calculate the offset, move it, and store its location in a set. There's our part 1!

## Part 2

Part 2 involved a larger rope. This isn't much harder, but we _will_ benefit from some code re-cleanup. Let's start with our offsets calculations. I knew there was a more elegant way to write them, but it didn't click into place until I added a comment about their inputs and outputs:

```py
def squish_offset(i: int) -> int:
    """
    takes either 0, 2, or -2 and returns 0, 1, or -1 respectively
    """
    ...


def squish_big_offset(i: int) -> int:
    """
    takes 2, -2, 1, or -1 and returns 1, -1, 1, or -1 respectively
    """
    ...
```

We need to match the sign and return 1, -1, and 0 depending on the input. Much clearer than what I had originally:

```py
def squish_offset(i: int) -> int:
    if i > 0:
        return 1
    if i < 0:
        return -1
    return 0
```

The other big change is that instead of 2 ropes, we have 10 of them. It's no longer feasible to keep track of each individually in `head` and `tail` variables, so we'll load them into a list. This also means we should modify our class to keep track of its own location. We also know that they always start at `(0, 0)`, so we can provide those as defaults:

```py
from dataclasses import dataclass, field

...

@dataclass
class RopeEnd:
    x: int = 0
    y: int = 0
    locations: Set[GridPoint] = field(default_factory=lambda: {(0, 0)})

    ...

    def move(self, offset: GridPoint):
        self.x += offset[0]
        self.y += offset[1]
        self.locations.add(self.loc)
```

We have to use the `default_factory` because dataclasses can't take mutable types as parameters (just like defaults in functions); you can [read more here](https://docs.python.org/3/library/dataclasses.html#mutable-default-values).

We should also move our whole part 1 solution into a function that we can call with a rope size:

```py
class Solution(StrSplitSolution):
    def simulate_rope(self, rope_size: int) -> int:
        rope = [RopeEnd() for i in range(rope_size)]

        ...
```

Our code here is mostly the same, but I moved the `too_far` function off the class an to a standalone function that takes a pre-calculated offset:

```py
def should_move(o: GridPoint) -> bool:
    return abs(o[0]) > 1 or abs(o[1]) > 1

class Solution(StrSplitSolution):
    def simulate_rope(self, rope_size: int) -> int:
        rope = [RopeEnd() for i in range(rope_size)]

        for line in self.input:
            direction, distance_str = line.split()
            head_offset = get_offset(direction)

            for _ in range(int(distance_str)):
                rope[0].move(head_offset)
                for a, b in zip(rope, rope[1:]):
                    tail_offset = a.offset(b)
                    if should_move(tail_offset):
                        b.move(tuple(map(squish_offset, tail_offset)))

        return len(rope[-1].locations)

    def part_1(self) -> int:
        return self.simulate_rope(2)

    def part_2(self) -> int:
        return self.simulate_rope(10)
```

The big change is that we use `zip` to iterate through each pair of rope segments in order. Then we report the locations of the last one. This will work for ropes of any length, so go nuts!
