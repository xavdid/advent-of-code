---
year: 2020
day: 12
title: "Rain Risk"
slug: "2020/day/12"
pub_date: "2020-12-12"
---

## Part 1

Another straightforward one! No tricks, no fancy algorithms, just following instructions. After [day 11's odd grid](/writeups/2020/day/11/), I was personally happy to back to a more standard X/Y plane. In any case, let's start with a `class` and some constants:

```py
COMPASS = ["N", "E", "S", "W"]


class Ship:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        # index in the compass
        self.facing = 0
```

Our ship has two main actions, moving and rotating. Moving is more verbose, but simple.

Our grid is much like high school algebra: `(0,0)` is in the middle of an infinite plane. `X` increases in value to the right; `Y` increases when going up. The only interesting bit is that `F` is equal to a move in whatever direction we're already facing:

```py
def move(self, direction: str, distance: int):
    if direction == "F":
        direction = self.facing

    if direction == "N":
        self.y += distance
    elif direction == "S":
        self.y -= distance
    elif direction == "E":
        self.x += distance
    elif direction == "W":
        self.x -= distance
```

Rotating is slightly more interesting. The goal is to have a clean way to move through the `COMPASS` declared above. As a rule of thumb, whenever you have to loop through a finite `list`, the general pattern is `new_index = (index + num_steps) % len(my_list)`. The `%` operator ensures our `new_index` never exceeds the length of the `list`, which is convenient. The `rotate` method translates the `L` and `R` commands into a number of steps (maybe negative) and calculates the new direction:

```py
def rotate(self, direction: str, degrees: int):
    num_steps = degrees // 90
    if direction == "L":
        num_steps *= -1

    self.facing = (self.facing + num_steps) % len(COMPASS)
```

Now all we need is to parse the input and string those functions together:

```py
DIRECTIONS = set([*COMPASS, "F"])

def execute(self, instructions: List[str]):
    for instruction in instructions:
        move_type = instruction[0]
        value = int(instruction[1:])
        if move_type in DIRECTIONS:
            self.move(move_type, value)
        else:
            self.rotate(move_type, value)
```

Calculating the distance from 0 is easy with Python's `abs` (absolute value) function:

```py
def distance(self) -> int:
    return abs(self.x) + abs(self.y)
```

Finally, our actual solution:

```py
ship = Ship()
ship.execute(self.input)
return ship.distance()
```

## Part 2

Much like in previous days, day 2 requires us to modify our part 1 code and add some logic branches.

First, we add a few new variables to our class to hold which mode we're in (`waypoint` or not):

```py
def __init__(self, waypoint=False) -> None:
        ...
        self.waypoint = waypoint
        self.waypoint_x = 10
        self.waypoint_y = 1
```

Our `move` method has to now _mostly_ move the waypoint coordinates instead of the ship. The notable change is that an `F` move in `waypoint` mode moves the `distance` times the `offset`. Otherwise, everything is familiar:

```py
def move(self, direction: str, distance: int):
if self.waypoint:
    if direction == "F":
        self.x += distance * self.waypoint_x
        self.y += distance * self.waypoint_y
    elif direction == "N":
        self.waypoint_y += distance
    elif direction == "S":
        self.waypoint_y -= distance
    elif direction == "E":
        self.waypoint_x += distance
    elif direction == "W":
        self.waypoint_x -= distance
else:
    # part 1 code
    ...
```

The part that too me the longest to wrap my head around was rotating the waypoint. I had to read the prompt about 8 times:

> The waypoint [is at] 10 units east and 4 units north of the ship.
> R90 ... [moves] it to 4 units east and 10 units south of the ship.

In numbers, our waypoint goes from `(10, 4)` to `(4, -10)`. If we had rotated `L` instead, we would have gone from `(10, 4)` to `(-4, 10)`. So each time we rotate, there are two steps:

1. Swap values
2. Swap positivity for either `X` or `Y`. Based on the examples above, `L` rotation means we swap the (now) `x` value. `R` is the opposite.

We have to do both of the above for each of the rotation steps. These rules lead to straightforward code:

```py
def rotate(self, direction: str, degrees: int):
    num_steps = degrees // 90
    if self.waypoint:
        for _ in range(num_steps):
            temp = self.waypoint_y
            self.waypoint_y = self.waypoint_x
            self.waypoint_x = temp
            # when turning L, the new X swaps sign
            # opposite is true for R
            if direction == "L":
                self.waypoint_x *= -1
            else:
                self.waypoint_y *= -1

    else:
        # part 1 code
        ...
```

The solution code is nearly identical:

```py
ship = Ship(waypoint=True)
ship.execute(self.input)
return ship.distance()
```
