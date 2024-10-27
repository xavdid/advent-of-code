---
year: 2023
day: 1
title: "Trebuchet?!"
slug: 2023/day/1
pub_date: "2023-11-30"
---

Welcome, one and all, to Advent of Code 2023! I'm excited for another year deepening my Python and puzzle solving expertise.

It's a bright new (puzzle) year and you're reading this on a beautiful new website. If you'd like to learn more about it I wrote a little [blog post](https://xavd.id/blog/post/building-aoc-showcase/) about it earlier this year.

If this is your first time reading my solutions, I recommending reading through [this site's homepage](/#audience), which will explain what I expect a reader to be familiar with.

With that out of the way, Let's dive in!

## Part 1

We've got some computation to do before take our place aboard the [superior seige engine](https://www.military.com/off-duty/2020/01/31/why-trebuchet-was-superior-siege-engine.html). At this point, all we need is the digits out of the string. Python's got a string method, `.isdigit()`, that will do exactly what we need. Let's use it in a list comprehension to filter out anything that isn't a digit:

```py
def calculate_calibration(s: str) -> int:
    digits = [c for c in s if c.isdigit()]
    assert digits, "empty array!"
```

The `assert` ensures that if a line doesn't have _any_ digits, we know early and loudly (rather than finding weird bugs later).

Next, we'll build a number from the first and last items in our `digits` list (which might be the same element):

```py
def calculate_calibration(s: str) -> int:
    ...

    return int(digits[0] + digits[-1])
```

Back in our `part_1` function, we'll loop over our input lines and call the function:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(calculate_calibration(line) for line in self.input)
```

And boom! Star 1, in the bag.

## Part 2

Next, we have to replace the names of digits with numbers; easy enough. First we define the number names and their digits:

```py
NUMBERS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
```

And in our calibration function, we replace all instances of each word with its digit:

```py ins=", replace_nums=False" ins={2-4}
def calculate_calibration(s: str, replace_nums=False) -> int:
    if replace_nums:
        for num, digit in NUMBERS.items():
            s = s.replace(num, digit)

    ...
```

And that should do... wait. That doesn't even pass the sample input. Huh.

Taking a closer look at the examples, we see a couple of test cases for which this code fails. Namely, the examples `eightwothree` and `xtwone3four`. Because Python dicts remember their insertion order, we replace the numbers in numerical order. Because some of the numbers overlap, by replacing the entire word, we inadvertently changed which words appear in the input. For example, `eightwothree` becomes `eigh23` instead of `823`.

So, when doing our replacements we _can't_ destroy any overlaps. A quick read shows us that two number names can only overlap by a single letter (that is, there's no names whose last 2 letters are the start of another number). So, when replacing words, we have to do so in a way that doesn't change their first or last letters in the string (while still adding the digit). Once we've thought it through that way, it's easy enough:

```py add="f"{num[0]}{digit}{num[-1]}""
def calculate_calibration(s: str, replace_nums=False) -> int:
    if replace_nums:
        for num, digit in NUMBERS.items():
            # don't remove the word, since some words are used twice
            s = s.replace(num, f"{num[0]}{digit}{num[-1]}")

    ...
```

Now our replacement of `eightwothree` goes:

1. `eight2othree`
2. `eight2ot3e`
3. `e8t2ot3e`

Which when fed through our original function from part 1 yields the correct answer.

Phew! I think this takes the cake for the day 1 with the most edge cases. Hopefully that's not a preview of things to come.
