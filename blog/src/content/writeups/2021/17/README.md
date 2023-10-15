---
year: 2021
day: 17
title: "Trick Shot"
slug: "2021/day/17"
pub_date: "2021-12-22"
---

## Part 1

This is the sort of AoC puzzle I don't enjoy- one that's just about modeling a physics concept I've forgotten since high school. I didn't have the steam for this today, so I looked through [this great walkthrough](https://github.com/mebeim/aoc/blob/master/2021/README.md#day-17---trick-shot) for the solution(s).

For part 1, there's a mathy formula that just gives you the answer: `y1 * (y1 + 1) // 2`. Of course, to use, that you'll have to parse the input. We can do that with a simple regex:

```py
from re import findall
from typing import Tuple

Range = Tuple[int, int]

ranges = [
    cast(Range, tuple(map(int, x)))
    for x in findall(r"(-?\d+)\.\.(-?\d+)", self.input)
]
# => [(20, 30), (-10, -5)]
```

That handles finding our points and converting them to `int`s.

Now we can plug that into the formula for our answer:

```py
y1 = ranges[1][0]
return y1 * (y1 + 1) // 2
```

And again- you should really read [the explanation](https://github.com/mebeim/aoc/blob/master/2021/README.md#day-17---trick-shot) for why this works. Unfortunately, there's not much in the way for interesting code here, but the Newtonian physics is worth a little refresher.

## Part 2

For part 2, I got to repurpose a class I had _originally_ written when I thought part 1 was worth solving "by hand". It's nothing wild- I organized the step math into little functions and a check to see if our current position is in past the target. There's also a `fly`, which runs the steps and knows when we haven't missed the target (yet):

```py
from dataclasses import dataclass

@dataclass
class Probe:
    vel_x: int
    vel_y: int
    targ_x: Range
    targ_y: Range

    pos_x = 0
    pos_y = 0

    def step(self) -> None:
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        if self.vel_x < 0:
            self.vel_x += 1
        if self.vel_x > 0:
            self.vel_x -= 1

        self.vel_y -= 1

    def is_in_target(self) -> bool:
        return (self.targ_x[0] <= self.pos_x <= self.targ_x[1]) and (
            self.targ_y[0] <= self.pos_y <= self.targ_y[1]
        )

    def fly(self) -> bool:
        """
        returns true if probe hit the target, false otherwise
        """

        # haven't missed yet!
        while self.pos_x <= self.targ_x[1] and self.pos_y >= self.targ_y[0]:
            self.step()
            if self.is_in_target():
                return True

        return False
```

Now, back in our main loop, we pick a range for initial `x` and `y` velocities and count the ones that hit. The bounds are sourced from more math, so [give it a read](https://github.com/mebeim/aoc/blob/master/2021/README.md#part-2-16):

```py
# parse input
...

total = 0
for x in range(int((ranges[0][0] * 2) ** 0.5), ranges[0][1] + 1):
    for y in range(y1, -y1):
        p = Probe(x, y, *ranges)
        if p.fly():
            total += 1
return total
```

Not so bad, once someone else does the math for us 😅
