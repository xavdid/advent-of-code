---
year: 2023
day: 15
slug: 2023/day/15
title: "Lens Library"
pub_date: "2023-12-18"
---

## Part 1

Part 1 seems to just be an exercise in following instructions, so let's do that. The only potentially unfamiliar thing is the global `ord` function, which returns the ASCII value for a character. `ord('H') == 72` lines up with the example perfectly, so that's all we need for that bit. The rest is basic math:

```py
def make_hash(ins: str) -> int:
    result = 0

    for c in ins:
        result += ord(c)
        result *= 17
        result %= 256

    return result

class Solution(StrSplitSolution):
    separator = ","

    def part_1(self) -> int:
        return sum(make_hash(ins) for ins in self.input)
```

Which seems much too straightforward for a day 15, but here we are. Onward!

## Part 2

Despite being a whole lot of text, this one is surprisingly straightforward. We've got 256 items that each need to maintain a structure that can handle ordered keys and values. We could build a list that held 2-tuples of key+value (so we could find a pair by key), but you can't modify tuples and it'll get messy fast. Instead, we'll use a plain `dict`.

Now, you've probably heard that you should use a `list` if the order of you data matters, and that's mostly true. But, ever since Python 3.6, dictionaries have retained their insertion order. That means we'll be able to iterate over a dict's keys in the order they were created. Updates don't change the order either and removing a key means everything behind it moves "forward" without having to actually do anything!

We'll start with a `defaultdict` that maps box ids to `dict`s (which are each a box). From there, we're just doing a little string parsing and adding/removing values to the box locations:

```py
from collections import defaultdict
...

class Solution(StrSplitSolution):
    separator = ","
    ...

    def part_2(self) -> int:
        lenses: dict[int, dict[str, int]] = defaultdict(dict)

        for ins in self.input:
            if "-" in ins:
                label = ins[:-1] # "abc-"
                lenses[make_hash(label)].pop(label, None)
            elif "=" in ins:
                label, val_str = ins.split("=") # "abc=6"
                lenses[make_hash(label)][label] = int(val_str)
            else:
                raise ValueError(f"unrecognized pattern: {ins}")
```

There are only two cases, so we can do some very simple parsing rather than reach for anything like pattern matching. Everything else is fairly basic Python, so not much to say.

The last thing is summing up the results. We have to look at each box and, inside that, loop over the lenses (in order!) and do the math. I used a nested comprehension (which I usually don't go for), but some descriptive variable names make it pretty readable:

```py ins={11-17}
...

class Solution(StrSplitSolution):
    separator = ","
    ...

    def part_2(self) -> int:
        lenses: dict[int, dict[str, int]] = defaultdict(dict)
        ...

        return sum(
            sum(
                (box_id + 1) * (lense_pos + 1) * (focal_length)
                for lense_pos, focal_length in enumerate(box.values())
            )
            for box_id, box in lenses.items()
        )
```

And that's all there is to it! I imagine this was much trickier in other languages? Because it didn't feel like a day 15 in Python. Let's not look a gift puzzle in the mouth, I guess.
