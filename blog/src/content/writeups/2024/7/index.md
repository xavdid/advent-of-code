---
year: 2024
day: 7
slug: "2024/day/7"
title: "Bridge Repair"
# concepts: []
pub_date: "2024-12-07"
---

## Part 1

We'll start today, like most days, by parsing input. Since each line can be handled independently, we'll wrap all our logic into a single function that takes a full line:

```py
def process_line(line: str) -> int:
    target, *inputs = parse_int_list(line.replace(":", "").split())
```

Because there's a colon separating the numbers in addition to a space, we'd usually have to do multiple splits or use [a regex](https://docs.python.org/3/library/re.html#re.split). But, since we know our input is well formed, we can ignore the colon and safely assume our first element is the target anyway.

Next, we need to actually do our math. The easiest way to see if there's a match is to try every combination of operators. It may not scale for part 2, but that's a later us problem.

If there's `N` elements to check, there's space for `N-1` operators. We need to generate every single permutation (with repeats). Python's got a function for this:

```py
from itertools import product

list(product('AB', repeat=3))
# => [
#     ('A', 'A', 'A'),
#     ('A', 'A', 'B'),
#     ('A', 'B', 'A'),
#     ('A', 'B', 'B'),
#     ('B', 'A', 'A'),
#     ('B', 'A', 'B'),
#     ('B', 'B', 'A'),
#     ('B', 'B', 'B')
# ]
```

Instead of letters, we can use the pre-built `add` and `mul` functions from the `operator` module. Those, plus our list of numbers and we have everything we need to produce a total... except the algorithm, of course.

> I enjoy recursion, so I figured I'd give that a go. If you want a more thorough introduction to recursive concepts, I recommend jumping back to [2020 day 7](/writeups/2020/day/7/#rule-1-always-start-with-your-base-case) or Al Sweigart's [Recursive Book of Recursion](https://nostarch.com/recursive-book-recursion).

Our base case when there's only a single number left in the list. Otherwise, there's at least 2. We should perform the first operation on them and then recurse with the result as the first item in the array. Python's `*` operator makes it easy to pop the front item(s) off a list:

```py
from typing import Callable, Sequence

type Operation = Callable[[int, int], int]

def process_ops(nums: list[int], ops: Sequence[Operation]) -> int:
    if len(nums) == 1:
        return nums[0]

    l, r, *rest = nums
    cur_op, *remaining_ops = ops

    return process_ops([cur_op(l, r), *rest], remaining_ops)
```

Now we can jump back to `process_line`. We've got our numbers an operators, so now we tie it all together:

```py
from itertools import product
from operator import add, mul
...

def process_line(line: str) -> int:
    target, *inputs = parse_int_list(line.replace(":", "").split())

    ops = [add, mul]

    if any(
        process_ops(inputs, op_combo) == target
        for op_combo in product(ops, repeat=len(inputs) - 1)
    ):
        return target

    return 0
```

So our actual solution is only:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(map(process_line, self.input))
```

## Part 2

We're adding an extra operator, which doesn't sound like much. But since we need it in every slot, we're doing a bunch of extra computation. So much so that an adaptation of my 0.5s solution is going to take 22s to run! We can fix it, but we have to write it first.

The simple approach is to conditionally add a new operator to `process_line`. Python doesn't have a built-in "contact 2 ints", but it's easy to write:

```py rem={6} ins={3-4,7,11-12}
...

def concat(a: int, b: int) -> int:
    return int(str(a) + str(b))

def process_line(line: str) -> int:
def process_line(line: str, include_concat=False) -> int:
    target, *inputs = parse_int_list(line.replace(":", "").split())

    ops = [add, mul]
    if include_concat:
        ops.append(concat)

    if any(
        process_ops(inputs, op_combo) == target
        for op_combo in product(ops, repeat=len(inputs) - 1)
    ):
        return target

    return 0
```

So our part 2 answer is:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return sum(process_line(line, include_concat=True) for line in self.input)
```

But now we get to our performance problem. This solution takes more than 20 seconds to run, which is unacceptable. We could refactor the whole thing, (there are definitely some tricks!) but we've already solved it and reworking the whole thing feels like a marginal benefit at best.

At the beginning, I mentioned how each line is totally independent and can be handled individually. Problems like that are a great candidates for parallel computation, where the CPU puts work onto each of its cores. By default, Python only uses a single core, which means every line is waiting on the one before it. If we could work on multiple lines at once, we'd finish in a fraction of the time.

Luckily, Python ships with the `multiprocessing` module, which is meant to solve exact.ly this problem. It abstracts the work of creating and managing a thread pool. It gives `pool.map` and all it asks for in return is a function to call on every item of an iterable.

One problem though- the `map` function expects a callable and we need to pass it a function with some arguments pre-applied. What's a programmer to do!

Why, it's `functools.partial` to the rescue ([docs](https://docs.python.org/3/library/functools.html#functools.partial))! It takes a function and returns a new function which calls the original with some arguments pre-supplied. For instance:

```py
from functools import partial

def add(a, b):
    return a + b

add_two = partial(add, b=2)
add_two(3) # => 5
```

We can do the same thing to pre-bind `include_concat` to our `process_line` function. And like that, we're in business:

```py
from multiprocessing import Pool

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        # I paid for a whole CPU amd I'm gonna use all of it!
        with Pool() as pool:
            return sum(
                pool.map(
                    partial(process_line, include_concat=True),
                    self.input,
                )
            )
```

Adding the same `Pool()` context manager to part 1 gives me a total runtime of ~3.8s for both parts, which is close enough for me.
