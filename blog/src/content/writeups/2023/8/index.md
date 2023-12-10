---
year: 2023
day: 8
title: "Haunted Wasteland"
slug: 2023/day/8
pub_date: "2023-12-09"
---

## Part 1

Another one of those suspiciously simple days (to start).

We split our input into 2 blocks (above and below the `\n\n` break). For the top part, we send that string into a `itertools.cycle`, which will iterate through the string repeatedly forever. For the nodes, we can use a regex to find each 3-letter string in the line and assign it to a dict accordingly. Here's how that all looks:

```py
import re

class Solution(TextSolution):
    def part_1(self) -> int:
        raw_directions, raw_nodes = self.input.split("\n\n")

        instructions = cycle(raw_directions)

        nodes: dict[str, dict[str, str]] = {}
        for line in raw_nodes.split("\n"):
            root, l, r = re.findall(r"[A-Z]{3}", line)
            nodes[root] = {"L": l, "R": r}
```

For the actual solution, we need to track 2 pieces of information: our current node and the number of steps we've taken. The latter calls for `enumerate` and the former is a string.

On each step, we exit if we're on `ZZZ`. Otherwise, we take a step according to the next instruction:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...

        current = "AAA"
        for idx, ins in enumerate(instructions):
            if current == "ZZZ":
                return idx
            current = nodes[current][ins]
```

If we were worried about this _never_ completing then I'd add a check for `if idx > some_big_number: break` and save myself from the infinite loop. But, no worries here!

## Part 2

Ok, so we _might_ be able to just run a modified version of our part 1 code, but it's also possible that that'll go way too long. Let's give it a try. Moving our parsing code (unchanged) into a function, we get:

```py ins={7, 9, 11, 14}
...

class Solution(TextSolution):
    ...

    def part_2(self) -> int:
        instructions, nodes = self._parse_input()

        current = [k for k in nodes.keys() if k[-1] == "A"]
        for idx, ins in enumerate(instructions):
            if all(l[-1] == "Z" for l in current):
                return idx

            current = [nodes[l][ins] for l in current]
```

But, that runs way too long (if it even ever completes). So, we need a different approach.

I did some manual investigation of my input data, which is a great way to start understanding the problem space. For my input, there were exactly 6 starting locations and 6 ending locations. Next, I tweaked my solver to navigate from an arbitrary starting place to anything ending in `Z` (which should look familiar):

```py ins="_from_start_to_z" ins=", start: str" ins={5-6,9,12-13}
...

class Solution(TextSolution):
    def _from_start_to_z(self, current: str) -> int:
        print(f"\nchecking {start}")
        instructions, nodes = self._parse_input()
        for idx, ins in enumerate(instructions):
            if current[-1] == "Z":
                print(f"  found ending {current} at t={idx}")
            current = nodes[current][ins]

            if idx > 100_000:
                return -1
```

I wrote this wanting to learn a few things:

1. How many exits does each starting location find?
2. do they loop?

The output was illuminating:

```
checking MTA
  found ending BJZ at t=16897
  found ending BJZ at t=33794
  found ending BJZ at t=50691

checking QNA
  found ending NPZ at t=16343
  found ending NPZ at t=32686
  found ending NPZ at t=49029

checking XCA
  found ending PBZ at t=21883
  found ending PBZ at t=43766
  found ending PBZ at t=65649
  found ending PBZ at t=87532

checking BXA
  found ending PMZ at t=13019
  found ending PMZ at t=26038
  found ending PMZ at t=39057
  found ending PMZ at t=52076
  found ending PMZ at t=65095
  found ending PMZ at t=78114
  found ending PMZ at t=91133

checking AAA
  found ending ZZZ at t=14681
  found ending ZZZ at t=29362
  found ending ZZZ at t=44043
  found ending ZZZ at t=58724
  found ending ZZZ at t=73405
  found ending ZZZ at t=88086

checking VCA
  found ending BLZ at t=20221
  found ending BLZ at t=40442
  found ending BLZ at t=60663
  found ending BLZ at t=80884
```

Not only does each entrance have a 1:1 relationship with an exit, they all loop as soon as they find their exit. We can tell because the timestamps for each exit are multiples of the first exit time (e.g. if a path exits at `t=5`, we'll also see exits at `t=10`, `t=15`, etc).

So, this gives us a ton more info about how to solve the problem. We know we only need to find the first exit (same as part 1) and we need to know when all of these cycles sync up. Sounds like a job for `math.lcm` ([docs](https://docs.python.org/3/library/math.html#math.lcm)).

We're most of the way there already, but we can now clean our code up:

```py ins=" _solve" ins={14,16-20}
...

class Solution(TextSolution):
    ...

    def _solve(self, current: str) -> int:
        instructions, nodes = self._parse_input()
        for idx, ins in enumerate(instructions):
            if current[-1] == "Z":
                return idx
            current = nodes[current][ins]

    def part_1(self) -> int:
        return self._solve("AAA")

    def part_2(self) -> int:
        _, nodes = self._parse_input()
        starts = [k for k in nodes.keys() if k[-1] == "A"]

        return math.lcm(*[self._solve(s) for s in starts])
```

My answer of more than 1 trillion makes me _real_ glad I didn't try running my laptop until I eventually found the answer.
