---
year: 2021
day: 11
title: "Dumbo Octopus"
slug: "2021/day/11"
pub_date: "2021-12-11"
---

## Part 1

Another grid! But, one where we'l be iterating over values a lot. Rather than have to do a nested `for` loop repeatedly, we can store our grid differently to make further iterations. Namely, we'll use a `dict`. The key is a `(row, col)` `tuple` (renamed as `Location` using a type alias) and the values are a little `Point` class that will store the numeric value and whether or not it's flashed this round.

Grid ingestion is straightforward:

```py
from dataclasses import dataclass
from typing import Dict, List, Tuple

Location = Tuple[int, int]


@dataclass
class Point:
    val: int
    flashed: bool = False

    def reset(self):
        if self.val > 9:
            self.val = 0
            self.flashed = False

grid: Dict[Location, Point] = {}
    for row in range(10):
        for col in range(10):
            grid[(row, col)] = Point(int(self.input[row][col]))
```

Next is a way to get neighbor tuples based on a location. I vaguely remember last year a function to do this really cleanly, but couldn't remember it offhand. So, you get a bit of verbose code:

```py
def neighbors(loc: Location) -> List[Location]:
    res = []
    row, col = loc
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue  # skip self
            if not 0 <= row + i <= 9:
                continue

            if not 0 <= col + j <= 9:
                continue

            res.append((row + i, col + j))

    return res
```

No we're ready to perform each step. You could do this recursively, but I like approach these iteratively; it makes a little more sense in my head and we don't have to worry about stack sizes.

The core of the approach is a list of locations. For each location, we're going to increment its value. Then if it's `>= 9`, we'll add all its neighbors to that list. But, we can't change the size of a list while we're iterating through it, so we'll use an "on deck" list that replaces the one we're iterating once we're done. It's important that we use a list instead of a `set`, since points _can_ be added multiple times. Let's write a loop!

```py
total = 0

for step in range(100):
    to_power: Iterable[Location] = grid.keys()

    # on first pass, this is a full list; it probably shrinks over time
    while to_power:
        # this is the on-deck list that replaces the one we iterate over
        triggered: List[Location] = []
        for loc in to_power:
            p = grid[loc]

            p.val += 1
            # the and not p.flashed is important; without it, we'd never exit
            if p.val > 9 and not p.flashed:
                p.flashed = True
                total += 1
                triggered += neighbors(loc)

        to_power = triggered

    # once the `while` exits, we'll have looped over spot and resolved every chain reaction
    # so, we reset the grid
    for p in grid.values():
        p.reset()

# once that's all done, we've done our 100 loops and can return the number of flashes
return total
```

This is pretty efficient because we can loop through `grid.values()` and modify it as we go. This works because `.values()` provides an iterator that still references the data in the original grid, not a copy of it. So, any modifications we do to our pointer are "saved" even once we're outside the loop. Knowing exactly what will happen when with regards to existing data in memory can be the source of some tough bugs, so it's worth really taking the time to understand.

In any case, we have our answer. Quickly, too!

## Part 2

We got lucky here - because of how our code for part 1 was set up, this may set the record for least amount of code changed to solve a part 2.

There's 2 main changes:

1. we have to go more loops, but save our part 1 answer at the right place
2. we have to have a way to validate if the whole grid flashed. Because we can already iterate over all our values quickly, this is pretty easy

Let's rename our running variable, modify our loop, and add that check:

```py
...

num_flashes_100_steps = 0
# if 500 isn't enough, we can raise it
for step in range(1, 500):
    ...

    while to_power:
        ...

        if p.val > 9 and not p.flashed:
            p.flashed = True
            # added this check so we stop at some point
            if step <= 100:
                num_flashes_100_steps += 1
            ...

    if all(p.flashed for p in grid.values()):
        return num_flashes_100_steps, step

    # reset grid
    ...

# just in case our limit is too low, it'll be obvious
return num_flashes_100_steps, -1
```

That's all! We stop tallying flashes after 100 steps, and we do a check before we reset the grid to see if everything flashed. That `all` is fast because it "short circuits", or stops as soon as any value is "falsy". It doesn't have to check the rest of the list as soon as it finds a single un-flashed octopus, so we save some loops there too.
