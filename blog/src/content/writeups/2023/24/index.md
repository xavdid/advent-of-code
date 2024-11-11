---
year: 2023
day: 24
slug: 2023/day/24
title: "Never Tell Me The Odds"
# concepts: []
pub_date: "2024-11-10"
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

While I got back into my groove for part 1, I didn't have near the same confidence level for part 2. After spinning my wheels for a bit and not knowing where to start, I headed to the trusty [solution thread](https://old.reddit.com/r/adventofcode/comments/18pnycy/2023_day_24_solutions/). There were a lot of approaches that involved plugging data into [Z3](https://github.com/Z3Prover/z3), an equation solver or [Mathematica](https://www.wolfram.com/mathematica/index.php.en), a similar offering from Wolfram. That certainly works, but I found it boring. Let's solve it for real!

After a lot of reading (and a few other hint threads), I finally made sense of [this answer](https://old.reddit.com/r/adventofcode/comments/18pnycy/2023_day_24_solutions/keqf8uq/) from `/u/TheZigerionScammer`, which I'll explain below. I've adapted their code to fit my style, but it's generically the same approach.

We ultimately need to find the rock's position across 3 dimensions, but our approach starts by finding the velocities.

The key insight is that **for every pair of hailstones that share a velocity, the rock must be thrown at a speed that _could_ intersect both rocks**. Both rocks are moving at a constant velocity, but they're separated by some distance. This means the `vx` of our rock will need to account for the velocity of both hailstones, plus the distance between them.

For example, imagine a pair of hailstones (`L` and `R`) with `px` of `5` and `8` respectively. They're both moving at a `vx` of `7`. We can track their `px` over time:

| `t` | `px` of `L` | `px` of `R` |
| --- | ----------- | ----------- |
| 0   | 5           | 8           |
| 1   | 12          | 15          |
| 2   | 19          | 22          |
| 3   | 26          | 29          |
| ... | ...         | ...         |

Depending on which hailstone the rock's touching at `t == 0`, there are 4 values of `vx` that will cause it to intersect the other hailstone within a few microseconds:

| `px` of rock @ `t==0` | `vx` of rock | hit other hailstone at `t ==` |
| --------------------- | ------------ | ----------------------------- |
| 5                     | 10           | 1                             |
| 8                     | 4            | 1                             |
| 5                     | 6            | 3                             |
| 8                     | 8            | 3                             |

Subtracting the constant velocity that the hailstones are traveling (`7`) from each of the possible `vx` values gives us `[3, -3, -1, 1]` which are all of the factors of the distance between the two hailstones!

More broadly, we're looking for values of `v` such that `distance % (v - vx) == 0`! If we find every possible `v` for every pair of hailstones, then the values that show up in _every_ combination must be the velocity the rock is traveling! The same goes for the other two dimensions as well. This code is fairly straightforward:

> Note: this doesn't work for the test input, but works great for the real one, which I'll allow!

```py
...

def possible_velocities(hailstone_velocity: int, distance: int) -> set[int]:
    return {
        v
        for v in range(-1000, 1000)
        # find values in a (large) range that satisfy our equation
        # have to cap it because there's an infinite number of answers,
        # so just make it "big enough"
        # also, make sure we don't divide by 0!
        if v != hailstone_velocity and distance % (v - hailstone_velocity) == 0
    }

@dataclass
class Hailstone:
    ...

    # add some helpers to dynamically get values from Hailstones
    def velocity(self, dim: str) -> int:
        return getattr(self, f"v{dim}")

    def position(self, dim: str) -> int:
        return getattr(self, f"p{dim}")

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        hailstones = [Hailstone.parse(line) for line in self.input]

        rock_velocities = []
        # for each dimension...
        for dim in "xyz":
            all_possibilities = [
                # call our function with the velocity and the distance between the hailstones
                possible_velocities(l.velocity(dim), r.position(dim) - l.position(dim))
                # for every hailstone pair...
                for l, r in combinations(hailstones, 2)
                # that share a velocity
                if l.velocity(dim) == r.velocity(dim)
            ]

            # find the velocity that shows up in every pair's set
            common_possibilities = all_possibilities[0].intersection(*all_possibilities)
            # ensure there's just the 1 possible velocity
            assert len(common_possibilities) == 1

            # and save it to our results list
            rock_velocities.append(common_possibilities.pop())
```

There are some dense list comprehensions there, but it's mostly just set up for the equation we figured out before. Some new property helpers and a function mean that we can get the rock's velocity for all 3 of our dimensions with minimal fuss.

Next, we have to solve for our rock's starting position. We have no idea where it'll be, but we know which line it'll intersect- all of them! We also know how fast the rock moves.

If we subtract the rock's velocity from any hailstone, we'll get a new line showing all the potential start points for that rock to ensure it can still intersect our chosen hailstone. If we do that twice, we'll get two lines of possible start points. _Their intersection_ is the only place the rock could start to hit both hailstones, and by extension, all the others.

At this point, we can reuse bits of part 1, which we'll move into a function:

```py ins={5-19,32,40,42-43,45} del={28-31}
@dataclass
class Hailstone:
    ...

    def slower_hailstone(self, rvx: int, rvy: int) -> "Hailstone":
        """
        given the 2D velocity of a rock, slow this hailstone down to create a reference frame
        """
        return Hailstone(
            self.px, self.py, self.pz, self.vx - rvx, self.vy - rvy, self.vz
        )

    def intersection_with(self, other: "Hailstone") -> tuple[float, float]:
        x_intersection = (other.y_intercept - self.y_intercept) / (
            self.slope - other.slope
        )
        y_intersection = self.slope * x_intersection + self.y_intercept

        return x_intersection, y_intersection

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for l, r in combinations(hailstones, 2):
            ...

            x_intersection = (r.y_intercept - l.y_intercept) / (
                l.slope - r.slope
            )
            y_intersection = l.slope * x_intersection + l.y_intercept
            x_intersection, y_intersection = l.intersection_with(r)
            ...

    def part_2(self) -> int:
        ...

        rvx, rvy, rvz = rock_velocities

        a, b, *_ = hailstones

        a = a.slower_hailstone(rvx, rvy)
        b = b.slower_hailstone(rvx, rvy)

        rpx, rpy = a.intersection_with(b)
```

That gives 2/3 of our answer, but we still need to solve for `rpz`. It's basically the same equation as part 1 with some variables moved around. We know that the rock intersects a hailstone in the `x` dimension at a certain time. So, the initial `rpx` + `rvx` after some amount of time will equal the same from the hailstone (`a`):

> rpx + rvx \* t == apx + avx \* t

Solving for `t`, we get:

> t == (rpx - apx) / (avx - rvx)

or the `t` value for when both objects are aligned in the `x` dimension.

Lastly, we work backwards in time. Because we know all their velocities and when they intersect, we can see how far the rock must have traveled from its initial `pz` to reach the hailstone at thie intersection time, `t`. It must have gone the difference in their velocities `t` times, or `(avz - rvz) * time`. Add that to `apz` and you know the rock's initial z position:

> rpz == apz + (avz - rvz) \* time

All that remains is to write the last bit of code to to the calculation and return the sum:

```py ins={9, 16-17,19}
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        a, b, *_ = hailstones
        # store un-slowed because we need it later
        avx = a.vx

        a = a.slower_hailstone(rvx, rvy)
        b = b.slower_hailstone(rvx, rvy)

        rpx, rpy = a.intersection_with(b)

        time = (rpx - a.px) / (avx - rvx)
        rpz = a.pz + (a.vz - rvz) * time

        return int(rpx + rpy + rpz)
```

No step was too complicated, but boy were there a lot of them! In any case, we're on the home stretch now.
