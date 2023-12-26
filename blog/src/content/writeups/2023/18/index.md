---
year: 2023
day: 18
slug: 2023/day/18
title: "Lavaduct Lagoon"
pub_date: "2023-12-25"
---

## Part 1

This smells an awful lot like [Day 10](/writeups/2023/day/10/), which introduced us to:

- [Pick's Theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem), for finding the number of points in a shape given its area and border points
- the [Shoelace formula](https://en.wikipedia.org/wiki/Shoelace_formula), for finding the area of a shape given its border points

I could reuse all the math code from that day:

```py
from itertools import pairwise

GridPoint = tuple[int, int]

def num_points(outline: list[GridPoint]) -> int:
    """
    the number of the points inside an outline plus the number of points in the outline
    """
    # shoelace - find the float area in a shape
    area = (
        sum(
            row1 * col2 - row2 * col1
            for (row1, col1), (row2, col2) in pairwise(outline)
        )
        / 2
    )
    # pick's theorem - find the number of points in a shape given its area
    return int(abs(area) - 0.5 * len(outline) + 1) + len(outline)
```

The only changes are:

1. I put my math into a single function
2. I renamed some variables
3. I switched `zip(l, l[1:])` to `itertools.pairwise`, which does the same thing (TIL!)

With that, we can do part 1 literally:

```py
...

OFFSETS: dict[str, GridPoint] = {
    "R": (0, 1),
    "D": (1, 0),
    "L": (0, -1),
    "U": (-1, 0),
}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        points: list[GridPoint] = [(0, 0)]

        for line in self.input:
            direction, distance_str, _ = line.split()

            for _ in range(int(distance_str)):
                points.append(add_points(OFFSETS[direction], points[-1]))

        return num_points(points)
```

> again, using `add_points` from [my graph utils](https://github.com/xavdid/advent-of-code/blob/2ca77eeb7801aa8b3ea5885b367d4f12f0db0957/solutions/utils/graphs.py#L89-L93)

Not bad at all! Not sure what those colors are for though...

## Part 2

Ah, not colors, just huge numbers. Let's start by doing it literally again and see where that gets us. Our code adapts well, with just minor changes needed:

```py del={14,19} ins={9, 15,20-22}
...

OFFSETS = {
    "R": (0, 1),
    "D": (1, 0),
    "L": (0, -1),
    "U": (-1, 0),
}
OFFSET_INDEXES = list(OFFSETS.values())

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
    def part_2(self) -> int:
        points: list[GridPoint] = [(0, 0)]

        for line in self.input:
            direction, distance_str, _ = line.split()
            _, _, hex_str = line.split()
            distance = int(hex_str[2:-2], 16)
            offset = OFFSET_INDEXES[int(hex_str[-2])]

            for _ in range(distance):
                points.append(add_points(offset, points[-1]))

        return num_points(points)
```

Python keeping dict insertion order means careful ordering on our `OFFSETS` allows for index-based access. Then, targeting string indexing and `int('...', 16)` to convert from a hex gets us our big numbers. The big problem now is that it's slow.

Out of curiosity, I let it run for a full minute (using `timeout -v 60s ./advent`) and... it _did_ work! It just took 48 seconds of computing a _very_ long list of points (the example alone has `6405263` points in the outline). Let's speed that up.

At first I was going to try and pre-compute large number of shoelace ranges (the part that actually has to iterate over an entire range of points). Then it hit me: we're always moving in a straight line; let's only worry about the start and end of each segment. This turns `[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]` into `[(0, 0), (0, 4)]`. Spread that over segments that are hundreds of thousands of meters long and we've got some pretty significant speedups!

We'll be able to draw the same paths effectively, but we'll have to track the length of our border separately (since we can't rely on the length of the outline) anymore; we'll start there.

```py ins=", border_length: int" del="len(outline)" ins="border_length"
def num_points(outline: list[GridPoint], border_length: int) -> int:
    # shoelace - find the float area in a shape
    area = (
        sum(
            row1 * col2 - row2 * col1
            for (row1, col1), (row2, col2) in pairwise(outline)
        )
        / 2
    )
    # pick's theorem - find the number of points in a shape given its area
    return int(abs(area) - 0.5 * len(outline) + 1) + len(outline)
    return int(abs(area) - 0.5 * border_length + 1) + border_length
```

Next we adapt our part 2 code to scale its offsets:

```py del={18} ins={8,16,19} ins=", border_length"
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        outline: list[GridPoint] = [(0, 0)]
        border_length = 0

        for line in self.input:
            _, _, hex_str = line.split()

            distance = int(hex_str[2:-2], 16)

            offset = OFFSET_INDEXES[int(hex_str[-2])]
            scaled_offset = (offset[0] * distance, offset[1] * distance)

            outline.append(add_points(scaled_offset, outline[-1]))
            border_length += distance

        return num_points(outline, border_length)
```

Now our answer is instant! There are only `15` points in the example's `outline` list (down from `6,405,263`), hence the speed up.

## Extra Credit

The last order of business is combining our part 1 and part 2 code into a single implementation. We could use the part 2 approach for part one (overkill though it may be); the only difference between the parts is the way they pull an `offset` and a `distance` out of the input. So if we make that configurable, we can do it all in a single function:

```py del={5,11-13} ins={6,14}
from typing import Callable
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
    def _solve(self, get_heading: Callable[[str], tuple[GridPoint, int]]):
        outline: list[GridPoint] = [(0, 0)]
        border_length = 0

        for line in self.input:
            _, _, hex_str = line.split()
            offset = OFFSET_INDEXES[int(hex_str[-2])]
            distance = int(hex_str[2:-2], 16)
            offset, distance = get_heading(line)

            scaled_offset = (offset[0] * distance, offset[1] * distance)
            outline.append(add_points(scaled_offset, outline[-1]))
            border_length += distance

        return num_points(outline, border_length)
```

Lastly, each part defines how to extract data from input:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        def parse_line(line: str):
            direction, distance_str, _ = line.split()
            return OFFSETS[direction], int(distance_str)

        return self._solve(parse_line)

    def part_2(self) -> int:
        def parse_line(line: str):
            _, _, hex_str = line.split()
            offset = OFFSET_INDEXES[int(hex_str[-2])]
            distance = int(hex_str[2:-2], 16)
            return offset, distance

        return self._solve(parse_line)
```

Our `_solve` function could now work with basically any input format (as long as it could produce a basic offset and direction). Now that's what I call maintainable!
