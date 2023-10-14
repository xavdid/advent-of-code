---
year: 2021
day: 22
title: "Reactor Reboot"
slug: "2021/day/22"
pub_date: "2022-01-02"
---

## Part 1

Another suspiciously simple part 1. Honestly, the hardest thing to write concisely is the input parsing. We'll start there:

```py
from typing import List, Tuple
Instruction = Tuple[bool, Tuple[range, range, range]]

signed_int = r"(-?\d+)"

def parse_input(self) -> List[Instruction]:
    results = []
    for line in self.input:
        action, raw_bounds = line.split(" ")
        bounds = [
            map(int, x)
            for x in re.findall(fr"[xyz]={signed_int}..{signed_int}", raw_bounds)
        ]
        results.append((action == "on", tuple(range(l, h + 1) for l, h in bounds)))
    return results
```

This is a couple of neat tricks:

- we can declare a little part of a regex as a variable
- we can parse each pair as ints
- we can build and return our ranges from those pairs; the high end is 1 more than where we actually want to stop

Once we have each instruction, we can store each 3-d coordinate as the key in dict with the value as the on/off bool. The result is the number of `True`s in the `dict` at the end:

```py
    cores = {}
    for result, ranges in self.parse_input():
        # 51 on the top end because python ranges don't include the stop
        if not all(-50 <= r.start and r.stop <= 51 for r in ranges):
            continue

        for coord in product(*ranges):
            cores[coord] = result

    return len([x for x in cores.values() if x])
```

With that done, we have to figure out what we're doing about these _huge_ ranges.

## Part 2

Rather than thinking of these ranges as many points, we'll need to treat them as large, continuous blocks; each one has volume. The volume of a block is it's length (`x`) times width (`y`) times height (`z`). The volume of 2 (or more) blocks is their volume added together, minus the volume of any part where they overlap. Here's what that would look like in 2D:

```
     -------
    |       |
    |   B   |
 -------    |
|   |A+B|   |
|    ---|---
|   A   |
|       |
 -------
```

You'd calculate that as `A + B - (A+B)`. Things are a little trickier with a third area:

```
         ------------
        |           |
        |           |
        |     C     |
     -----------    |
    |   |  B+C  |   |
    |    -----------
 -------        |
|   |A+B|   B   |
|    ---|-------
|   A   |
|       |
 -------
```

Now the volume is `A + B - (A+B) + C - (B+C)`. This gets more complex if `A` also intersected `C` at some point, and so on. We can generalize this to:

> The unique volume of a cube is its volume minus the volume of any overlaps it has with other cubes

and thus the volume of the whole input is:

> the sum of the unique volume of every cube

Doesn't seem so bad all of the sudden! It's made _slightly_ more complex by some of the cubes being "off" instead of "on", but we'll get to that when we need it.

In the meantime, let's start with a `Box` class. It'll hold the ranges and some simple methods:

```py
from dataclasses import dataclass
from functools import reduce
from operator import mul

def product(values: List[int]) -> int:
    return reduce(mul, values, 1)

@dataclass(frozen=True)
class Box:
    x: range
    y: range
    z: range
    on: bool = True

    @property
    def is_small(self) -> bool:
        return all(-50 <= r.start and r.stop <= 51 for r in self.ranges)

    @property
    def ranges(self):
        yield self.x
        yield self.y
        yield self.z

    def start(self, direction: Union[Literal["x"], Literal["y"], Literal["z"]]) -> int:
        """
        little helper to do the start-of-range that matches `.end`
        """
        return cast(range, getattr(self, direction)).start

    def end(self, direction: Union[Literal["x"], Literal["y"], Literal["z"]]) -> int:
        """
        little helper to do the end-of-range math right
        """
        return cast(range, getattr(self, direction)).stop - 1

    @property
    def volume(self) -> int:
        return product([len(r) for r in self.ranges])
```

At first, I was using `self.x.start` and `self.x.end` for range math, but the `end` always needs a `- 1`, so I put it in a helper. But then I didn't like that I used `self.x.start` and `self.end('x')`, so I added a matching `start` helper. This is how weird legacy code happens, and I apologize.

The only other neat thing is `ranges`- here we manually create a generator by yielding a few things and nothing more. This allows the `for x in self.ranges` to look nice and normal.

Now, the important one. Given a box and a second box, we need to get the overlapping region. conveniently, we can also express that region as a `Box`:

```py
class Box:
    ...

    def overlap(self, other: "Box") -> Optional["Box"]:
        """
        Returns a box describing the overlap between two other boxes
        (or `None` if the boxes don't intersect)
        """
        overlap_min_x = max(self.start("x"), other.start("x"))
        overlap_max_x = min(self.end("x"), other.end("x"))
        overlap_min_y = max(self.start("y"), other.start("y"))
        overlap_max_y = min(self.end("y"), other.end("y"))
        overlap_min_z = max(self.start("z"), other.start("z"))
        overlap_max_z = min(self.end("z"), other.end("z"))

        if (
            overlap_min_x > overlap_max_x
            or overlap_min_y > overlap_max_y
            or overlap_min_z > overlap_max_z
        ):
            return None

        return Box(
            range(overlap_min_x, overlap_max_x + 1),
            range(overlap_min_y, overlap_max_y + 1),
            range(overlap_min_z, overlap_max_z + 1),
        )
```

Let's look back at our example from above and walk through the logic:

```
         ------------
        |           |
        |           |
        |     C     |
     -----------    |
    ^   |  B+C  |   |
    ^    -----------
 -------        |
|   ^A+B*   B   |
|    ---*-------
|   A   *
|       *
 -------
```

The biggest starting value of `x` for boxes A and B (`overlap_min_x`) is marked above as `^`. The smallest ending value of `x` is marked as `*` (`overlap_max_x`). Because the overlap's `max` is greater than its `min`, we know it they overlap (in that dimension). On the other hand, the top of `A` is less than the bottom of `C`, so those two boxes will return `None` when compared.

Make sure to walk through that code and understand how and _why_ it works before moving on.

Now, we can get the overlap between two boxes. So, for a given box, we should be able to calculate its "unique volume" using the method described above. It's volume, plus that of all the others, minus all the overlaps. Here's how that looks:

```py
def all_overlaps(root: Box, rest: List[Box]) -> Set[Box]:
    """
    given a box, return a set of all of the overlaps that box has with the rest of the provided ones
    """
    result = set()
    if not rest:
        return result

    for box in rest:
        overlap = root.overlap(box)
        if overlap:
            result.add(overlap)

    return result

def total_volume(boxes: List[Box]) -> int:
    if not boxes:
        return 0

    root, *rest = boxes
    overlaps = all_overlaps(root, rest)

    return root.volume + total_volume(rest) - total_volume(overlaps)
```

Just like we said: the unique volume of this box is the volume of all of the others minus their overlaps. We recurse through the list of boxes for each box down the line. We can't cache this, unfortunately, because `all_overlaps(A, [B,C])` is going to give a different result than `all_overlaps(B, [C])`. But, it's a short-ish list, so it doesn't take too long (we're just doing integer math, which is quite fast). We also only have to go one direction. Our function calls are:

- `all_overlaps(A, [B,C,D])`
- `all_overlaps(B, [C,D])`
- `all_overlaps(C, [D])`
- `all_overlaps(D, [])`

We don't call `all_overlaps(C, [A,B,D])` like you might expect. That's because the overlap between `A` and `C` is calculated when `A` is the root, so we don't need to re-do it when `C` is the root.

There's one last wrinkle- the "off" boxes. If we hit a box that's off, then we want to exclude it from the count. So, we just skip straight to the "next" recurisve item, which is `total_volume(rest)`:

```py
def total_volume(boxes: List[Box]) -> int:
    if not boxes:
        return 0

    root, *rest = boxes
    if not root.on:
        return total_volume(rest)

    overlaps = all_overlaps(root, rest)

    return root.volume + total_volume(rest) - total_volume(overlaps)
```

Because our `Box` defaults to `on = True` this "just works". The only time a box is dark is when it's read from the puzzle input. So, finally, we can solve our puzzle:

```py
# input parsing from above was moved into a function
# it was also tweaked slightly to return Box objects

part_1 = total_volume([box for box in self.parse_input() if box.is_small])
part_2 = total_volume(self.parse_input())
```

That'll do it! Today was tough to wrap your head around, but not to complex when we got down to it.
