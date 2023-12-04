---
year: 2023
day: 3
title: "Gear Ratios"
slug: 2023/day/3
pub_date: "2023-12-03"
---

## Part 1

While this might look like a grid-parsing puzzle, it's actually simpler than that! For each (potentially multi-digit) number in the grid, we need to look at 4 locations around that number (labeled A-D):

```
AAAAA
B123C
DDDDD
```

If any of those are a symbol (aka not a `.` or a number), then we'll add the number to the running total.

Since we're picking variable-length numbers out of the grid, we'll turn once again to regex. Instead of `re.findall`, which just found all the values, we'll use `re.finditer`, which returns `Match` objects. These also include the matched string, but they also have the start and end indexes of the match, which is important for knowing where in the grid we are. Here's how this looks:

```py
import re

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        total = 0
        symbols = re.compile(r"[^\w.]")

        for line_num, line in enumerate(self.input):
            for number in re.finditer(r"\d+", line):
                checks = [
                    # A - previous line
                    symbols.search(
                        self.input[line_num - 1][number.start() - 1 : number.end() + 1],
                    ),
                    # B
                    symbols.search(line[number.start() - 1]),
                    # C
                    symbols.search(line[number.end()]),
                    # D
                    symbols.search(
                        self.input[line_num + 1][number.start() - 1 : number.end() + 1],
                    ),
                ]

                if any(checks):
                    total += int(number.group())

        return total
```

Here, we're using the `[^\w.]` regex, which matches anything that's not alphanumeric or a dot; you can [see it in action here](https://regex101.com/r/voFmNz/1). We're doing some careful bounds checking (because `number.start()` is the index of the first digit, but `number.end()` is the index _after_ the last character), but it's pretty straightforward otherwise.

It doesn't _quite_ work though. On the first line of the example, we hit an error when we check the line above the first line, which is out of bounds. We hit similar issues against the other walls of the grid.

We _could_ carefully check our location before checking surrounding lines, but there's an easier way. What if the grid just... had an extra layer of dots on every side? It wouldn't change the answer at all, but it'll mean we never have to check any edges. Sounds like a good trade to me! Padding is pretty easy:

```py ins={4-13} ins="grid"
...

class Solution(StrSplitSolution):
    def padded_input(self) -> list[str]:
        width = len(self.input[0])
        # ensure every line is the same length; we'll mess up lines if it's not
        assert all(len(l) == width for l in self.input)

        return [
            "." * (width + 2),
            *[f".{l}." for l in self.input],
            "." * (width + 2),
        ]

    def part_1(self) -> int:
        total = 0
        symbols = re.compile(r"[^\w.]")
        grid = self.padded_input()

        for line_num, line in enumerate(grid):
            for number in re.finditer(r"\d+", line):
                checks = [
                    # A - previous line
                    symbols.search(
                        grid[line_num - 1][number.start() - 1 : number.end() + 1],
                    ),
                    # B
                    symbols.search(line[number.start() - 1]),
                    # C
                    symbols.search(line[number.end()]),
                    # D
                    symbols.search(
                        grid[line_num + 1][number.start() - 1 : number.end() + 1],
                    ),
                ]
                ...
        ...
```

And boom! Why be careful when we can guarantee we're always in bounds?

## Part 2

We're in a good spot to tackle part 2. Instead of finding _any_ symbol in the neighbors, we only care about asterisks. Also, we have to store the gear's location so we know if another number sees the same one.

Ultimately we'll need the gears surrounded by exactly 2 numbers, so we have to store _all_ the numbers associated with each gear. A `defaultdict(list)` makes it easy to blindly append to a dict key. We also have everything we need to determine the location of a gear, since we know the `line_num` and the passing index. Let's tweak the code (highlighting changes from part 1):

```py ins={1,9,15-21,24-25,28-29,32-38}
from collections import defaultdict

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        gears: dict[tuple[int, int], list[int]] = defaultdict(list)
        grid = self.padded_input()

        for line_num, line in enumerate(grid):
            for number in re.finditer(r"\d+", line):
                # A
                if "*" in (
                    l := grid[line_num - 1][number.start() - 1 : number.end() + 1]
                ):
                    assert l.count("*") == 1
                    gears[(line_num - 1, number.start() - 1 + l.index("*"))].append(
                        int(number.group())
                    )

                # B
                if line[number.start() - 1] == "*":
                    gears[(line_num, number.start() - 1)].append(int(number.group()))

                # C
                if line[number.end()] == "*":
                    gears[(line_num, number.end())].append(int(number.group()))

                # D
                if "*" in (
                    l := grid[line_num + 1][number.start() - 1 : number.end() + 1]
                ):
                    assert l.count("*") == 1
                    gears[(line_num + 1, number.start() - 1 + l.index("*"))].append(
                        int(number.group())
                    )
```

It's still the same basic idea - we're getting a string relative to the found number and doing a check on it (now, `if "*" in` that string). If there's a match, we add the location of the gear (a tuple of `(line_num, col_num)`) to the `gears` dict. The gear's location is simple for `B` and `C`, it's next to the sides of the match. For `A` and `D`, it's a little trickier. That range of characters spans `number.start() - 1 : number.end() + 1`. So to get the gear's actual column, we need its index in that string, plus the starting index in the row of the entire string. Not conceptually complicated, but tricky to get right (again, those dang bounds!)

When we're done, we have all the gears and their neighboring numbers:

```
{
    (2, 4): [467, 35],
    (5, 4): [617],
    (9, 6): [755, 598]
}
```

The last thing is the result. For each gear with exactly 2 numbers, multiply them! A comprehension makes quick work of it:

```py ins={1, 13}
from operator import mul

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        gears: dict[tuple[int, int], list[int]] = defaultdict(list)

        ...

        return sum([mul(*nums) for nums in gears.values() if len(nums) == 2])
```

And that's part 2!

It's not the prettiest code I've ever written, but it works and we've got better things to move onto!
