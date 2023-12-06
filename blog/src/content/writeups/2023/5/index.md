---
year: 2023
day: 5
title: "If You Give A Seed A Fertilizer"
slug: 2023/day/5
pub_date: "2023-12-05"
---

## Part 1

Our input is in two sections, so we'll need to handle them individually. The seeds themselves are simple, but the actual transformation layers are a little more involved. Each one is a range of numbers (aka a "mask") and a shift, so let's store them that way:

```py
Transformation = tuple[range, int]

def parse_range(line: str) -> Transformation:
    dest_start, source_start, size = map(int, line.split())

    return range(source_start, source_start + size), dest_start - source_start


def parse_map(map_block: str) -> list[Transformation]:
    return sorted(
        [parse_range(l) for l in map_block.split("\n")[1:]], key=lambda r: r[0].start
    )
```

`50 98 2` becomes `(range(98, 100), -48)`, which is much more useful. Any number in that range will be added to the offset (`2`).

In our main method, we can put the parsing together:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        blocks = self.input.split("\n\n")
        # start parsing after `seeds:`
        seeds = [int(s) for s in blocks[0][6:].split()]

        map_layers = [parse_map(b) for b in blocks[1:]]
```

`map_layers` is a `list[list[Transformation]]`. Each list is all the instructions for each map (e.g. the first element is `[[(range(50, 98), 2), (range(98, 100), -48)]`).

Next, we need a way to apply a mask to a number given a list of potential transformations. Python's `range` class make short work of this because `in` works like you'd expect:

```py
def mask_number(num: int, transformations: list[Transformation]) -> int:
    for mask, offset in transformations:
        if num in mask:
            return num + offset
    return num
```

That lets us send each seed through all the map layers:

```py ins={10-15}
...

class Solution(TextSolution):
    def part_1(self) -> int:
        blocks = self.input.split("\n\n")
        seeds = [int(s) for s in blocks[0][6:].split()]

        map_layers = [parse_map(b) for b in blocks[1:]]

        result = []
        for seed in seeds:
            for transformations in map_layers:
                seed = mask_number(seed, transformations)

            result.append(seed)

        return min(result)
```

We transform and update each seed for each transition until we've done them all. The smallest of those is our answer!

## Part 2

In classic AoC fashion, we write the approach in part 1 only for part 2 to ask us to do the same thing, but _way_ too big. As soon as I saw how big this ranges were, I knew that was the case again.

Rather than trying to run each number through all 7 maps, we can instead act on entire _ranges_. For example, let's say we're looking at the numbers `[79, 80, ..., 91, 92]` and we're going to apply `(range(50, 85), 200)`. Instead of iterating over the entire range, we know that all numbers outside that range can be ignored. So the entire operation can be simplified to `[range(279, 285), range(85, 92)]`, where the overlapping portion of the range was shifted while the non-overlapping portion is left as-is. This required no iteration at all, which fixes our performance issues!

Now, actually implementing this cooked my noodle. I do not promise this is the best or cleanest way to do it, but it _does work_ (~ instantly), so there something to be said for that.

The core challenge for me was writing a function that does the actual cutting. Given a list of input `range`s and a bunch of transforms, we need a new list of ranges with all of the parts that overlap with a transform, transformed. So.

First things first, we need some helper functions to know if two ranges overlap and to shift a range by an offset. That's pretty straightforward:

```py
def do_ranges_overlap(a: range, b: range) -> bool:
    return a.start < b.stop and b.start < a.stop

def shift_range(r: range, offset: int) -> range:
    return range(r.start + offset, r.stop + offset)
```

And now for the big one! Given a `range` and a list of transforms, return a new list of ranges where the appropriate section(s) have been shifted. We'll do that by applying each mask in order, if possible. It's also important (for this approach) that **all ranges are sorted**. When we make cuts to the base range, we'll be assuming that anything lower than our current range doesn't need to be masked if it hasn't been already.

Broadly, there are 5 cases to cover:

1. No overlap:

```
base:    12345
mask:         6789
result:  12345
```

2. Mask whole range:

```
base:      345
mask:    1234567
result:    MMM
```

3. Mask center portion of range:

```
base:    1234567
mask:      345
result:  12MMM??
```

4. Mask left:

```
base:      34567
mask:    12345
result:    MMM??
```

5. Mask right:

```
base:    12345
mask:      34567
result:  12MMM
```

The question marks above are why the sorted transforms are so important. In cases `3` and `4`, we know that everything before the current mask is settled, but a subsequent mask could still apply. So we can't know what the rest of result will look like yet. We'll have to recurse a little.

Let's see what this code looks like:

```py
def apply_transformations(base: range, transforms: list[Transformation]) -> list[range]:
    for mask, offset in transforms:
        # 1 - no overlap; skip this mask
        if not do_ranges_overlap(base, mask):
            continue

        # 2 - base is inside mask, shift entire base
        if mask.start <= base.start and base.stop <= mask.stop:
            return [shift_range(base, offset)]

        # 3 - mask is a subset of base
        # return unshifted left, shifted middle, and recurse for the rest
        if base.start <= mask.start and mask.stop <= base.stop:
            return [
                range(base.start, mask.start),
                shift_range(mask, offset),
                *apply_transformations(range(mask.stop, base.stop), transforms),
            ]

        # 4 - mask overlaps only the left side,
        # return masked left, recurse for the rest
        if mask.start <= base.start and mask.stop <= base.stop:
            return [
                shift_range(range(base.start, mask.stop), offset),
                *apply_transformations(range(mask.stop, base.stop), transforms),
            ]

        # 5 - mask overlaps only the right side
        # return unshifted left, masked right
        if base.start <= mask.start and base.stop <= mask.stop:
            return [
                range(base.start, mask.start),
                shift_range(range(mask.start, base.stop), offset),
            ]

    # no masks overlapped this base; pass it through
    return [base]
```

Only a couple of cases (the ones with `?` in the diagram above) worry about recursion. Otherwise, we're carefully checking bounds and masking portions of the `base`.

Finally, we can put it all together (highlighting differences from part 1):

```py ins={1,10-11,18,20-25}
from itertools import batched, chain
...

class Solution(TextSolution):
    ...

    def part_2(self) -> int:
        blocks = self.input.split("\n\n")
        seeds = [
            range(start, start + size)
            for start, size in batched(map(int, blocks[0][6:].split()), 2)
        ]

        transformations = [parse_map(b) for b in blocks[1:]]

        result = []
        for seed_range in seeds:
            ranges = [seed_range]

            for block in transformations:
                ranges = list(
                    chain.from_iterable(apply_transformations(r, block) for r in ranges)
                )

            result.append(sorted(ranges, key=lambda r: r.start)[0].start)

        return min(result)
```

We start with a 1-length list of seed ranges and keep them grouped by their cohort at each layer. We use `iterools.chain.from_iterable` to keep our nested results flat. Once we've done all the transformations on a seed group, we sort the resulting ranges, meaning the `start` of the first one must be the lowest result. Doing that for each `seed_range` gives us the lowest result from each group, at which time a simple `min` will round us out.

As a bonus, we got to use `itertools.batched`, [my absolute favorite](https://mastodon.social/@xavdid/111167364447761991) Python 3.12 feature!
