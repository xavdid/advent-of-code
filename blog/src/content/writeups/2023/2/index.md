---
year: 2023
day: 2
title: "Cube Conundrum"
slug: 2023/day/2
pub_date: "2023-12-01"
concepts: ["regex"]
---

## Part 1

Welcome to day 2! The meat of today's puzzle is extracting data from the input, so that's where we'll start. On each line, we need 2 pieces of information:

1. the game id
2. pairs of count & color of handfuls of marbles

While we could pull the game id out of the input itself, the ids are in order, so we can lean on a built-in iterator index instead:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        total = 0

        for idx, game_info in enumerate(self.input):
            _, marbles = game_info.split(": ")

            if False: # TBD
                total += idx + 1

        return total
```

We haven't written our actual condition check yet, but we have a rough outline of what we're doing. If some condition is met, we add the game's id (which is 1 more than its index in the list) to the total, which we'll eventually return. This uses the built-in `enumerate` function ([more info](https://realpython.com/python-enumerate/)) to iterate through each element and its index.

Now for the good stuff. We need to extract each count & color pair from the rest of each line. At first, I was splitting by semi-colon and then splitting and iterating again, but no part of the puzzle actually requires differentiating between each set of marbles. We only care that each number is under a certain value (based on its color). Extracting values out of structured text is exactly what [regular expressions](https://realpython.com/regex-python/) (or regex) are useful for, so we'll start there!

<figure>
  <img src="https://imgs.xkcd.com/comics/perl_problems.png" />
  <figcaption><a href="https://xkcd.com/1171/">obligatory xkcd</a></figcaption>
</figure>

A lot of people are intimidated or scared of regex, but they're one of the most useful tools in a programmer's arsenal.

A regex has two parts:

1. an expression, a string which describes the shape of text you want to search for
2. an input string (here, `3 blue, 4 red; 1 red...`)

We have to describe the sort of text we want to extract in a specific way. In our case, we want a number followed by a space, followed by a word. In regex, we'd write that as `(\d+) (\w+)`. Let's break that down:

1. `\d` means "any digit"
2. `+` means "1 or more of the last thing
3. the space means "there needs to be an actual space next"
4. `\w` means "any alphanumeric character"
5. the next `+` is the same
6. the parenthesis mean "extract everything in here as a group", which I'll get to momentarily

Not so bad right? Once you learn what all of the characters mean, you can really fly. Here's an [interactive version of that regex](https://regex101.com/r/ujv6r7/1) if you want to play with it more. We'll see a lot more of these, so I'd get comfortable with them.

When you're ready, we can use the `re.findall` function (using Python's built-in r(egular) e(xpression) module) to see all the pairs:

```py
re.findall(r"(\d+) (\w+)", "3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green")

# [
#   ('3', 'blue'),
#   ('4', 'red'),
#   ('1', 'red'),
#   ('2', 'green'),
#   ('6', 'blue'),
#   ('2', 'green'),
# ]
```

Looks pretty useful, right?

For each of those pairs, we have to enure the number is less than the max value for that color. A little lookup table can get us that info. Lastly, we need to wrap that check in an `all` function, which verifies whether every item in a list is truthy. Let's put that all together:

```py ins={1, 9-12}
import re

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        total = 0

        for idx, game_info in enumerate(self.input):
            _, marbles = game_info.split(": ")
            if all(
                int(count) <= {"red": 12, "green": 13, "blue": 14}[color]
                for count, color in re.findall(r"(\d+) (\w+)", marbles)
            ):
                total += idx + 1

        return total
```

It gets a little dense with that list comprehension, but I find it pretty readable! For each `count, color`, we return whether `count <=` the value in the dict. Since there's only 3 keys, we just inline it right there. We only add the index if every item in the list returns true, which is exactly what we needed. That's all there was to part 1!

## Part 2

Part 2 is very similar, except we have different data to track. For each row, we need the biggest value for each color. There are a few ways to go about this, but they mostly involve further parsing of the input; I think sticking with our regex is great.

For each line, we'll store the larger of the previous value or the new one. We could use `.get(color, 0)` to easily handle missing keys, but Python's `collections.defaultdict` cleans this code up a bit (by returning `0` instead of a `KeyError` when you ask for a missing key). Here's our part 2 solution:

```py ins={3-5, 15,18,20}
...

from collections import defaultdict
from functools import reduce
from operator import mul

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        total = 0

        for game_info in self.input:
            _, marbles = game_info.split(": ")
            mins: dict[str, int] = defaultdict(int)

            for count, color in re.findall(r"(\d+) (\w+)", marbles):
                mins[color] = max(mins[color], int(count))

            total += reduce(lambda x, y: x * y, mins.values())

        return total
```

The only other function of note is `reduce`, which you may not be familiar with. Its goal is to "reduce" an iterable into a single value. In the absence of a multiplication equivalent of the `sum` function, we're using it to multiply a bunch of numbers into a single one. You can [read more about it here](https://realpython.com/python-reduce-function/).

The gist is that `reduce` uses a function with 2 args to turn an iterable into a single value. The function is called repeatedly with the previous function result and the next element in the iterator. For our function, we opted for `operator.mul`, which is the operation that backs multiplication in Python. That is, `a * b` is the same as `mul(a, b)`. Since `reduce` needs a function with 2 arguments, `mul` is perfect!

By finding the max value of each color on each line, we've found our solution! Another day in the books.
