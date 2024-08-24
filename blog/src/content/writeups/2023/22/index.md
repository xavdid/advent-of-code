---
year: 2023
day: 22
slug: 2023/day/22
title: "Sand Slabs"
# concepts: [design]
pub_date: "2024-08-24"
---

## Part 1

While I'd usually start by writing our `Brick` class, I'm going to mix it up today. There's some interesting discussion to be had while writing that implementation, so I'm going to save it for after we know how we'll use the class.

In the meantime, I'll give you an abstract version of `Brick` and we'll fill it in later. There are only a few methods:

```py
from dataclasses import dataclass

@dataclass
class Brick:
    @staticmethod
    def parse(id_: int, s: str) -> "Brick":
        ...

    def intersects(self, other: "Brick | set") -> bool:
        ...

    def fall(self) -> "Brick":
        ...
```

Now for the actual problem. First, input parsing:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        bricks = [Brick.parse(idx, l) for idx, l in enumerate(self.input)]
```

Gosh, writing code is so easy when you get to skip them implementation! So convenient.

So, how do we drop bricks? The simple approach is to take each brick and decrement its `z` value until it equals `1` or tries to overlap with any other brick. That almost works, but if you drop a high brick onto a lower brick that hasn't fallen yet, the higher brick will stop before it's supposed to.

Instead, it's important that each brick can only come to rest on bricks that have already settled. This invites another issue: which bricks can we safely move? How do I untangle this tower to find "free" bricks?

At this point, I did a lot of finger gymnastics to understand the problem. This lead to a few conclusions about the input:

1. Bricks are made of individual cubes in 3D space.
2. We can represent each cube as a 3-tuple of its location (`(x, y, z)`).
3. A collision only happens if two bricks try to contain the same cube.
4. Bricks only ever move down, so the only thing that will change the cubes in our parsed bricks is their `z` value.
5. Because we know the input is valid (and no bricks are currently intersecting), we know that bricks that share a `z` value can _never_ collide.

That means if we sort our bricks before we drop them, we can safely send them all the way to the ground:

```py ins={4-6,11} rem={10}
class Brick:
    ...

    # all we need to be sortable
    def __lt__(self, other: "Brick") -> bool:
        ...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        bricks = [Brick.parse(idx, l) for idx, l in enumerate(self.input)]
        bricks = sorted(Brick.parse(idx, l) for idx, l in enumerate(self.input))
```

Now we can start dropping them! We need to track both the final position of each brick and the set of all settled cubes.

For each brick, if it's not already on the floor and if its fallen version doesn't intersect with the settled cubes update its position and loop. Once it rests, store the brick and its points. We can do this with a fairly terse `while` and the walrus operator:

```py
type Cube = tuple[int, int, int]

class Brick:
    ...

    @property
    def on_ground(self) -> int:
        ...

    @property
    def cubes(self) -> set[Cubes]:
        ...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        settled_bricks: list[Brick] = []
        settled_cubes: set[Cube] = set()

        for b in bricks:
            cur_pos = b
            while not (
                cur_pos.on_ground
                or (next_pos := cur_pos.fall()).intersects(settled_cubes)
            ):
                cur_pos = next_pos

            settled_bricks.append(cur_pos)
            settled_cubes |= cur_pos.cubes
```

With that taken care of, now we have to find our load bearing bricks. There may be a fancier way to do this, but I went simple: for each settled brick, drop it once more and see which bricks it intersects now. This is an O(n^2) operation, but `set` comparisons are quite fast, so it's not bad:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        supported_by: dict[int, set[int]] = {}
        for settled_brick in settled_bricks:
            if settled_brick.on_ground:
                continue

            below = settled_brick.fall()
            supported_by[settled_brick.id_] = {
                other.id_
                for other in settled_bricks
                if settled_brick.id_ != other.id_ and below.intersects(other)
            }
```

For the sample input (using numbers instead of letters), we get:

```py
{
   1: {0},
   2: {0},
   3: {1, 2},
   4: {1, 2},
   5: {3, 4},
   6: {5},
}
```

Lastly, we want to count all the bricks which are load bearing. Those are the ids appear alone in any of the dict values above. In the example, bricks `0` and `5` are both load bearing. But, we have to take care not to double-count `0`, so we'll use sets again. Here's a neat Python trick for getting the union of a bunch of sets at once:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        num_load_bearing = len(
            set().union(*(s for s in supported_by.values() if len(s) == 1))
        )
```

We're getting an iterable of every 1-element set and passing the whole thing as a bunch of positional args to the `union()` method on an empty set. If we wrote out the example by hand, it would be:

```py
set().union({0}, {0}, {5})
# => {0, 5}

# equivalent to:
set() | {0} | {0} | {5}
```

With a count of unique load-bearing bricks computed, we can subtract it from the count of all of our bricks for the answer:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        return len(self.input) - num_load_bearing
```

### Implementing the Abstract

If you've been playing along at home, you'll notice that none of the code I've written up to this point actually _runs_. We're still missing the inside of our `Brick`. Let's fix that!

I saved this for last because my `Brick` implementation went through a few versions ([this whole solution did](https://github.com/xavdid/advent-of-code/blob/d7a3102/solutions/2023/day_22/solution.py), to be honest) and I thought it would be interesting talk through them separately. I've been writing [a lot of rust](https://exercism.org/profiles/xavdid/solutions?track_slug=rust) this year (see [my blog post](https://xavd.id/blog/post/12-languages-in-12-months/#wrapping-it-up) for why) and it's definitely affected how I write Python.

There are a lot of ways [to write Python like it's Rust](https://kobzol.github.io/rust/python/2023/05/20/writing-python-like-its-rust.html), but the patterns that speak to me the most are:

1. static builder functions
2. immutable data structures that return new versions of themselves instead of modifying any local state
3. front-loading complexity (during building, not during usage)

With those goals in mind, let's look at both versions of my `Brick` class- one that follows the first 2 guidelines and another that follows all 3. Here's our starting point:

```py
...

@dataclass
class Brick:
    @staticmethod
    def parse(id_: int, s: str) -> "Brick":
        ...

    @property
    def cubes(self) -> set[Cubes]:
        ...

    def intersects(self, other: "Brick | set") -> bool:
        ...

    def fall(self) -> "Brick":
        ...

    @property
    def on_ground(self) -> int:
        ...

    def __lt__(self, other: "Brick") -> bool:
        ...
```

> Note: Despite designing for immutable data structures, I ended up using unfrozen `@dataclass`es (and not mutating them). Frozen ones (and `NamedTuple`s) each incur [a small time penalty](https://docs.python.org/3.12/library/dataclasses.html#frozen-instances) and I didn't need hashability. Plus, using them reaised my final runtime from `0.76s` to `0.80s`. Every (milli)second counts!

First is parsing via a builder function (pattern 1). Each brick comes to us as a pair of start and end positions. For each dimension (`x`,`y`,`z`) we'll store either an `int` or a `range` based on whether start and end match or not:

```py
...

@dataclass
class Brick:
    id_: int
    x: int | range
    y: int | range
    z: int | range

    @staticmethod
    def parse(id_: int, s: str) -> "Brick":
        start, end = [ss.split(",") for ss in s.split("~")]
        dims: dict[str, int | range] = {}

        for dim, l, r in zip("xyz", start, end):
            if l == r:
                dims[dim] = int(l)
            else:
                assert int(l) < int(r)
                dims[dim] = range(int(l), int(r) + 1) # +1 because input range is inclusive

        return Brick(id_, **dims)
```

Our `.cubes` method produces the set of cubes that comprise our brick. It can handle any configuration of ints and ranges thanks to pattern matching:

```py
from functools import cached_property
...

@dataclass
class Brick:
    ...

    @cached_property
    def cubes(self) -> set[Cube]:
        match self.x, self.y, self.z:
            case int(x), int(y), int(z):
                return {(x, y, z)}
            case range() as r, int(y), int(z):
                return {(x, y, z) for x in r}
            case int(x), range() as r, int(z):
                return {(x, y, z) for y in r}
            case int(x), int(y), range() as r:
                return {(x, y, z) for z in r}
            case _:
                raise RuntimeError(f"invalid shape: {self}")

    def intersects(self, other: "Brick") -> bool:
        return bool(self.cubes & other.cubes)
```

Each branch is basically the same, but which dimension the range represents changes. We also cache for performance reasons, since there's no reason to iterate twice. Our `intersects` method is simple, providing some nice ergonomics to brick comparisons. We could have defined `__and__`, but I didn't find `below & other` as readable.

Last up is falling down. Following pattern 2, we'll return new objects based on old ones rather than modify any state. As I said before, the only thing changes is the `z` value. There are only three possible outcomes, so the code is straightforward:

```py
...

@dataclass
class Brick:
    ...

    @cached_property
    def lowest_z(self) -> int:
        if isinstance(self.z, range):
            return self.z.start
        return self.z

    @property
    def on_ground(self) -> bool:
        return self.lowest_z == 1

    def fall(self) -> "Brick":
        # refuse to fall if on ground already
        if self.on_ground:
            return self

        if isinstance(self.z, range):
            return Brick(
                self.id_,
                self.x,
                self.y,
                range(self.z.start - 1, self.z.stop - 1),
            )

        return Brick(self.id_, self.x, self.y, self.z - 1)
```

The `on_ground` helper isn't _really_ necessary, but I messed up that check in enough places (foolishly assuming the ground is at `0`, not `1`) that I thought it was worthwhile. `lowest_z` simplifies our other lowest-point checks, which is nice. It's also all we need to make bricks sortable (because we don't care about their absolute ordering as long as they're sorted by `lowest_z`):

```py
@dataclass
class Brick:
    ...

    def __lt__(self, other: "Brick") -> bool:
        return self.lowest_z < other.lowest_z
```

Now, that's a perfectly reasonable place to stop. Our code produces the correct answer, runs in just over 1 second, and doesn't have any glaring issues. But, you'll notice I haven't mentioned the third pattern (front-loading complexity) yet. Let's fix that.

### Cleaner, Better, Faster, Stronger

While the code works, it was a little frustrating having every method have to work around `z` being `int | range`. A rust-y alternative would be an [Algebraic Data Type](https://en.wikipedia.org/wiki/Algebraic_data_type) that separates the two cases out. I could have an `IntBrick` and a `RangeBrick` that implement the same interface (so the main code doesn't care what it's working with). Each version of the `fall` method would be simpler, only having a single case to worry about. But, that still means I'm writing every method twice. It would be more maintainable that what I have (I guess) but isn't the reduction in complexity I was looking for.

Then it hit me - why have two versions of a brick at all? A brick is always a group of cubes, so why not just store cubes instead of bounds and pre-compute anything else we need? The whole design is meant to act immutable, so those pre-computations won't go stale.

Storing cubes directly means `parse` gets a little more complicated (there's that up-front complexity I mentioned!) but everything else gets _much_ simpler. First, our dataclass properties change:

```py ins={7-8} rem={4-6}
@dataclass
class Brick:
    id_: int
    x: int | range
    y: int | range
    z: int | range
    cubes: set[Cube]
    lowest_z: int
```

Next, parsing. Our `match` statement from `.cubes` moved here, as did our `lowest_z` check:

```py ins={18-20,22-34,37} rem={10-17,36}
...

@dataclass
class Brick:
    ...

    @staticmethod
    def parse(id_: int, s: str) -> "Brick":
        start, end = [ss.split(",") for ss in s.split("~")]
        dims: dict[str, int | range] = {}

        for dim, l, r in zip("xyz", start, end):
            if l == r:
                dims[dim] = int(l)
            else:
                assert int(l) < int(r)
                dims[dim] = range(int(l), int(r) + 1) # +1 because input range is inclusive
        dims = [
            int(l) if l == r else range(int(l), int(r) + 1) for l, r in zip(start, end)
        ]

        match dims:
            case int(x), int(y), range() as r:
                cubes = {(x, y, z) for z in r}
            case int(x), range() as r, int(z):
                cubes = {(x, y, z) for y in r}
            case range() as r, int(y), int(z):
                cubes = {(x, y, z) for x in r}
            case int(x), int(y), int(z):
                cubes = {(x, y, z)}
            case _:
                raise ValueError(f"invalid shape: {s}")

        lowest_z = dims[2] if isinstance(dims[2], int) else dims[2].start

        return Brick(id_, **dims)
        return Brick(id_, cubes, lowest_z)
```

I did some light refactoring on the `dims` calculation (since I knew I didn't need the `assert` or dimension name anymore), but everything else should look pretty familiar. We also do validation checks up front rather than during use. It doesn't really matter here, but this means that every `Brick` instance will be valid (rather than `.cubes` maybe throwing validation errors, which would be surprising and bad).

Like I said it would, `parse` has more going on. But look how it's simplified our business logic:

```py ins={31-35} rem={7-11,13-15,22-30}
...

@dataclass
class Brick:
    ...

    @cached_property
    def lowest_z(self) -> int:
        if isinstance(self.z, range):
            return self.z.start
        return self.z

    @cached_property
    def cubes(self) -> set[Cube]:
        ...

    def fall(self) -> "Brick":
        # refuse to fall if on ground already
        if self.on_ground:
            return self

        if isinstance(self.z, range):
            return Brick(
                self.id_,
                self.x,
                self.y,
                range(self.z.start - 1, self.z.stop - 1),
            )

        return Brick(self.id_, self.x, self.y, self.z - 1)
        return Brick(
            self.id_,
            {(x, y, z - 1) for x, y, z in self.cubes},
            self.lowest_z - 1,
        )
```

Falling is a single, easy-to-understand operation and adding future methods to this class would be much simpler.

Anyway, that should do it for today. Thanks for coming on that design journey with m...

Oh right, there's still half a puzzle to solve!

## Part 2

At first I thought this would be a dynamic programming problem where the number of bricks that fall when pulling `0` are equal to the sum of number of bricks that fall when you pull the al bricks it supports (`1` and `2` and so on).

I thought I was clever for realizing you have to do that calculation with the [power set](https://en.wikipedia.org/wiki/Power_set) of bricks to drop (e.g. `0` causes anything held by `1`, `2`, or `1, 2` to drop). Unfortunately, my answer was too low.

Though my approach worked swimmingly for the example input, I drew the wrong conclusions from it. Imagine the following `brick: {supported_by}` structure:

```py
{
   1: {0},
   2: {0},
   3: {1, 2},
   4: {0, 1, 2},
}
```

My approach would still drop `1` and `2` (and then `3`) for brick `0`, but it would fail to drop `4` because it's not exclusively held up by things supported by `0`. While I don't think that basic example is physically possible, our real puzzle inputs _do_ have that situation buried in them.

Rather than recurse up a tree structure, we want to drop any bricks who are supported by _any_ of the already dropped bricks. Luckily, everything is already stored in `set`s!

> Note: not pictured is me transforming and re-transforming these structures way too many times; it wasn't quite this smooth

So, we'll iterate through every brick. For each one, we build the set of all removed bricks (which starts with only the brick we're focused on). Then, we can find all the bricks that are supported exclusively by that initial set. We can add those would-fall bricks to our set of things being removed before looping to find everything this now-larger set supports. We'll stop if a pass of the `supported_by` values doesn't grow the set at all.

That code ends up being pretty straightforward when we're all said and done:

```py ins={5} rem={4}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        ...

        # all we need for part 2:
        chain_reaction_total = 0
        for settled_brick in range(num_bricks):
            removed = {settled_brick}

            while True:
                would_fall = {k for k, v in supported_by.items() if v <= removed}
                # sub 1 to account for the staring brick which won't be in `would_fall`
                if len(would_fall) == len(removed) - 1:
                    chain_reaction_total += len(would_fall)
                    break

                # find bricks that are supported by _anything_ we've pulled on next loop
                removed |= would_fall
```

And _that_ should do it! Not so bad once we caught those tricky edge cases. Thanks for bearing with me on this one.
