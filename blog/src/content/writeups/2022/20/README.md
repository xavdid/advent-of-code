---
year: 2022
day: 20
title: "Grove Positioning System"
slug: "2022/day/20"
pub_date: "2023-01-29"
---

## Part 1

Before diving in in earnest, I wanted to confirm a couple of properties about my input to help inform my solution. A quick loop revealed that:

1. List items are **not** unique.
2. The value `0` only shows up once

With that, we know that:

1. We have to track items with something other than their int value (because we won't be able to differentiate between a pair of 5's otherwise)
2. `0` is important because it informs our answer, but we don't have to do anything special for it other than find it

Also, our list being circular should tip us off to the fact that we'll either be using the modulo operator (`%`) _a lot_ or we should use a data structure that allows us to easily "rotate" the items. Luckily, Python has exactly that: `collections.deque` (pronounced "deck", the word stands for "double-ended queue"). It's got a `.rotate` method, plus it's fast to add/pop from either end of the list.

Before we can enqueue them, we'll need a way to store list items. We'll use a `namedtuple`:

```py
from typing import NamedTuple

class Item(NamedTuple):
    id: int
    value: int
```

We could also use a `dataclass`, but given that we're not adding any methods, it's overkill. Also, when I tried each out, the tuple-based approach was 8x faster.[^1]

Anyway, now we can parse our input:

```py
from collections import deque
...

class Solution(IntSplitSolution):
    def part_1(self) -> int:
        items: list[Item] = [
            Item(idx, value) for idx, value in enumerate(self.input)
        ]
        d = deque(items)
```

Separating the original `Item`s and the `deque` will allow us to iterate over the starting items correctly without worrying about the state of our `deque`.

Next, we need to be able to move items through our list. We could delete and insert at a given index (using a standard `list`) but popping and rotating made a lot more sense to me. To do that, we:

1. rotate until the item we're moving is first
2. pop the item off the front
3. rotate the list based on its value
4. append it to the left

Here's how that looks:

```py
...

class Solution(IntSplitSolution):
    def part_1(self) -> int:
        ...

        for item in items:
            d.rotate(-d.index(item)) # 1
            assert d[0] == item

            d.popleft() # 2
            d.rotate(-item.value) # 3
            d.appendleft(i) # 4
```

Note that we rotate by `-item.value`, because positive arguments to `.rotate` move towards the right and we want our positive rotations to move the rest of the list left (towards the front).

Finally, we need to find the item with value `0`, put it at the front of the list, and do our index lookups. We'll find it during iteration and use it at the end of the loop:

```py
from typing import Optional

...

class Solution(IntSplitSolution):
    def part_1(self) -> int:
        ...
        zero: Optional[Item] = None

        for item in items:
            if item.value == 0:
                zero = item
            ...

        assert zero
        d.rotate(-d.index(zero))

        num_items = len(self.input)
        return sum(d[c * 1000 % num_items].value for c in [1, 2, 3])
```

Boom! Didn't even need to mod the list size to save on rotations, though I have a feeling we will shortly...

## Part 2

And... there we go.

There are two main changes to make. First, we have to account for the multiplier when parsing input. Secondly, we (for performance reasons) need to simplify the size of the rotation. Plus, we wrap it all in a method our actual solution functions can call:

```py
...

class Solution(IntSplitSolution):
    def _solve(self, multiplier: int, num_mixes: int):
        items = [Item(idx, value * multiplier) for idx, value in enumerate(self.input)]

        ...

        for _ in range(num_mixes):
            for item in items:
                ...

                d.popleft() # step 2 from before

                rotation = item.value % (num_items - 1)

                d.rotate(-rotation) # step 3 before

                ...
```

Not so bad, right? Because rotating a list of 5k items (our input size) by 5000 leads to no change, we only really need to rotate the list by the remainder. Hence, our use of modulo.

The trickiest thing was that we had to mod not by the length of the full list, but by the size of the current list - which we have just popped an item from. That one took me a bit to fix. Otherwise, it was smooth sailing here on this day 20.

[^1]: I suspect because our code is doing a lot of lookups, and `tuple`s are fast for those sort of operations (as compared to `dict`s, which is what backs the `dataclass`)
