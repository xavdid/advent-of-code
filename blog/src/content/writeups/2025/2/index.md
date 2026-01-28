---
year: 2025
day: 2
slug: "2025/day/2"
title: "Gift Shop"
concepts: [regex]
pub_date: "2026-01-27"
---

## Part 1

Today we'll take advantage of one of Python's unsung heroes: the `range` class. We'll use them to store the start and stop of each range in our input before iterating over them to verify validity.

My solution relies on two utility functions: one for parsing the input and one for determining the validity of an ID. Let's parse.

```py
def parse_range(s: str) -> range:
    l, r = s.split("-")
    return range(int(l), int(r) + 1)
```

The only tricky bit is the `+ 1` at the end, since we want the ranges to be inclusive. That is, the `11-22` in our input should include both the numbers `11` and `22`, so the Python `range` is `range(11, 23)`.

Next is validity. Based on the examples, the (string representation of a) number needs to be:

- an even number of digits
- have its first half match its second half

That's easy enough to write:

```py
def is_valid(i: int) -> bool:
    s = str(i)
    str_len = len(s)
    if str_len % 2 == 1:
        return True

    midpoint = str_len // 2

    return s[:midpoint] != s[midpoint:]
```

Now we put it all together:

```py
class Solution(StrSplitSolution):
    separator = ","

    def part_1(self) -> int:
        ranges = [parse_range(r) for r in self.input]

        total = 0

        for r in ranges:
            total += sum(i for i in r if not is_valid(i))

        return total
```

> Remember, this solution takes advantage of the basic parsing logic in my [AoC Python template](https://github.com/xavdid/advent-of-code-python-template), so the top-level code won't work out of the box for you unless you're using it
>
> In this case, it's reading the input file and calling `text.split(separator)`, which gives us a nice list of `"12-34"` strings.

And that works! But we can fix it up a bit. We're only adding numbers into `total`, which is a signal we can just build a list of numbers instead and sum them up at the end. Here's equivalent code:

```py
from itertools import chain
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ranges = [parse_range(r) for r in self.input]

        return sum(i for i in chain.from_iterable(ranges) if not is_valid(i))
```

Or as a 1-liner:

```py
return sum(
    i
    for i in chain.from_iterable(map(parse_range, self.input))
    if not is_valid(i)
)
```

Both these approaches use `chain.from_iterable`, which makes one long iterable out of a bunch of smaller ones. It basically lets us iterate `[[1,2], [3,4], [5,6]]` like it was `[1,2,3,4,5,6]`, which is perfect for a list of ranges.

## Part 2

Part 2 is much the same, but we have to account for multiple repeats.

First, let's refactor our code so that solving parts 1 and 2 are as easy as supplying a validity function:

```py ins={1,6,13,14} del={5}
from typing import Callable
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def _solve(self, validity_func: Callable[[int], bool]) -> int:
        return sum(
            i
            for i in chain.from_iterable(map(parse_range, self.input))
            if not validity_func(i)
        )

    def part_1(self) -> int:
        return self._solve(is_valid)
```

Now we can swap in a new argument to `self._solve` to handle different requirements!

So, the repetition. There's an interesting way to do this and a simple way; let's see each.

### The interesting way

As I was going through the test cases, a pattern started to emerge. An invalid number consists of a substring whose number of occurrences times its length is equal to the length of the string.

For example, take `121212`. The substring `12` has a length of 2 and occurs 3 times in the string. Since `2 * 3 == 6` and the original string has a length of `6`, it must be invalid!

To correctly verify a string, we have to check every substring up to half its length (rounded down). It's not super efficient, but it's pretty easy to code. The hardest part is the edge cases:

```py
def is_valid_repeated(i: int) -> bool:
    s = str(i)
    str_len = len(s)

    # 1-length nums can't have repeated digits
    if str_len == 1:
        return True

    # a single number repeated is invalid
    if len(set(s)) == 1:
        return False

    midpoint = str_len // 2
    for substr_len in range(2, midpoint + 1):
        num_occurances = s.count(s[:substr_len])
        if num_occurances * substr_len == str_len:
            return False

    return True

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return self._solve(is_valid_repeated)
```

And we have our answer! While the solution itself is elegant, repeatedly counting substring occurrences is fairly inefficient. If only there was a simpler way...

### The simple way

Whenever you're matching text in a specific shape, regular expressions are your friend. In our case we want some number which is repeated at least one time. That's a 1-liner:

```py
import re

def is_valid_repeated_regex(i: int) -> bool:
    return not re.match(r"^(\d+)\1+$", str(i))
```

Regex can be intimidating, but looking at them one bit at a time helps translate them to plain english. Let's break it down:

- `^` is the start of the string
- `(\d+)` is a capture group consisting of 1 or more digits (`0-9`). Basically, a thing that, if matched, we can refer to later
- `\1+` is a reference to the first capture group, also repeated 1+ times (hence the `+`)
- `$` is the end of the string

So just like it says on the tin: we want a string that's a number followed by repeats of that number, then the end of the string. This does exactly that!

If you want to play around with this regex more, you can use this [interactive version](https://regex101.com/r/kmvHr2/1).

---

In the end, I was surprised at the lack of time difference between the approaches. I sort of thought regex would be way faster, but it was only about a .3s difference. Just goes to show - don't [optimize too early](https://en.wikipedia.org/wiki/Program_optimization#When_to_optimize)!
