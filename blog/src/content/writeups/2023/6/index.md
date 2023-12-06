---
year: 2023
day: 6
title: "Wait For It"
slug: 2023/day/6
pub_date: "2023-12-05"
---

## Part 1

This seems... suspiciously simple. Let's code it up and see where that takes us.

First, input parsing. There are 2 lines and a few columns; we don't care about the first column. There are a few ways to parse the input so that it'll handle any numbers of columns. The key to both approaches is The more verbose one is `line.split()[1:]`, which splits on whitespace (of any size). It also throws out that label column that we don't need.

So, we can do each line on their own:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        times = [int(t) for t in self.input[0].split()[1:]]
        distances = [int(d) for d in self.input[1].split()[1:]]
        races = zip(times, distances) # [(7, 9), (15, 40), (30, 200)]
```

But, those two lines are identical, so we could use a comprehension too:

```py ins={3}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        races = zip(*(map(int, line.split()[1:]) for line in self.input))
```

That's maybe a little too dense, but it's not too bad. The trickiest bit is using `*`, the [unpacking operator](https://realpython.com/python-kwargs-and-args/#unpacking-with-the-asterisk-operators), to send each `map` result into `zip` as a separate argument. We can afford to play a little fast & loose with this, since we know with some certainty how our input will be shaped.

Whichever approach you pick, we've now got an iterable full of race info. Now we need to see how far you get for each button hold duration. We want to check every value between `1` and `time` and run it through the equation described in the prompt, which is fairly simple. We can add a filter to a list comprehension to get this in one line:

```py
def num_race_wins(time: int, distance: int) -> int:
    return len([1 for t in range(1, time) if t * (time - t) > distance])
```

We don't actually care about the output of the expression, so we're just using a list filled with `1`s and taking the length.

Back in the solver, all that remains is to run our races through the counter and multiply the results:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        result = 1

        for time, distance in races:
            result *= num_race_wins(time, distance)

        return result
```

If we were adding results, we could use a comprehension with `sum`, but there's no built-in for mass-multiplication.

If you're interested in [functional programming](https://en.wikipedia.org/wiki/Functional_programming), `reduce` can further simplify this last part. It's good for "reducing" a list into a single value:

```py ins={5}
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        return reduce(lambda res, race: res * num_race_wins(*race), races, 1)
```

Son once again, pick your poison!

## Part 2

Those numbers looked big, so I was gearing up to figure out a clever way solve this one. But... I'm just doing simple math. I bet I can do a _lot_ of simple math in a reasonable time frame.

Our parsing has changed slightly- we `"".join()` our columns before parsing them as an int. Otherwise, our `num_race_wins` function serves us well:

```py ins={3,4}
class Solution(StrSplitSolution):
    def part_2(self) -> int:
        time, distance = [int("".join(line.split()[1:])) for line in self.input]
        return num_race_wins(time, distance)
```

Using Python 3.12, this ran in ~ 2.5 seconds. Longer than I'd want (I really do like the "instant" solutions). But, given its simplicity, I'm happy to keep this one as is. That just goes to show - if it's stupid and it works, then it's not stupid.

Anyway, there definitely seems to be a difficulty pattern emerging here. See you (eventually...) for tomorrow's puzzle!
