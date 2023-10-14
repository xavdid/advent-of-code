---
year: 2021
day: 1
title: "Sonar Sweep"
slug: "2021/day/1"
pub_date: "2021-12-01"
---

## Part 1

Welcome one and all to Advent of Code 2021! This is one of my favorite events of the year. Just like last year, I'll be posting daily explainers for each puzzle (usually day-of, but I'll slow down as we get into harder puzzles).

Reminder that my solutions take advantage of my [AoC base class](https://github.com/xavdid/advent-of-code/blob/main/solutions/base.py), which handles input parsing, among other things. When I reference `self.input`, that's a parsed copy of the puzzle input. Parsing changes each day- it's usually one of: `str, int, List[str], List[int]`. You can use my base class (instructions are in the [README](https://github.com/xavdid/advent-of-code#quickstart)), or do your own parsing.

Anyway, let's get to it!

---

To kick the year off, we'll be iterating a list of numbers and comparing each to the one right before it. We'll also have a running count, so we'll track that too.

For each item, we increment our total if:

1. the item isn't the first in the list
2. the item is larger than the one before it.

There's no trick here, so we can write it just like that:

```py
total = 0

for index, i in enumerate(self.input):
   if index > 0 and i > self.input[index - 1]:
       total += 1

return total
```

## Part 2

The last step of part 2 is generically the same as part 1, it just takes different input. So, I started by extracting my part 1 solution into a function:

```py
def num_increases(nums: List[int]) -> int:
    # same as above
    ...
```

Now the puzzle is how to transform our list of numbers into the sum of its neighbors. We can break the problem down as follows:

1. Split the input into many smaller lists. Each sub-list should have a number and the 2 right after it
2. Sum each sub-list, leaving us (once again) with a list of numbers
3. Run that number through our function above.

Let's do #1 with a simple iteration:

```py
windows = [
   [self.input[i], self.input[i + 1], self.input[i + 2]]
   for i in range(0, len(self.input) - 2)
]

return num_increases([sum(w) for w in windows])
```

Using `range` with a second arg keeps us from going too far. We do a quick [list comprehension](https://realpython.com/list-comprehension-python/) to sum each window, and pass it to our function above. :tada: Tada! That's all it took.

If you'd like to be done here, you can be! This code works and we have our answer. But, we can improve it if we'd like.

---

An easy improvement is to use slices for each window instead of manually specifying the indexes:

```py
windows = [sum(self.input[i : i + 3]) for i in range(0, len(self.input) - 2)]
```

Python's slice syntax is a fancy way to get part of a list. Instead of `l[NUMBER]`, you can do `l[start_index : stop_index]`. The slice doesn't include the stop index, so to get 3 total elements, we add `3` to the current index.

Our second approach works just as well as the first, but in a slightly more "pythonic" manner. But, I didn't love how we had to specify a bunch of start and stop indexes- that's an easy place to make a mistake.

One last approach is using `zip`, which "zips" up multiple iterables into little groups. For each list, it makes a group from the first element, the second element, etc:

```py
zip([1,2,3], [4,5,6], [7,8,9])
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
```

Instead of thinking of our windows as neighbors in a list, what if they were elements from 3 separate lists? Take the following from the start of the example input:

```
   /A\ /B\ /C\
1. 199 200 208 210 200
2. 200 208 210 200
3. 208 210 200
```

If we skip the first element from the input and use it as a second list, then it lines up exactly where we want it. We can skip the first two elements and use it again. Our groups (`A`, `B`, `C`) are the same as in the example. So, if we combine our slice syntax with the `zip` function, we get:

```py
return num_increases(
   [sum(x) for x in zip(self.input, self.input[1:], self.input[2:])]
)
```

Luckily for us, `zip` stops as soon as any of the inputs end, so we don't have to worry about stopping early enough. I'm much happier with that solution than where we started.
