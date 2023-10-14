---
year: 2021
day: 8
title: "Seven Segment Search"
slug: "2021/day/8"
pub_date: "2021-12-09"
---

## Part 1

This is a _lot_ of reading, but not actually too bad. First it describes a "Seven Segment Display" where, using up to 7 segments, you can make any digit 0-9. Then, it assigns letters to those segments. Now, you can represent any digit with a set of letters. In the diagram, segments `c` and `f` are the right side verticals. So `cf` -> `1`. If you add the top (`a`), you get a 7 instead (`acf` -> `7`). This also means that each digit has a known number of segments (`1` is always made of 2 letters, `7` is always made of 3, etc). It'll be important to understand that concept, but not until part 2.

For now, we only have to worry about the right side of the input (after the `|`). The prompt tell us that the digits `1`, `4`, `7`, and `8` have unique numbers of segments. This is true! If you have a 3-letter digit (such as `acf`), it _has_ to map to `7`. Part 1 is asking how many of those pre-defined digits are found on the right side of the input. Or, put another way: "how many items on the right have a length of 2, 3, 4, or 7?" (the number of segments for each of the 4 numbers discussed above). When you put it that way, this part isn't too bad:

```py
# hardcoded unique segment lengths
UNIQUE_SIZES = {2, 3, 4, 7}

total = 0
for line in self.input:
    _, wires = line.split(" | ")
    total += sum([1 for x in wires.split() if len(x) in UNIQUE_SIZES])
return total
```

This solution combines a couple of neat tricks:

- combines a list comprehension and filter, like we've seen before
- uses `1 for x in ...` instead of `x for x`. This is so we can sum up the `1`s and get how many items were left. This could have also been written `len([x for x in ...`, but I figured it was worth showing this feature off. You can return anything in the first spot of a list comprehension!

Anyway, I've got a feeling part 2 is going to have a lot more steps...

## Part 2

And so it does. Now we have to decode the numbers on each line. We'll be doing this via process of elimination and working our way up.

For each line in our input, we'll need to create a mapping of the actual number (`1`) to its scrambled result (`ab`). I thought we'd have to solve for individual segments, but we actually don't need to- we can instead start with some freebies and compare our way home.

We'll be doing a lot of filtering list comprehensions here. I wrote a little helper to validate assumptions:

```py
from typing import List


def validate(i: List[str]):
    assert len(i) == 1
    return i[0]

result[1] = validate([x for x in digits if len(x) == 2])
```

For each comprehension, I'm assuming I've filtered the list down to a single item. While solving, I was taking a different approach, using an iterator and the `next` function:

```py
result[1] = next(x for x in digits if len(x) == 2)
```

That gives me the first item in the iterator. If my logic is sound, then they work the same way. But, if I have a bug (and I did), then I'll get the first of multiple possible options, leading to a bug. So, I made sure to start validating assumptions as I went.

Anyway, let's get to the solve.

As we solve this, we'll be using a lot of `set`s. This is because order doesn't matter (so we don't need a `list`). We actually want to specifically _ignore_ the order. We'd be sad if the input was `ba` and we were checking against `ab`. Plus, they make some of this math very easy.

We start with a loop and our freebies from part 1:

```py
total = 0
for line in self.input:
    digits, number = line.split(" | ")
    result: Dict[int, str] = {}

    digits = digits.split()

    result[1] = validate([x for x in digits if len(x) == 2])
    result[4] = validate([x for x in digits if len(x) == 4])
    result[7] = validate([x for x in digits if len(x) == 3])
    result[8] = validate([x for x in digits if len(x) == 7])

    # using one-liner sample input:
    # {1: 'ab', 4: 'eafb', 7: 'dab', 8: 'acedgfb'}
```

Easy enough- we knew about those from part one.

Now, there are 6 numbers remaining. They fall into two groups: 5 segments (`2`, `3`, `5`) and 6 segments (`0`, `6`, `9`). In each group, there's an odd number out:

- `3` has 5 letters and _does_ contain both letters for `1`
- `6` has 6 letters and _doesn't_ contain both letters for `1`

We can write that in Python code just like we did before:

```py
for line in self.input:
    ...

    result[6] = validate(
        [x for x in digits if len(x) == 6 and not set(result[1]) < set(x)]
    )
    result[3] = validate(
        [x for x in digits if len(x) == 5 and set(result[1]) < set(x)]
    )
```

Now we can clear out used numbers:

```py
for line in self.input:
    ...

    found = set(result.values())
    digits = [x for x in digits if x not in found]
```

There are two groups left, each with two items. We can identify `9` within its group because it's a strict superset of `4` (that is, it contains everything in `4`); the same cannot be said of `0`. So we can spot `9` and `0` is the other one with the same length:

```py
for line in self.input:
    ...

    result[9] = validate(
        [x for x in digits if len(x) == 6 and set(result[4]) < set(x)]
    )
    result[0] = validate([x for x in digits if len(x) == 6 and x != result[9]])
```

One more clear out to make our last couple of lines simpler.

```py
for line in self.input:
    ...

    found = set(result.values())
    digits = [x for x in digits if x not in found]
```

For this last part, I solved for a segment. We know that `8` and `9` share nearly all of their letters. The only one that `9` lacks is the bottom left segment. Conveniently, that letter only appears in `2`:

```py
    ...
    bottom_left = (set(result[8]) - set(result[9])).pop()
    result[2] = validate([x for x in digits if bottom_left in x])
    result[5] = validate([x for x in digits if x != result[2]])
```

That's all our numbers! Now we have to reverse our `result` so we can plug the input back into it:

```py
for line in self.input:
    ...

    decoded = {frozenset(v): str(k) for k, v in result.items()}
```

Here we use a _dict_ comprehension (instead of the `list`) one we've been doing before. It's a similar setup, but the output is a `dict` instead of a `list`. The same can be done with `set`s, which can be useful. Also note that we're using a `frozenset` as the key instead of a regular `set`. That's because `dict` keys in Python have to be _hashable_; to be hashable, a variable must be immutable (never changing). Sets and lists can change (using `.add` and `.append` respectively), so they throw errors when used as keys. A `frozenset` promises that it and all of its members will never change, so we can use them as keys to look up our digit.

Last, we add to our total:

```py
for line in self.input:
    ...

    total += int("".join([decoded[frozenset(x)] for x in number.split()]))

return total
```

It looked intimidating and took a bit of logic, but we got there! I liked that one.
