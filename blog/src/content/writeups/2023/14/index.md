---
year: 2023
day: 14
slug: 2023/day/14
title: "Parabolic Reflector Dish"
pub_date: "2023-12-17"
---

## Part 1

For this first part, we'll need the `parse_grid` function I described in [Day 10](/writeups/2023/day/10/) (and improved on [day 11](/writeups/2023/day/10/)), so refer back to those if needed. That work makes short work of parsing our rocks and walls:

Next, we need to roll the rocks up. There might be a clever way to do this, but I sort of like the "by the book" solutions, at least to start. So let's do it! For each rock, we need to walk up each row in its column until we hit something (wall, rock, grid edge, etc). The big ck here is that we have to move the topmost rocks first so they correctly block rocks farther down. That's nothing a little sorting can't fix:

```py
# import my parse_grid func

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        rocks = set(parse_grid(self.input, ignore_chars=".#"))
        walls = set(parse_grid(self.input, ignore_chars=".O"))

        for row, col in sorted(rocks):
            ...
            # TODO

        grid_height = len(self.input)
        return sum(grid_height - row for row, _ in rocks)
```

Because we're separating our rocks and walls, we don't care about the dict keys. To save us calling `.keys()` repeatedly, I put all the points into a `set`- being able to check membership quickly is all we need, so we can ignore the values. We're also doing the sorting I mentioned before- it's important that we do each column top-to-bottom. The `(row, column)` order already does this for us. We could also group columns together, but that doesn't actually matter as long as long as each column is ordered.

From there, we ~~walk~~ roll up. We start immediately above our position and walk off the top of the grid (using `range`'s `step` arg to count down instead of up). If we could move to the spot, we store as the last successful move. We do that until we `break` out of the loop, at which time we move if we found any successful destinations:

```py ins={6,8-12,14-16}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for row, col in sorted(rocks):
            new_row = None

            for potential_new_row in range(row - 1, -1, -1):
                potential_new_spot = potential_new_row, col
                if potential_new_spot in walls or potential_new_spot in rocks:
                    break
                new_row = potential_new_row

            if new_row is not None:
                rocks.remove((row, col))
                rocks.add((new_row, col))
        ...
```

I had a couple of off-by-one errors on the range here, but it all works quickly once those were ironed out.

It's not the most elegant code I've ever written, but it works well enough. I usually don't clean part 1 _too_ much since I usually rip it out for p2 anyway. Onward!

## Part 2

Reading this prompt, 2 things jump out at me:

1. rolling rocks different directions will just be minor tweaks on rolling up, but making one (or two) functions to do all 4 might be more trouble than it's worth
2. 1 billion is a lot of cycles; I bet the board gets into a loop

Let's knock those out one at a time.

First, the rolling. Like I said, making this pretty may be tricky. But it doesn't need to be pretty at first! To that end, I wrote 4 functions, one for each direction. `roll_up` is the middle section of our part 1 code. The other directions have small tweaks (highlighted), where they replace the other half of the tuple, sort the `rocks` differently, or tweak the `range` to go a different direction:

```py ins={1,3,4,7,11,14,15,22,25,28}
Points = set[tuple[int,int]]

def roll_down(rocks: Points, walls: Points, grid_size: int) -> None:
    for row, col in sorted(rocks, reverse=True):
        new_row = None

        for potential_new_row in range(row + 1, grid_size):
            ...

def roll_left(rocks: Points, walls: Points) -> None:
    for row, col in sorted(rocks, key=lambda loc: loc[1]):
        new_col = None

        for potential_new_col in range(col - 1, -1, -1):
            potential_new_spot = row, potential_new_col
            if potential_new_spot in walls or potential_new_spot in rocks:
                break
            new_col = potential_new_col

        if new_col is not None:
            rocks.remove((row, col))
            rocks.add((row, new_col))

def roll_right(rocks: Points, walls: Points, grid_size: int) -> None:
    for row, col in sorted(rocks, key=lambda loc: loc[1], reverse=True):
        new_col = None

        for potential_new_col in range(col + 1, grid_size):
            ...
```

I'll be the first to admit there's a lot of repetition here. But, we're still in step 1 of "make it work, make it fast, make it pretty", so there's no rush. The important thing is that they _do_ work for now. A `print_grid` function and manual checks against the examples will verify this:

```py
def print_grid(rocks: Points, walls: Points, size: int) -> None:
    print()
    for row in range(size):
        for col in range(size):
            loc = row, col

            print("O" if loc in rocks else ("#" if loc in walls else "."), end="")
        print()

rocks = set(parse_grid(self.input, ignore_chars=".#"))
walls = set(parse_grid(self.input, ignore_chars=".O"))
grid_size = len(self.input)

for _ in range(3):
    roll_up(rocks, walls)
    roll_left(rocks, walls)
    roll_down(rocks, walls, grid_size)
    roll_right(rocks, walls, grid_size)

    print_grid(rocks, walls, grid_size)
```

Now that we can correctly tumble rocks, it's time to loop:

```py ins={9,11-15}
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        rocks = set(parse_grid(self.input, ignore_chars=".#"))
        walls = set(parse_grid(self.input, ignore_chars=".O"))
        grid_size = len(self.input)

        NUM_CYCLES = 1_000_000_000

        for _ in range(NUM_CYCLES):
            roll_up(rocks, walls)
            roll_left(rocks, walls)
            roll_down(rocks, walls, grid_size)
            roll_right(rocks, walls, grid_size)

        return sum(grid_size - row for row, _ in rocks)
```

While this will _eventually_ work, it'll also run for a super long time. For problems like this, that usually means there's a loop. Let's see if we can find one!

We know we're in a loop if we, at the end of a cycle, have the exact same set of rocks we've seen before. If we track each state (and when we've seen it) we'll be able to determine the length of the loop, an important component in knowing exactly how far to jump. Let's find a loop!

```py ins={7,9,13-50}
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...

        states: dict[frozenset[tuple[int,int]], int] = {}

        for i in range(NUM_CYCLES):
            roll_up(rocks, walls)
            ...

            state = frozenset(rocks)
            if state in states:
                loop_length = i - states[state]
                print(
                    f"loop! {i=} is also {states[state]}, so loop length is {loop_length}"
                )
                print(
                    f"you can fit {NUM_CYCLES // loop_length} full loops in, which puts you at {(NUM_CYCLES // loop_length) * loop_length}"
                )
                break

            states[state] = i
```

Note that we use `frozenset` instead of `set` since only the former is hashable (by virtue of being immutable).

The code no longer finds the answer, but it _will_ confirm that we have a loop, how big it is, and when it starts. Running it on the example, I get:

```
loop! i=9 is also 2, so loop length is 7
you can fit 142857142 full loops in, which puts you at 999999994
```

Loop confirmed! That's important, because otherwise we'd be in trouble. The fact that we have a fixed-length loop means we can bump `i` by a known amount and do the last few cycles (to get to 1mil) manually.

Math wise, this isn't bad. When we find the loop, we need to add a multiple of `loop_length` to `i` so that we're in the exact same spot in the cycle but much closer to our target. The modulo operator (`%`) makes this easy, allowing us to calculate how much farther we need to go after completing all the cycles that will fit in `NUM_CYCLES - i`. Subtract _that_ from `NUM_CYCLES` and our `i` is now ready to finish the sprint to 1 million:

```py ins={7,8,14-17,20}
...

class Solution(StrSplitSolution):
    def part_2(self) -> int:
        ...

        i = 0
        while i < NUM_CYCLES:
            roll_up(rocks, walls)
            ...

            state = frozenset(rocks)

            if state in states and i < 500:
                distance_to_goal = NUM_CYCLES - i
                loop_length = i - states[state]
                i = NUM_CYCLES - distance_to_goal % loop_length

            states[state] = i
            i += 1

        return sum(grid_size - row for row, _ in rocks)
```

We switched from `for .. range` to a `while` loop so we could manage `i` manually. I also put the modulo math in some extra variables for clarity, but you can squish it all down if you'd like.

That'll do it! I'm doing to add a section to [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) up our rolling functions but that's an optional bonus. In AoC, an answer is an answer!

### Cleanup

My 4 nearly-identical functions have been bugging me, so let's condense a little. Let's start with the two closest-matching pairs: vertical and horizontal rolling. These each change the same half of the location tuple, so the'll have to adjust the fewest things.

A diff shows us the exact differences:

```py del={1,3,7} ins={2,4,8}
def roll_up(rocks: Points, walls: Points) -> None:
def roll_down(rocks: Points, walls: Points, grid_size: int) -> None:
    for row, col in sorted(rocks):
    for row, col in sorted(rocks, reverse=True):
        new_row = None

        for potential_new_row in range(row - 1, -1, -1):
        for potential_new_row in range(row + 1, grid_size):
            ... # identical from here down
```

They are:

1. `down` takes an extra argument
2. `down` sorts its rocks in reverse
3. `down` passes totally different arguments to `range`

Of the 3 differences, only #3 is really going to give us any trouble. Let's write a `_roll_vertically` that we can call from `roll_up` and `roll_down` (to keep our nice top-level interface):

```py ins="range_builder(row)" ins="reverse=reverse_sort" ins={1,4,20-25,29-34}
RangeGen = Callable[[int], range]

def _roll_vertically(
    rocks: Points, walls: Points, reverse_sort: bool, range_builder: RangeGen
) -> None:
    for row, col in sorted(rocks, reverse=reverse_sort):
        new_row = None

        for potential_new_row in range_builder(row):
            potential_new_spot = potential_new_row, col
            if potential_new_spot in walls or potential_new_spot in rocks:
                break
            new_row = potential_new_row

        if new_row is not None:
            rocks.remove((row, col))
            rocks.add((new_row, col))

def roll_up(rocks: Points, walls: Points) -> None:
    _roll_vertically(
        rocks,
        walls,
        reverse_sort=False,
        range_builder=lambda row: range(row - 1, -1, -1),
    )


def roll_down(rocks: Points, walls: Points, grid_size: int) -> None:
    _roll_vertically(
        rocks,
        walls,
        reverse_sort=True,
        range_builder=lambda row: range(row + 1, grid_size),
    )
```

We can do a similar thing with `_roll_horizontally`. Now we're down to 2 business functions instead of 1; we can mark the "public" part of this code (the functions the solution should use) from the actual logic by marking the latter with a leading underscore. Though the entire thing is in a single file, we can practice defining a public "API" to an implementation.

I'm not positive I want to combine the two functions into one, but we can at least see how we _would_ do it. Here's the diff again (highlighting non-name differences):

```py del={1,4,9,17} ins={5,10,18}
def _roll_vertically( # _horizontally is the + lines
    rocks: Points, walls: Points, reverse_sort: bool, range_builder: RangeGen
) -> None:
    for row, col in sorted(rocks, reverse=reverse_sort):
    for row, col in sorted(rocks, key=lambda loc: loc[1], reverse=reverse_sort):
        new_row = None

        for potential_new_row in range_builder(row):
            potential_new_spot = potential_new_row, col
            potential_new_spot = row, potential_new_col
            if potential_new_spot in walls or potential_new_spot in rocks:
                break
            new_row = potential_new_row

        if new_row is not None:
            rocks.remove((row, col))
            rocks.add((new_row, col))
            rocks.add((row, new_col))
```

That's actually not too bad. I'm not sure we'll write a better function by combining them, but it's worth trying:

```py ins={6,8,9,11-14,21-22,25,30}
def _roll(
    rocks: Points,
    walls: Points,
    reverse_sort: bool,
    range_builder: RangeGen,
    index_to_replace: int,
):
    for rock in sorted(rocks, reverse=reverse_sort):
        new_rock = None

        for potential_new_value in range_builder(rock[index_to_replace]):
            _new_rock = list(rock)
            _new_rock[index_to_replace] = potential_new_value
            potential_new_rock = tuple(_new_rock)

            if potential_new_rock in walls or potential_new_rock in rocks:
                break
            new_rock = potential_new_rock

        if new_rock is not None:
            rocks.remove(rock)
            rocks.add(new_rock)

def roll_up(rocks: Points, walls: Points) -> None:
    _roll(
        rocks,
        walls,
        reverse_sort=False,
        range_builder=lambda row: range(row - 1, -1, -1),
        index_to_replace=0,
    )

... # same for other directions
```

Also not too bad! We aren't able to destructure anything, but I'm not sure that makes it less readable. Also, after forgetting to add the dynamic sorting method, I realized it's apparently not necessary. The `reverse` is still important, but sorting the rocks horizontally doesn't require them to be sorted right to left. The more you know!

Anyway, we could keep breaking this down, but I'm fairly pleased with how it ended up (and this post is already long). Until tomorrow!
