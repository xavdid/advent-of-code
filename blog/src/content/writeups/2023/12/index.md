---
year: 2023
day: 12
title: "Hot Springs"
slug: 2023/day/12
pub_date: "2023-12-15"
concepts: ["recursion", "dynamic programming"]
---

## Part 1

Today we're solving [nonograms](https://en.wikipedia.org/wiki/Nonogram)! These are puzzles I enjoy solving [on my phone](https://apps.apple.com/app/id574857255); let's see if we can do it algorithmically too.

I can't imagine this will work for part 2, but let's brute-force part 1. Each row can only have a certain number of combinations, so if we can determine if a row is valid, we can try every option and count the valid ones. Let's [start with the ending](https://www.youtube.com/watch?v=OwTiPQKaT3M) and work our way up.

First things first, we have to know if a puzzle is solved. If we have a list of groups of broken springs (`#`) and a list of group sizes, we can see if they match up:

```py
def is_valid(groups: list[str], counts: list[int]) -> bool:
    """
    do the listed groups of `#` match the required blueprint?
    """
    return len(groups) == len(counts) and all(
        len(l) == g for l, g in zip(groups, counts)
    )
```

This works for some basic tests:

```py
is_valid(['#', '##', '###'], [1, 2, 3]) # true
is_valid(['#', '###', '#'], [1, 3, 1]) # true
is_valid(['#', '##'], [1, 3]) # false
is_valid(['#', '##'], [1]) # false
```

Next, we need to turn a raw `record` (like `???.###`) into all of its possible combinations. Those 3 `?` could be anywhere between `0` and `3` `#`s and they could be in any position. If we had a list of indexes that could be replaced, we could use `itertools.combinations` to get each possibility. There's one wrinkle though - `combinations` takes a length:

```py
combinations('ABCD', 2) # AB AC AD BC BD CD
combinations('ABCD', 3) # ABC ABD ACD BCD
```

We need every possible length, so we'll have to wrap our call to `combinations` in its own iterator. Luckily, the [recipes](https://docs.python.org/3/library/itertools.html#itertools-recipes) section of the Python docs have just the thing for this! The `powerset` function:

```py
from itertools import chain, combinations

def powerset(l: list[int]):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l) + 1))
```

That looks like exactly what we need. It lets us build a function that shows every possible _combination_ of pipe arrangements. first, we get the indexes of the `?`. Then, we iterate through the powerset of those indexes (every combination of every length) and replace those indexes with `#`. Anything that's left must still be a `.` (for this loop). Then a `re.findall(r'#+')` to get a list of continuous block of springs will bring us home. Here's the whole thing:

```py
...
import re
from typing import Iterable

def every_solve_combination(record: str) -> Iterable[list[str]]:
    """
    yields every combination of lists of groups of broken springs (`#`)
    """
    unknown_indexes = [idx for idx, c in enumerate(record) if c == "?"]
    for indexes_to_replace in powerset(unknown_indexes):
        chars = list(record)
        for i in indexes_to_replace:
            chars[i] = "#"
        yield re.findall(r"#+", "".join(chars).replace("?", "."))
```

We're doing some splitting and joining, but nothing too weird. That gives us:

```py
list(every_solve_combination('???.###'))
# [
#     ["###"],
#     ["#", "###"],
#     ["#", "###"],
#     ["#", "###"],
#     ["##", "###"],
#     ["#", "#", "###"],
#     ["##", "###"],
#     ["###", "###"],
# ]
```

Now that we can validate if a `list of groups` matches a `shape` and we can get every `list of groups` from a `record`, all we need to do is count how many valid combinations we get from a `line`:

```py
def num_valid_combinations(line: str) -> int:
    record, raw_shape = line.split()
    shape = list(map(int, raw_shape.split(",")))

    return sum(is_valid(l, shape) for l in every_solve_combination(record))
```

And finally, run every line through that:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(num_valid_combinations(line) for line in self.input)
```

And it works! It runs in like 7 seconds, but it works! That's slower than I'd usually allow, but I didn't want to improve it further. I was pretty sure brute force wasn't going to work for part 2, so I'd be ripping it all out shortly anyway.

As I was looking for tips on part 2 (more on that below), I came across [this Reddit meme](https://old.reddit.com/r/adventofcode/comments/18gz9na/2023_day_12_part_2_i_paid_for_the_whole_cpu_so/) titled `i paid for the whole cpu so I'll use the whole cpu"` which cracked me up. I had never used the `multiprocessing` module so I decided to give it a try:

```py del={6} ins={7,8}
from multiprocessing import Pool
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(num_valid_combinations(line) for line in self.input)
        with Pool(processes=8) as pool:
            return sum(pool.map(num_valid_combinations, self.input))
```

That brought my solve time down from `7.6s` to `1.3s`; definitely in the realm of acceptable. This won't always work, but the fact that every line of our input is totally independent means we can divide an conquer the whole puzzle, hence the speed up. Unfortunately, I don't think that's going to get us far in part 2...

## Part 2

As I feared, the lines are now so long that no amount of brute-forcing will get us there. You can tell by the increase in size of the sample answer. For part 1, it's `21` but grows to `525152` in part 2. This tell us we won't be doing these calculations. Instead, we have to break the problem down so it'll work for lines of _any_ length.

It turns out there are a lot of ways to solve this problem, but I ended up going with a cached recursive one. I spun my wheels for a few days trying to think through a workable approach. I sort of knew I wanted to do it recursively, but I was having trouble thinking through exactly how it would work. Ultimately, [this great comment](https://old.reddit.com/r/adventofcode/comments/18ghux0/2023_day_12_no_idea_how_to_start_with_this_puzzle/kd0npmi/) by `/u/damaltor1` set me on the right track. Let's break it down.

Our problem was that records became too long to try all of the combinations. Instead of trying to solve big records, we could instead try solving smaller component records and adding the results. For example, `..?. 1` has the same number of valid combinations as `.?. 1` and `?. 1`. Once we've solved that smallest record, we will have also solved the larger ones. Break down enough large records and we'll have enough answers to solve any row. This process is known as "dynamic programming".

To solve a record definitively, we'll need to break the problem down into a _base case_, or a small version of our problem which we can't break down any further. All other versions of the record eventually break down to a base case. For us, there are 2:

1. our record (the `.#?` portion of the string) is empty, so we have nothing else to check. This case is valid only if we've used all our groups (of numbers)
2. there are no groups left, which is valid only if there are no `#` left

Those two cases translate nicely into the start of a new function:

```py
def num_valid_solutions(record: str, groups: tuple[int, ...]) -> int:
    if not record:
        # if there are no more spots to check;
        # our only chance at success is if there are no `groups` left
        return len(groups) == 0

    if not groups:
        # if there are no more groups the only possibility of success
        # is that there are no `#` remaining
        return "#" not in record
```

You'll note that in each case, we're returning a `bool`, not an `int`. That's because in Python, they're the same! `True` is just a special version of `1` (same with `False` and `0`) and they can be used interchangeably. That's why `True + True` is `2`.

Now for the [recursion](https://www.google.com/search?q=recursion). We have to empty out `record`s and `groups` until they fit into one of those 2 cases. `.` is the easiest; they are ignored! So we simply skip them and recurse with the rest of the record:

```py
def num_valid_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...

    char, rest_of_record = record[0], record[1:]

    if char == ".":
        # dots are ignores, so keep recursing
        return num_valid_solutions(rest_of_record, groups)
```

For the rest of the function, `char` will only be `#` or `?`. Next up is the trickier of the two: `#`. If `#` is the character at the start of the string, it means we're in a group of some size. To be valid here, we have to be able to fulfil that group by having the exact right number of `#` at the start of the record (and no more). At this point, we can treat any `?` as `#` because the only way we'll be valid is in the case where they all match.

We'll check 3 conditions:

```py ins={8-50}
def num_valid_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...

    char, rest_of_record = record[0], record[1:]

    ...

    if char == "#":
        group = groups[0]
        # we're at the start of a group! make sure there are enough here to fill the first group
        # to be valid, we have to be:
        if (
            # long enough to match
            len(record) >= group
            # made of only things that can be `#` (no `.`)
            and all(c != "." for c in record[:group])
            # either at the end of the record (allowed)
            # or the next character isn't also a `#` (would be too big)
            and (len(record) == group or record[group] != "#")
        ):
            return num_valid_solutions(record[group + 1 :], groups[1:])

        return 0
```

If all of those things are true, than this `record` is valid (so far) and we keep recursing to see how many valid combinations the rest of the `record` has. We do so by dropping everything from the matched group (and its immediate predecessor, which must be either a `.` or a `?` we're treating like a `.`). We also skip the group we just validated, which shrinks both `record` and `group` towards being empty (our base case). If anything didn't match, this isn't a valid string and we can immediately bail.

Last is the easy one - `?`. To resolve that, we add the number of valid solutions we'd get if the `?` was a `.` to the number we'd get if it were a `#`. Then we let the rest of the function do its thing:

```py ins={8-11}
def num_valid_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...

    char, rest_of_record = record[0], record[1:]

    ...

    if char == "?":
        return num_valid_solutions(f"#{rest_of_record}", groups) + num_valid_solutions(
            f".{rest_of_record}", groups
        )
```

This now-complete function will keep chopping records and groups until there's nothing left of one of them, at which time everything gets totaled up and we'll have our answer. Last thing is a small tweak to the root function to actually run everything:

```py ins={3-11,15,18}
...

def solve_line(line: str, with_multiplier=False) -> int:
    record, raw_shape = line.split()
    shape = tuple(map(int, raw_shape.split(",")))

    if with_multiplier:
        record = "?".join([record] * 5)
        shape *= 5

    return num_valid_solutions(record, shape)

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(solve_line(line) for line in self.input)

    def part_2(self) -> int:
        return sum(solve_line(line, with_multiplier=True) for line in self.input)
```

And... wait hang on, it's still looping forever. Ah, that's because we forgot the cherry on top that makes all of this possible: `functools.cache` ([docs](https://docs.python.org/3/library/functools.html#functools.cache)). It does the heavy lifting for reusing all our repeated computation:

```py ins={1,3}
from functools import cache

@cache
def num_valid_solutions(record: str, groups: tuple[int, ...]) -> int:
    ...
```

And _there_ it is. I see both parts complete in ~ `0.42s`, which feels pretty good after all the trouble it gave us. Great job today!
