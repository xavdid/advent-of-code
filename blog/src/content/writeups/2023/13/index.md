---
year: 2023
day: 13
slug: 2023/day/13
title: "Point of Incidence"
pub_date: "2023-12-15"
---

## Part 1

This is another day where every block in our input is totally separate. Each gets a score that we'll sum together, so we'll design our function around scoring a single block.

The core of the puzzle is to line up rows (or columns) with their opposite across a changing line. Let's start with the rows.

If we've got a list of strings (`block`) and some index in the middle (`idx`), getting the bottom rows is easy: `block[idx:]` lists those strings in order as they depart the index. Getting the top half is marginally trickier- we need to reverse the lines _before_ index so they match their (potential) mirror. That's `reversed(block[:idx])`. If it's a perfect mirror, every pair in those two sequences will match exactly. Let's write that:

```py
def reflection_row(block: list[str]) -> int:
    for idx in range(1, len(block)):
        if all(l == r for l, r in zip(reversed(block[:idx]), block[idx:])):
            return idx

    return 0
```

`zip` lets us pair up lines and handles stopping the reflections when the shorter one ends. We also skip the first line, since there's nothing above it to reflect. If there's no match, we return `0` to signal to the caller that we need to try column instead.

We can now score any blocks that are horizontal reflections:

```py
def score_block(block: str) -> int:
    rows = block.split("\n")
    if row := reflection_row(rows):
        return 100 * row

    # TODO: columns
```

Now for the trick. We _could_ write a `reflection_col` that's a sideways version of `reflection_row`. Or... we rotate the input. Because a reflection column moving left to right is basically the same as the row moving top to bottom, this might just work.

There's a trick with `zip` that allows us to do exactly what we need:

```py
l = ['qwer', 'asdf', 'zxcv']
# [
#   'qwer',
#   'asdf',
#   'zxcv',
# ]

list(zip(*l))
# [('q', 'a', 'z'), ('w', 's', 'x'), ('e', 'd', 'c'), ('r', 'f', 'v')]
```

This zipped list moves one column at a time instead of one row, which is exactly what I "rotated" list would do. We can plug that into our `reflection_row` without further changes:

```py ins={6,7}
def score_block(block: str) -> int:
    rows = block.split("\n")
    if row := reflection_row(rows):
        return 100 * row

    if col := reflection_row(list(zip(*rows))):
        return col

    # not strictly necessary... if our code works on the first try
    # useful otherwise!
    raise ValueError("no reflection found!")
```

Sum our input up and we're off to part 2:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        return sum(score_block(block) for block in self.input.split("\n\n"))
```

## Part 2

Goo news: this sounds worse than it is.

In part 1, we had to make sure every matched pair were identical. In part 2, we need exactly _one_ pair to differ by a single character. This means we'll need a way to count the differences between a list of strings.

Here's our `difference` function, which takes advantage of the fact that `bool`s are `int`s and can be added:

```py
def distance(l: str, r: str) -> int:
    return sum(a != b for a, b in zip(l, r))
```

For identical strings, we'll be adding up a big list of `0`s. For unrelated strings it'll be some large number. For our "smudged" strings, it'll be exactly `1` (since most characters will be the same, but a single pair will differ).

Now we can plug it back into our `reflection` function:

```py ins=", distance_to_match: int" ins=", distance_to_match" ins={8-11}
...

def reflection_row(block: list[str], distance_to_match: int) -> int:
    for idx in range(len(block)):
        if idx == 0:
            continue

        if (
            sum(distance(l, r) for l, r in zip(reversed(block[:idx]), block[idx:]))
            == distance_to_match
        ):
            return idx

    return 0

def score_block(block: str, distance_to_match: int) -> int:
    rows = block.split("\n")
    if row := reflection_row(rows, distance_to_match):
        return 100 * row

    if col := reflection_row(list(zip(*rows)), distance_to_match):
        return col

    raise ValueError("no reflection found!")
```

And finally, we can tweak our runners:

```py ins=", 0" ins=", 1"
class Solution(TextSolution):
    def part_1(self) -> int:
        return sum(score_block(block, 0) for block in self.input.split("\n\n"))

    def part_2(self) -> int:
        return sum(score_block(block, 1) for block in self.input.split("\n\n"))
```

And that should do it!
