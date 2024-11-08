---
year: 2023
day: 24
slug: 2023/day/24
title: "Never Tell Me The Odds"
# concepts: []
# pub_date: "TBD"
---

## Part 1

Today felt like a throwback to high school algebra, which I'm pretty rusty on. Luckily, part 1 is pretty straightforward and it came back to me quickly!

Given a pair of lines, we have to determine if/where those lines intersect. That's [a multi-step process](https://www.wikihow.com/Algebraically-Find-the-Intersection-of-Two-Lines#Finding-the-Intersection-of-Two-Straight-Lines) that requires two lines in the form of `y = mx + b`, where:

- `m` is the slope of the line (given as "rise over run", or the fraction `vx / vy`).
- `b` is the height at which the line crosses the y-axis.

We have some of this info in the input, but we'll have to do some parsing:

```py
from dataclasses import dataclass
from functools import cached_property


def parse_3d_point(point: str) -> list[int]:
    return list(map(int, point.split(", ")))


@dataclass
class Hailstone:
    px: int
    py: int
    pz: int

    vx: int
    vy: int
    vz: int

    @staticmethod
    def parse(line: str) -> "Hailstone":
        position, velocity = line.split(" @ ")
        values = [*parse_3d_point(position), *parse_3d_point(velocity)]
        return Hailstone(*values)

    @cached_property
    def slope(self) -> float:
        return self.vy / self.vx
```

There's a helper for parsing ints out of `"a, b, c"` strings, but otherwise we're just storing all this data. We also have our simple slope calculation for use later.

Next, we need to solve for `b`. Since we have the other 3 variables, it's easy to move the data around: `y = mx + b` -> `y - mx = b`. The matching code is equally straightforward:

```py
...

@dataclass
class Hailstone:
    ...

    @cached_property
    def y_intercept(self):
        """
        the height at which this line hits the y axis
        """
        return self.py - self.slope * self.px
```

So given a point (`(px, py)`) and a velocity (`(vx, vy)`), we have all the code needed to calculate every part of `y = mx + b`.

Before continuing, let's We'll parse our stones and examine each pair of them to figure out which ones will intersect.

```py
from itertools import combinations

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]

        total = 0
        for l, r in combinations(hailstones, 2):
            # TBD
            ...

        return total
```

That `TBD` is doing a lot of work, but you can see the shape of the thing. Next we'll solve for our `x` and `y` intersection points, starting with `x`. If you have to `y = mx + b` lines represented as `L` and `R`:

> y == m<sub>L</sub> \* x + b<sub>L</sub>
>
> y == m<sub>R</sub> \* x + b<sub>R</sub>

then you can set them equal to each other:

> m<sub>L</sub> \* x + b<sub>L</sub> == m<sub>R</sub> \* x + b<sub>R</sub>

subtract bits of both sides: to isolate our variables:

> m<sub>L</sub> \* x - m<sub>R</sub> \* x == b<sub>R</sub> - b<sub>L</sub>

before dividing out the slopes to give our final equation:

> x == (b<sub>R</sub> - b<sub>L</sub>) / (m<sub>L</sub> - m<sub>R</sub>)

Which is easy to translate into Python code:

```py ins={8}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for l, r in combinations(hailstones, 2):
            x_intersection = (r.y_intercept - l.y_intercept) / (l.slope - r.slope)
```

That's the `x` coordinate where the lines intersect! Now we can plug that back into either of our lines (again, shown as `y = mx + b`) to find the corresponding y value. This is also simple Python:

```py ins={9}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for l, r in combinations(hailstones, 2):
            x_intersection = (r.y_intercept - l.y_intercept) / (l.slope - r.slope)
            y_intersection = l.slope * x_intersection + l.y_intercept
```

A little bit of math went a long way here! But before we can wrap we have a few conditions to worry about.

First, it's possible that the lines are parallel. This means their slopes are the same and the lines will _never_ intersect. If we don't account for this before we calculate `x_intersection`, we'll end up dividing by `0` on that line. We also only want to count intersection points within the bounds of the problem (between `7` and `27` in the example).

Let's add those checks:

```py ins={8-13,16-18,23-27}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        # this variable is from my AoC template; you can also hardcode
        if self.use_test_data:
            BOUNDS_MIN = 7
            BOUNDS_MAX = 27
        else:
            BOUNDS_MIN = 200_000_000_000_000
            BOUNDS_MAX = 400_000_000_000_000

        for l, r in combinations(hailstones, 2):
            # parallel lines never intersect
            if l.slope == r.slope:
                continue

            x_intersection = (r.y_intercept - l.y_intercept) / (l.slope - r.slope)
            y_intersection = l.slope * x_intersection + l.y_intercept

            if (
                BOUNDS_MIN <= x_intersection <= BOUNDS_MAX
                and BOUNDS_MIN <= y_intersection <= BOUNDS_MAX
            ):
                total += 1

        return total
```

We're close, but there's one last thing to consider. Though we've correctly identified the intersection of the 2 lines, our hailstones start at a point and move in a direction. So there's a bunch of points on both lines that are in the "past" based on their current position and direction. Before we can increment our `total`, we have to check for that.

We know which direction (left or right) our hailstone will fly based on the sign of its `vx`: positive values move right, negative to the left. So if we're moving right and `x_intersection` is to our left (i.e. lower) than our `px`, we know the intersection point is in the past and shouldn't be counted. That gives us our last bits of code:

```py ins={7-11,20-21}
...

@dataclass
class Hailstone:
    ...

    def is_point_in_past(self, x) -> bool:
        if self.vx > 0:
            return self.px > x

        return self.px < x

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for l, r in combinations(hailstones, 2):
            ...

            if l.is_point_in_past(x_intersection) or r.is_point_in_past(x_intersection):
                continue

            ...

        return total
```

And that should do it! Despite the huge ranges, we're just doing a bunch of simple integer math for this part, so everything is quick and snappy. Those `z` values make me nervous about part 2 though...

## Part 2
