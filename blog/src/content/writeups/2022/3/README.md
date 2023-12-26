---
year: 2022
day: 3
title: "Rucksack Reorganization"
slug: "2022/day/3"
pub_date: "2022-12-03"
---

## Part 1

We're going to tackle today back to front - we'll start with a function to calculate the priority for a letter. This seems a little daunting, but Python's built-in `ascii_letters` string comes in clutch here. It's all the lowercase letters followed by all the uppercase letters, which is exactly what we need![^1]

```py
from string import ascii_letters

def priority(letter: str) -> int:
    return ascii_letters.index(letter) + 1
```

Next, given a string, we have to split it in two equal halves. We can assume that all our input is well-formed (no odd-numbered-length lines), so we can assume that `length / 2` is the middle index. This works nicely with Python's array slices:

```py
def overlap_value(rucksack: str) -> int:
    mid_point = len(rucksack) // 2
    first_half = rucksack[:mid_point] # string from 0 to middle
    second_half = rucksack[mid_point:] # string from middle to end

    ...
```

Finding the overlap is also straightforward- we can turn each half into a set and take their intersection with `&`, which will tell us which element(s) are in both sets:

```py
def overlap_value(rucksack: str) -> int:
    mid_point = len(rucksack) // 2
    shared = set(rucksack[:mid_point]) & set(rucksack[mid_point:])

    ...
```

Finally, we run that through our `priority` function to get the answer for a given line:

```py
def overlap_value(rucksack: str) -> int:
    mid_point = len(rucksack) // 2
    shared = set(rucksack[:mid_point]) & set(rucksack[mid_point:])
    return priority(shared.pop()) # .pop() because you can't subscript a set
```

If we wanted to be defensive in our code, this would be a great place to `assert` our assumptions, such as `len(rucksack) % 2 == 0` and `len(shared) == 1`. If either of these is false, our code will produce the wrong answer but wouldn't throw an error, a notoriously tricky bug to find.

All that remains is to load our input into a list comprehension:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(overlap_value(rucksack) for rucksack in self.input)
```

## Part 2

This solution will be very similar to part 1, but we'll need a way to get groups of elves, 3 at a time. I'll adapt one of my most-visited [StackOverflow snippets](https://stackoverflow.com/a/312464/1825390):

```py
class Solution(StrSplitSolution):
    ...

    def groups(self):
        """Yield successive groups of 3 from input"""
        n = 3
        for i in range(0, len(self.input), n):
            yield self.input[i : i + n]
```

This function uses `yield` in place of `return`, meaning it (implicitly) returns a generator! This is a very memory efficient construct I talked about in [day 1](/writeups/2022/day/1/#cleanup). In practice, it just means we can iterate through the result.

This lets us easily get 3 elves at a time out of our input. Put that in another list comprehension, and that's our day:

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return sum(
            priority((set(a) & set(b) & set(c)).pop()) for a, b, c in self.groups()
        )
```

We're using Python's "destructuring assignment" here, which lets us assign new variables from an iterable:

```py
a, b, c = [1, 2, 3]
```

This errors if the number of variables don't match the length of the iterable, but since we know we'll always have 3 elves, we're safe here.

Congrats on day 3!

[^1]: there's also `string.ascii_uppercase` and `string.ascii_lowercase` if we needed only part of them, or wanted to reorder the cases.
