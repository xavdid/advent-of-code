---
year: 2022
day: 6
title: "Tuning Trouble"
slug: "2022/day/6"
pub_date: "2022-12-06"
---

## Part 1

Eric, the creator of AoC, has [talked about](https://old.reddit.com/r/adventofcode/comments/7idn6k/question_why_does_the_difficulty_vary_so_much/dqy08tk/) how making puzzles is hard. Even harder is correctly sorting them in increasing difficulty (every person / language is good at different things). As a result, some days feel extra straightforward, like today. But, I'm not one to look a gift horse in the mouth; let's take the W.

We have to iterate over a string, looking at each 4-letter chunk. If all letters in that chunk are unique, then we return the index where the chunk ends. We have all the tools to do this:

- we know how to iterate over a specific set of numbers (`range`)
- we know how to slice a subset of a list (see [yesterday](/writeups/2022/day/5/#part-1-for-real))
- we know how to remove duplicates from an iterable (`set`)

Let's string it together:

```py
def find_packet_start(s: str) -> int:
    for i in range(4, len(s)):
        if len(set(s[i - 4 : i])) == 4:
            return i
    raise ValueError("not found")
```

There's no reason to start before `4`, since we can't have seen 4 values yet. For every subsequent set of 4 letters, we put them in a set (removing duplicates). If there are 4 items in the set, we know they must be unique (whatever they were) and know that we've found our result!

As a side note, we also raise an error in case we get to the end of our loop and haven't returned. If we neglected to do that (and we weren't guaranteed to find a valid start-marker), then the function could (implicitly) return `None`, which would be confusing. So, it's a best practice to fail loudly.

## Part 2

If you thought you'd have to adjust a bunch of code for part 2, have no fear! We just replace `4` with a variable and we're all set:

```py
def find_packet_start(s: str, packet_size: int) -> int:
    for i in range(packet_size, len(s)):
        if len(set(s[i - packet_size : i])) == packet_size:
            return i
    raise ValueError("not found")

class Solution(TextSolution):
    def part_1(self) -> int:
        return find_packet_start(self.input, 4)

    def part_2(self) -> int:
        return find_packet_start(self.input, 14)
```

Well, that was a [freebie](https://www.youtube.com/watch?v=4BaLprtbhvw). See you tomorrow!
