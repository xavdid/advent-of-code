---
year: 2022
day: 4
title: "Camp Cleanup"
slug: "2022/day/4"
pub_date: "2022-12-04"
---

## Part 1

Like the the last few days, there are a couple of steps to each part:

- parse input into a usable form factor
- do some calculation for each line
- return the sum of the results

Let's do it again!

First is input parsing. We want to turn a pair of `-`-separated numbers into all of the numbers in that range. Python's `range` function does this admirably:

```py
def pair_to_range(pair: str):
    start, stop = pair.split("-")
    return set(range(int(start), int(stop) + 1))
```

We have to include the `+ 1` at the end because the `range` function doesn't include the last element (e.g. `range(1,3)` is just `[1, 2]`). We're also returning a `set` instead of a `range` object, because being able to do set operations later makes our life much easier.[^1]

This next part should look familiar- for each line, we split it by `,` and map the `pair_to_range` function over the items:

```py
# list(tuple(...)) included for intermediate clarity
# will be removed soon
list(tuple(map(pair_to_range, line.split(","))) for line in self.input)
```

We now have a `List[Tuple[Set[int]]]` (each item in the root list is a 2-tuple of sets (which contain ints)). Here's the sample input if that's tough to visualize:

```
[
    ({2, 3, 4}, {8, 6, 7}),
    ({2, 3}, {4, 5}),
    ({5, 6, 7}, {8, 9, 7}),
    ({2, 3, 4, 5, 6, 7, 8}, {3, 4, 5, 6, 7}),
    ({6}, {4, 5, 6}),
    ({2, 3, 4, 5, 6}, {4, 5, 6, 7, 8})
]
```

Now, on each of these pairs of sets, we'll need to determine if either is a subset of the other. Python makes this simple:

```py
from typing import Set

# include extra type information
# helps with IDE hints, but isn't required for the solution
ISet = Set[int]

def is_either_subset(a: ISet, b: ISet) -> bool:
    return a <= b or b <= a
```

The `<=` operator between sets implicitly calls the `issubset` method ([docs](https://docs.python.org/3.11/library/stdtypes.html#frozenset.issubset)), which tells us exactly what we need to know: do either of the ranges totally encompass the other?

Now we need to call our function from a list comprehension. Unfortunately, our function takes 2 arguments (`a` and `b`), but the `map` function only returns one item (the generator). Luckily, we can use Python's spread operator (`*`) to bridge the gap!

It lets us "spread" a variable to function arguments easily:

```py
# a contrived example
def add(a, b):
    return a + b

numbers = (1, 2)

# 1 tuple can't become 2 arguments
add(numbers) # TypeError: add() missing 1 required positional argument: 'b'

# unless you "spread" it!
add(*numbers) # 3

# make sure the element length lines up though...
add(*(1,2,3)) # TypeError: add() takes 2 positional arguments but 3 were given
```

Because we know our function takes exactly 2 arguments and our `map` result is exactly 2 elements long, we can safely use the spread operator to combine the two. All together, with sum:

```py
return sum(
    is_either_subset(*map(pair_to_range, line.split(",")))
    for line in self.input
)
```

Eagle-eyed readers will note one last curiosity- `is_either_subset` returns a `bool`, yet we can safely pass the resulting `List[bool]` into `sum`. It happens that Python's boolean classes are subclasses of integers, meaning anywhere you can use an `int`, you can use a `bool` instead. That's why `True + True` returns `2` and not some weird error. Little bit of fun trivia to round out part 1.

## Part 2

Ironically, part 2 is slightly simpler for us, given that we already have sets (a data structure for which finding if there's _any_ overlap is notoriously easy). Everything about the answer is the same, we just need a new function to pass our sets into. It's a one-liner:

```py
...

def do_ranges_overlap(a: ISet, b: ISet) -> bool:
    return bool(a & b)
```

Plug that into our answer from part one (replacing `is_either_subset`) and that's it!

## One More Thing

Given that parts 1 and 2 are _so_ similar, it seems a shame to [repeat so much code](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)...

Because Python functions are first-class objects (meaning they can be passed around as arguments themselves), we could write a core function that does our mapping/splitting/etc and then provide the filterer as an argument. Here's how that would look:

```py
from typing import Callable, Set
...

class Solution(StrSplitSolution):
    ...

    # a function is typed as a "Callable", which provides info
    # about its argument type(s) and return value
    def _solve(self, f: Callable[[Set[int], Set[int]], bool]) -> int:
        return sum(f(*map(pair_to_range, line.split(","))) for line in self.input)
```

Then, part 1 becomes `return self._solve(is_either_subset)`. Note that we don't call `is_either_subset` here- we're just specifying which function eventually gets called.

### And Another One

Now that we've come this far, there's one more step towards simplicity we can take. Our `is_either_subset` and `do_ranges_overlap` functions are _pretty_ simple. Instead of devoting 3 lines to defining and naming a function we really only use in one place, we could define it anonymously, inline. Python's lambda functions do just that:

```py
self._solve(lambda a, b: a <= b or b <= a)
self._solve(lambda a, b: bool(a & b))
```

Sometimes seen as _too_ concise, lambdas are great for writing single-use one-line functions (like we need here!). The only odd thing about them is that the `return` is implicit- the whole expression after the `:` is what gets returned.

These in hand. our final code becomes:

```py
from typing import Callable, Set

from ...base import StrSplitSolution


def pair_to_range(pair: str) -> Set[int]:
    start, stop = pair.split("-")
    return set(range(int(start), int(stop) + 1))


class Solution(StrSplitSolution):
    def _solve(self, f: Callable[[Set[int], Set[int]], bool]) -> int:
        return sum(f(*map(pair_to_range, line.split(","))) for line in self.input)

    def part_1(self) -> int:
        return self._solve(lambda a, b: a <= b or b <= a)

    def part_2(self) -> int:
        return self._solve(lambda a, b: bool(a & b))
```

Concise, yet still quite readable!

[^1]: The big advantage of `range` is that, as a generator, it doesn't have to store all of the numbers in its range at once; `range(10)` and `range(100)` use the same amount of memory. But, because we need to know about all of the numbers _in_ the range, we'll discard that advantage.
