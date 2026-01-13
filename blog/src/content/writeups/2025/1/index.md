---
year: 2025
day: 1
slug: "2025/day/1"
title: "Secret Entrance"
# concepts: []
pub_date: "2026-01-12"
---

December ~~is~~ was here, which means it's [Advent of Code](https://adventofcode.com/) season! There were some [big changes](https://old.reddit.com/r/adventofcode/comments/1ocwh04/changes_to_advent_of_code_starting_this_december/) this year, and I'm not just talking about the puzzles. Late last year, my wife and I [adopted a baby](https://xavd.id/blog/post/first-day-of-the-rest-of-my-life/)! So as you can imagine, my December was totally shot as far as coding (or really thinking at all) went.

But I love AoC and writing these little posts. And now that my [Favorite Media of the Year](https://david.reviews/articles/favorite-media-2025/) post is done, I've got just a bit of time on my hands.

I'll be surprised if I get close to finishing all 12 of these puzzles, but let's see where we (eventually) get. Either way, thanks for at least reading what I do publish!

If it's your first time, here's the gist for these posts (copied from [last year](https://advent-of-code.xavd.id/writeups/2024/day/1/)):

> There are a few goals:
>
> - improve understanding of what's available in the Python standard library
> - produce clear, readable code
> - get comfortable with non-trivial programming concepts
>
> Readers are [expected to have](https://advent-of-code.xavd.id/#audience) a basic understanding of programming fundamentals. Advent of Code isn't the place to learn programming from scratch ([Exercism's bootcamp](https://bootcamp.exercism.org/) is a better place for that).
>
> Each of my solutions will use my [GitHub template](https://github.com/xavdid/advent-of-code-python-template), which handles some basic input parsing. It also has a good [Ruff](https://docs.astral.sh/ruff/) setup for linting and formatting. Feel free to fork this an adapt it for your needs! I didn't include any utility functions in the template itself, but you're encouraged to write and use your own. I've got a few (like for graph traversal) that I'll reference in my solutions, but you can take whatever approach you'd like.

Let's get to it!

## Part 1

Toady relies on two basic concepts:

- strings are iterables
- the modulo (`%`) operator

First, let's parse.

> Remember, I'm using a [custom class](https://github.com/xavdid/advent-of-code-python-template/blob/be255ce38893788ea6d74ac330a8c33838e28429/solutions/base.py#L204) to parse the input into a list of strings. That template is available to copy if you'd like a similar setup!

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        for line in self.input:
            direction, *raw_distance = line
            distance = int("".join(raw_distance))
            if direction == "L":
                distance *= -1
```

We're taking advantage of the fact that Python's strings are iterables. So `direction, *raw_distance = line` grabs the first character and all the rest separately (using the spread operator, `*`), which is perfect for our use case. We also treat `L` rotations as negative, since they cause the number to go down.

Though we're not actually tracking our position anywhere yet. Let's fix that:

```py ins={3,4,9,11,12,14}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        current = 50
        num_zeroes = 0

        for line in self.input:
            ...

            current = (current + distance) % 100

            if current == 0:
                num_zeroes += 1

        return num_zeroes
```

We update our position, `current`, with . The real key is the aforementioned `%`, which lets us cleanly wrap values outside the 0-100 range to be inside that range instead.

Every time we land on exactly `0`, we increment a counter, eventually returning it for our answer! Nothing much to see here yet, just a nice little warmup.

## Part 2

Little bit trickier now! Instead of using modulo to figure out where we eventually land, we have to know if/when we're crossing `0`, which means a bit of extra math.

I took a couple of passes on this, using Python's floor division (`//`) to figure out how many times we passed `0`. But I kept hitting little edge cases and as the code grew in complexity, my answers weren't correct. Maybe I'm still thinking a little less clearly than I thought.

Luckily, we can still do it the simple way way and see if that works. We'll make a big list of all the numbers we cross while rotating and count the zeroes. Listen, if it's stupid and it works, then it's not that stupid.

All it takes are some small tweaks to our code:

```py rem={2,10-11,21-22} ins={3,12-13,15-17}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def part_2(self) -> int:
        current = 50
        num_zeroes = 0

        for line in self.input:
            direction, *raw_distance = line
            distance = int("".join(raw_distance))
            if direction == "L":
                distance *= -1
            step = -1 if direction == "L" else 1
            distance *= step

            num_zeroes += [
                i % 100 for i in range(current, current + distance, step)
            ].count(0)

            current = (current + distance) % 100

            if current == 0:
                num_zeroes += 1

        return num_zeroes
```

The only tricky bit is generating the `range`. While it's most commonly constructed with a single argument (e.g. `range(10)`), it actually supports `start`, `stop`, and `step` arguments too. This lets us easily create reverse ranges by specifying a `step` (e.g. the distance we move between each item in the range) of `-1` when rotating left.

When our range is built correctly, we just count up the zeroes and arrive at our answer!
