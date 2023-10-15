---
year: 2022
day: 15
title: "Beacon Exclusion Zone"
slug: "2022/day/15"
pub_date: "2022-12-18"
---

## Part 1

Today seems simple enough, but taking a gander at what row the actual puzzle wants us to check (# 2 million!) means that we're going to have to be pretty judicious about space constraints. Let's give part 1 a go by iterating and see where that gets us.

Needless to say, we won't be storing a full grid today. The info we need to suss out is: "given a point, is it covered by a sensor?" It will be be covered by at-most-one, but we don't know which.

A point is covered by a beacon if the [manhattan distance](https://en.wikipedia.org/wiki/Taxicab_geometry) between the point and the sensor is less than the distance between the sensor and its beacon. To do that math, we need a little class:

```py
from dataclasses import InitVar, dataclass

GridPoint = tuple[int, int]

@dataclass
class Sensor:
    x: int
    y: int
    beacon: InitVar[GridPoint]

    def __post_init__(self, beacon):
        self.reach = self.distance_to(beacon)

    def distance_to(self, point: GridPoint) -> int:
        return abs(self.x - point[0]) + abs(self.y - point[1])

    def can_reach(self, point: GridPoint) -> bool:
        return self.distance_to(point) <= self.reach
```

We're marking `beacon` as an `InitVar`, meaning it's available for use in `__post_init__` (automatically called in the generated `__init__`), but isn't stored on the instance.

Next, we parse input. We could do a regex for the whole line, but we know there will be exactly 4 numbers in it, so we can write a regex to find all the numbers:

```py
from re import findall
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        sensors: list[Sensor] = []
        beacons: set[GridPoint] = set()

        for numbers in (
            tuple(map(int, findall(r"[\d-]+", line))) for line in self.input
        ):
            sensors.append(Sensor(numbers[0], numbers[1], numbers[2:]))
            beacons.add(numbers[2:])
```

Next, we need to figure out the range of `x` values to check. My first naive approach was to iterate the max range of x values that any sensor covered, from the [x_min](https://www.youtube.com/watch?v=sAkL2-vh2Sk) to the `x_max`:

```py
...

x_min = min(s.x - s.reach for s in sensors)
x_max = max(s.x + s.reach for s in sensors)
```

Then I could could count how many items in that row were covered (and weren't themselves beacons):

```py
...

target_row = 10 if self.use_test_data else 2000000

return sum(
    any(s.can_reach((x, target_row)) for s in sensors)
    for x in range(x_min, x_max + 1)
    if (x, target_row) not in beacons # remove duplicates
)
```

This _worked_, but ran in 14 seconds on my puzzle input. That's not going to fly for a part 2 which will almost certainly put those huge numbers front and center.

### Part 1 Improved

Rather than iterate at all, if we can build the possible range of `x` values (which we _were_ going to iterate over), we can just sum up the length of that range? We'll have to sort the ranges, but it reduces our work to a series of basic arithmetic.

To do this, we'll need to turn a `Sensor` into the range of values it covers on a given row. If it can reach the target row at all, it will cover `its reach - its vertical distance to that row` in each direction. For example, the `8,7` sensor from the example input has a reach of 10. So, it could cover 7 tiles in each direction: `10 - abs(7-10) == 7` (from 2 to 14, inclusive). Here's that visualized, with `V` being the path to the target row and `R` the range it covers on that row:

```
 7 .#########S#######S#........
 8 ..########V########.........
 9 ...#######V#######..........
10 ....RRRRRRRRRRRRR...........
```

There are `13` Rs there, which is 7 in each direction (minus 1 for the column that's counted twice). If we do that for every sensor and find the full distance those ranges cover, then we should have our answer!

First thing is to write the range finder function:

```py
class Sensor:
    ...

    def range_on_row(self, target_row: int) -> range | None:
        if not self.can_reach((self.x, target_row)):
            return None

        num_on_row = self.reach - abs(self.y - target_row)

        return range(self.x - num_on_row, self.x + num_on_row)
```

That's the same math we had above. Next, we build and sort our ranges; the sorting is important to make sure our overlaps are counted correctly:

```py
from operator import itemgetter

...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        ranges = list(
            sorted(
                (r for s in sensors if (r := s.range_on_row(target_row))),
                key=itemgetter(0),
            )
        )
```

Here's another use of the walrus (`:=`) operator, but it's on the on the conditional side of the comprehension.[^1] Now we have a series of ranges of the sensors that can see our target row. For the example input, that gives:

```py
[range(-2, 2), range(2, 14), range(14, 18), range(16, 24)]
```

Finally, we create one large range that encompasses the whole thing. We know there are no breaks, so all we need is the distance between the end of the last one and the start of the first:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        return ranges[-1].stop - ranges[0].start
```

That solution runs instantaneously. Pretty good improvement, if I do say so myself!

## Part 2

It's a good thing we took the time to improve our solution. I'm no mathematician, but trying to iterate over iterating 4,000,000<sup>2</sup> points is a _lot_ of distance to cover.

But, I think a small tweak to our (revised) part 1 code will get us there. Before, we assumed that the ranges overlapped. But, for one row, they won't! In exactly 1 pair of ranges on exactly 1 line, there's exactly 1 spot that's tile wide. We have to find that spot.

Before we do that, we have to be able to limit our ranges to the search boundary (`20` in the example, 4 million in the puzzle). We can modify `range_on_row` to do it:

```py
class Sensor:
    ...

    def range_on_row(self, target_row: int, clamp_at: int) -> range | None:
        if not self.can_reach((self.x, target_row)):
            return None

        num_on_row = self.reach - abs(self.y - target_row)

        res = range(self.x - num_on_row, self.x + num_on_row)

        if clamp_at:
            return range(max(res.start, 0), min(res.stop, TUNING_MULTIPLIER))
        return res

...

class Solution(StrSplitSolution):
    ...

    def get_ranges(
        self, sensors: list[Sensor], target_row: int, clamp_at: int = 0
    ) -> list[range]:
        ranges = list(
            sorted(
                (r for s in sensors if (r := s.range_on_row(target_row, clamp_at))),
                key=itemgetter(0),
            )
        )
        return ranges
```

Next, our loop. Unfortunately, we still have to loop over (in the worst case) 4 million rows, but at least each row will be fast!

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        sensors = self.parse_sensors()
        range_to_check = 20 if self.use_test_data else TUNING_MULTIPLIER

        for row in range(range_to_check):
            ranges = self.get_ranges(sensors, row, clamp_at=range_to_check)

            covered_range = ranges[0]
            for r in ranges[1:]:
                if not covered_range.start <= r.start <= covered_range.stop:
                    return (covered_range.stop + 1) * TUNING_MULTIPLIER + row

                covered_range = range(
                    min(covered_range.start, r.start), max(covered_range.stop, r.stop)
                )
        raise ValueError("Failed to find!")
```

For each row, we get the ranges, then join them if they overlap. If they don't, we've found a hole and we return that value. The good news is that this _does_ work. The bad news is that it runs for 39 seconds on my M1 Macbook Pro. 😬 We can leave if there if you want (after all, a star is a star!), but there's one other approach we can take.

### Part 2 Improved

We know that our hole will be bordered on all sides by the borders of scanners. If any of those scanners had a range 1 larger than it does, then that scanner would be the only one to include the point. So, if we grow each scanner one at a time and iterate over its (now enlarged) border, we can report the one point that no other scanner can reach. To do this, all we need is a method to walk the border of a scanner's reach + 1 circle:

```py
class Sensor:
    ...

    def enlarged_border_points(self, clamp_at: int) -> Iterable[GridPoint]:
        def in_range(x_, y_) -> bool:
            return 0 <= x_ <= clamp_at and 0 <= y_ <= clamp_at

        # start at the top of the diamond
        x = self.x
        y = self.y - self.reach - 1

        # go down and right
        change_x = 1
        change_y = 1
        while y < self.y:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go down and left
        change_x = -1
        while x > self.x:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go up and left
        change_y = -1
        while y > self.y:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y

        # go down and left
        change_x = 1
        while x < self.x:
            if in_range(x, y):
                yield x, y
            x += change_x
            y += change_y
```

Then, we walk that path and see if any sensors can see that point:

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        sensors = self.parse_sensors()
        range_to_check = 20 if self.use_test_data else TUNING_MULTIPLIER

        for sensor in sensors:
            for point in sensor.enlarged_border_points(range_to_check):
                if any(s.can_reach(point) for s in sensors):
                    continue
                return point[0] * TUNING_MULTIPLIER + point[1]

        raise ValueError("Failed to find!")
```

Running that, we get our answer in... 18 seconds. Definitely an improvement, but still quite slow as far as AoC solutions go. But at this point, I've spent enough time on this one.

If you're curious about other (faster) approaches, check out the [Reddit solution thread](https://old.reddit.com/r/adventofcode/comments/zmcn64/2022_day_15_solutions/). Highlights include:

- finding the intersections of the lines that border each diamond ([permalink](https://old.reddit.com/r/adventofcode/comments/zmcn64/2022_day_15_solutions/j0b90nr/))
- plugging the constraints into Z3, Microsoft Research's equation solver and letting it do the work ([permalink](https://old.reddit.com/r/adventofcode/comments/zmcn64/2022_day_15_solutions/j0af5cy/))

Good job sticking with this one!

[^1]: TBH I wasn't sure this sort of thing would work at all, but am pleased to report it does!
