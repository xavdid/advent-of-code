---
year: 2024
day: 9
slug: "2024/day/9"
title: "Disk Fragmenter"
# concepts: []
pub_date: "2024-12-12"
---

## Part 1

I've been thinking that the puzzles have felt fresher this year and day 9 reinforces that. This is a fun problem with a novel shape and I enjoyed working on it!

While it might be tempting to use a `list` here, I found it simpler to use a `dict[int, int]`. Each data structure lets us read and write to an `int` index, but dicts simplify bounds and presence checking with the `in` operator. Plus, we don't have to worry about initializing a `list` to the correct length; `dict` index access is unbounded!

We're given a list of ints which represent the sizes of alternating files and gaps. As we iterate, we also have to track the number of files we've seen. As we read files, we write that file's ID to a memory location, skipping forward by the gap size after each file.

There are a lot of ways to approach this, but I feel lke I've found an especially elegant one. We know there's always a file followed by a gap. We could track whether our index is even/odd and know that files are only at even indexes, but that's a lot of manual management. Instead, we can iterate through the input string as a series of pairs using `itertools.batched`:

```py
from itertools import batched

list(batched('ABCDEFG', 2))
# => [('A', 'B'), ('C', 'D'), ('E', 'F'), ('G',)]
```

If we batch a list of `int`s, each of our iterations will have both the `file_size` and `gap_size` parsed out for us! The only other thing we need is a running count of the number of files we've seen. If we were iterating over characters in the input, we'd have to calculate that ourselves (since it would only be half of our current index). But, by wrapping `batch` in an `enumerate` call, it'll count our files for us:

```py
from itertools import batched

class Solution(TextSolution):
    def part_1(self) -> int:
        assert len(self.input) % 2 == 1
        for file_id, (file_size, gap_size) in enumerate(
            batched([int(c) for c in self.input + "0"], 2)
        ):
            ...
```

Note that because we're destructuring the batch, it's important the length of the input be even. As it happens, both the test and real input have odd lengths, so I `assert`ed that assumption before adding a `0`-pad at the end of the input (which should be a no-op).

Then, for each of those batches, we can write the file id to the correct number of locations (our `file_size`) before jumping our pointer forward by `gap_size`:

```py ins={5,6,12-15}
...

class Solution(TextSolution):
    def part_1(self) -> int:
        disk: dict[int, int] = {}
        max_write_location = 0
        ...

        for file_id, (file_size, gap_size) in enumerate(
            batched([int(c) for c in self.input + "0"], 2)
        ):
            for pointer in range(max_write_location, max_write_location + file_size):
                disk[pointer] = file_id

            max_write_location += file_size + gap_size
```

Which works wonderfully for our test input:

```py
{0: 0, 1: 0, 5: 1, 6: 1, 7: 1, 11: 2, 15: 3, 16: 3, 17: 3, 19: 4,
 20: 4, 22: 5, 23: 5, 24: 5, 25: 5, 27: 6, 28: 6, 29: 6, 30: 6,
 32: 7, 33: 7, 34: 7, 36: 8, 37: 8, 38: 8, 39: 8, 40: 9, 41: 9}
```

The gaps in the filesystem are also gaps in our `dict`, which will come in handy shortly.

Next, we'll do our swaps. We'll start with 2 memory pointers that will walk towards each other in a loop. One will always point to the lowest gap and the other will point to the highest filled item, then swap:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...

        writer = 0
        reader = max_write_location # wherever we left off before

        while True:
            while writer in disk:
                writer += 1

            while reader not in disk:
                reader -= 1

            if writer >= reader:
                break

            disk[writer] = disk[reader]
            del disk[reader]
```

Once our writer is bigger than the reader (i.e. the pointers have swapped sides from their starting positions), then we're done!

All that remains is to multiply all our indexes. We know our highest index (`max_write_location`), so we can iterate up to there and sum all our multiples:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...

        return sum(
            idx * disk.get(j, 0) for idx, j in enumerate(range(max_write_location))
        )
```

## Part 2

While moving whole files sounds easier than splitting them up, it means we have a lot more to keep track of. Rather than moving a single bit at a time, we have to track the whole file (and the size of the gap). Let's make a little class for it:

```py
from dataclasses import dataclass
from typing import Literal

@dataclass
class Item:
    type: Literal["file", "gap"]
    size: int
    id_: int = 0
```

Files and gaps are basically the same, except the latter has an id based on its position in the initial list. Now our `disk` parsing looks different:

```py rem={4,6,7,12-14} ins={5,8,15-16}
...

class Solution(TextSolution):
    def part_1(self) -> int:
    def part_2(self) -> int:
        disk: dict[int, int] = {}
        max_write_location = 0
        disk: list[Item] = []
        for file_id, (file_size, gap_size) in enumerate(
            batched(parse_ints(self.input + "0"), 2)
        ):
            for pointer in range(max_write_location, max_write_location + file_size):
                disk[pointer] = file_id
            max_write_location += file_size + gap_size
            disk.append(Item("file", id_=file_id, size=file_size))
            disk.append(Item("gap", gap_size))
```

Past that, our approach is _largely_ the same. In part 2, we try to move each file exactly once (in descending order). So instead of just looping, we need to find each file, in order. Luckily, our `reader` pointer from before will still generally work:

```py
...

class Solution(TextSolution):
    def part_2(self) -> int:
        ...

        # the last item is the padded gap, so the 2nd to last item's id is the highest
        reader = len(disk) - 1
        for file_id in range(disk[-2].id_, -1, -1):
            while (f := disk[reader]).type != "file" or f.id_ != file_id:
                reader -= 1
```

We're counting down our file ids and, starting at the end, we walk backwards until we've found our file in the list.

Next, we have to find the leftmost gap. We could manage a `writer` ourselves, but Python's generators are pretty fast for this sort of thing and they support conditionals. So, we iterate over our disk looking for the first gap that would fit the file `f` that we just found:

```py
...

class Solution(TextSolution):
    def part_2(self) -> int:
        ...

        for file_id in range(disk[-2].id_, -1, -1):
            ...

            try:
                writer, g = next(
                    (writer, g)
                    for writer, g in enumerate(disk)
                    if g.type == "gap" and g.size >= f.size
                )
            except StopIteration:
                continue

            if writer > reader:
                continue
```

If `next` never finds anything, it throws `StopIteration`. That means no gap in the list will fit this file, so we `continue` to the next `file_id`. Similarly, if we'd move a file to the right instead of the left, that's not valid and we skip.

> You might wonder why I didn't include the `and writer < reader` check in my iterable and checked it afterwards instead. It turns out that including it inline adds ~ 2 seconds to my total solve time! It's probably something related to having to look up `reader` from outside the loop scope over and over, but that's a total guess.

Once we've got valid swap locations, we can insert the file just before `writer` and decrease the size of the gap by the file's size. We also need to add a gap where the file was:

```py
...

class Solution(TextSolution):
    def part_2(self) -> int:
        ...

        for file_id in range(disk[-2].id_, -1, -1):
            ...

            disk[reader] = Item("gap", f.size)

            disk.insert(writer, f)
            g.size -= f.size
```

Once we've tried to move every file, we can calculate the checksum again. The tricky thing now is that each item has width, so we have to flatten out _all_ the items to get our answer.

At first I tried to put digits back into a string, but because file ids are multiple-digits long, my indexes (and my answer) were all off. Instead, we can run them through an expansion function before enumerating over that:

```py
from itertools import batched, chain
...

def expand(i: Item) -> list[int]:
    return [i.id_] * i.size

class Solution(TextSolution):
    def part_2(self) -> int:
        ...

        return sum(
            idx * i for idx, i in enumerate(chain.from_iterable(map(expand, disk)))
        )
```

`chain.from_iterable` comes in handy for turning a list of lists (some of which are empty) into a single iterable. For example, this is the output for the example:

```py
[[0, 0], [9, 9], [2], [], [1, 1, 1], [7, 7, 7], [], [0], [4, 4], [0], 3, 3, 3],
[0], [0, 0], [0], [5, 5, 5, 5], [0], [6, 6, 6, 6], [0], [0, 0, 0], [0], [8, 8, 8, 8],
[], [0, 0], []]
```

gets chained into:

```py
[0, 0, 9, 9, 2, 1, 1, 1, 7, 7, 7, 0, 4, 4, 0, 3, 3, 3, 0, 0, 0, 0,
5, 5, 5, 5, 0, 6, 6, 6, 6, 0, 0, 0, 0, 0, 8, 8, 8, 8, 0, 0]
```

which is the exact format we need!
