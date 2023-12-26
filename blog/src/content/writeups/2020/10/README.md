---
year: 2020
day: 10
title: "Adapter Array"
slug: "2020/day/10"
pub_date: "2020-12-10"
---

## Part 1

Don't be intimidated by how wordy this prompt is - it's much simpler than it sounds.

After sorting our input, we want to track the difference between each pair of elements. Sorting elements is easy enough (after setting my `BaseSolution.input_type` to `InputTypes.INTSPLIT`). We also want to start with `0` and end with `max(self.input) + 3`:

```py
sorted_input: List[int] = sorted(self.input)
adapters = [0, *sorted_input, sorted_input[-1] + 3]
```

Here's another appearance of Python's `*` operator. It lets us flatten our input into an outside array. Here's a quick example:

```py
[0, [1, 2, 3], 4] # => [0, [1, 2, 3], 4]
[0, *[1, 2, 3], 4] # => [0, 1, 2, 3, 4]
```

There's also the neat `list[-1]`, which gets the last element of the list. Since `sorted_input` is sorted, using `[-1]` saves us a `max` call.

To track the number of differences concisely, we'll use `defaultdict`. It's like a regular Python `dict`, but instead of throwing `KeyError`s when a missing key is accessed, it instead initializes the value first (based on a class passed during initialization. That saves us from having to check if our value is in there yet:

```py
d = {}

d[1] += 3 # KeyError!

if 1 in d:
    d[1] += 3
else:
    d[1] = 3

# { 1: 3 }

# or
from collections import defaultdict
dd = defaultdict(int)
dd[1] += 3 # defaultdict(<class 'int'>, { 1: 3 })
```

Since we don't know what how many differences there'll be (the puzzle only worries about 1s and 3s, but there could be any number) then this will help keep our code tight.

The actual loop is straightforward. We check each element against the one right after it. The only trick is that we don't want to iterate right to the end because the last element doesn't have anything following it. Check it out:

```py
differences = defaultdict(int)
for index, val in enumerate(adapters[:-1]):
    diff = adapters[index + 1] - val
    differences[diff] += 1

return differences[1] * differences[3]
```

## Part 2

I'm pretty sure this is the first puzzle this year that can't be brute forced! This one was tough for me to wrap my head around, but the solution itself is pretty accessible. Similar to [day 7](/writeups/2020/day/7/), we need to solve small, simple problems to build up to our final answer.

Let's say our adapter list is `[(0), 1, 2, 4, 5, 6, (9)]`.

- The number of paths from `0 -> 1` is **1**:
  - direct link
- The number of paths from `0 -> 2` is **2**, the sum of:
  - direct link (1)
  - all the paths to get to `1` (1)
- The number of paths from `0 -> 4` is **3**, the sum of:
  - all the paths to get to `1` (1)
  - all the paths to get to `2` (2)
  - there's no `3` adapter, so there are no ways to use it in a path (0)
- The number of paths from `0 -> 5` is **5**, the sum of the values of its connections:
  - all the paths to get to `2` (2)
  - no `3` adapter (0)
  - all the paths to get to `4` (3)
- The number of paths from `0 -> 6` is **8**:
  - `1` and `2` are excluded because we can't jump straight from them to `6`. Same with the non-existent `3` (0)
  - all the paths to get to `4` (3)
  - all the paths to get to `5` (5)

Notice a pattern? Each new path is the sum of the 3 adapters that come before it (which is sometimes `0` if that adapter isn't present). If we loop through our adapters, we can build these computations from the ground up.

Code wise, this ends up being quite simple. We can use `defaultdict` again, which helpfully returns `0` for missing adapters:

```py
max_value = sorted_input[-1] + 3
adapters = [*sorted_input, max_value]
num_paths = defaultdict(int, {0: 1})
```

We pre-seeded our data with `{0: 1}` because the first connection needs to know that there's 1 way to get to zero (by starting there). From there, we iterate through each adapter and store the result for future use before finally returning the number of different paths to reach the `max_value` (3 + the biggest value in our input).

```py
for adapter in adapters:
    num_paths[adapter] = (
        num_paths[adapter - 1] + num_paths[adapter - 2] + num_paths[adapter - 3]
    )

return num_paths[max_value]
```

If you've been playing previous days and are curious why we didn't do this recursively (like [day 7](/writeups/2020/day/7/)), it's mostly because we didn't to! In this input, we knew all the connections ahead of time (`5` can only connect to `{2,3,4}`). With the bags, there wasn't a way to know what bags held `shiny gold` without parsing the whole tree structure.

Nevertheless, recursion is also possible. Such a solution gives me a great opportunity to introduce a Python feature that would have made day 7 much simpler...

### Part 2: Recursive Solution

If you haven't yet, skim through [day 7's extra credit portion](/writeups/2020/day/7/#part-1-extra-credit), where we cached recursion results so their results didn't need to be re-computed later.

Well, it turns out Python has a _function decorator_ that will help us do exactly that. Function decorators are functions that wrap other functions. The wrapper can store state (such as a cache), which turns out to be helpful for our needs.

Python version `3.9` introduced `functools.cache`. Each time the wrapped function is called, the input and output are cached. The next time the function is called with that same input, the cached result is returned instead. Sounds pretty familiar...

Our recursive code is pretty similar to the linear solution above, but the core functionality is wrapped in a function:

```py
max_value = max(self.input) + 3
adapters = set([0, *self.input, max_value])

@cache
def num_paths_to(val: int) -> int:
    if val not in adapters:
        return 0
    if val == 0:
        return 1

    return num_paths_to(val - 1) + num_paths_to(val - 2) + num_paths_to(val - 3)

return num_paths_to(max_value)
```

Notable differences are:

- no need to sort! We look at every number less than our max
- instead, we have a set that lets us quickly tell if we have that adapter
- same as with our previous recursive approach, we've got our base cases at the top and our computed values at the end

If you're using a Python version between `3.2` and `3.8`, you can use the following in instead of `@cache`:

```py
from functools import lru_cache

@lru_cache(maxsize=None)
def num_paths...
```
