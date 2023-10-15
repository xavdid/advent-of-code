---
year: 2022
day: 1
title: "Calorie Counting"
slug: "2022/day/1"
pub_date: "2022-12-01"
---

## Part 1

Once more into the breach! Welcome to Advent of Code 2022. As with previous years, I'll be writing up a (mostly) daily explanation of the solution. By following along each day, you'll gain a deeper understanding of the Python stdlib, how to write maintainable code, and what common algorithms are out there. You don't need to have read previous years' solutions to enjoy these writeups, but you do need some basic programming experience (outlined [here](https://github.com/xavdid/advent-of-code/tree/main/solutions#audience)). Solving these puzzles (with or without my help) should help you grow both as an engineer and as a programmer.

Each of my solutions uses my tried-and-true [solution helper class](https://github.com/xavdid/advent-of-code/blob/main/solutions/base.py). Among other things, it handles the input parsing (so I won't be showing that in my solutions directly). I'll just include a `self.input`, which will vary in type depending on what the puzzle requires. Feel free to copy my tooling (there's instructions [here](https://github.com/xavdid/advent-of-code)) if you'd like. Otherwise, replace my `self.input` with whatever variable holds your puzzle input.

Without further adieu, let's get to it!

---

Day 1 starts pretty straightforward: we have to parse a list of strings into ints, sum them, and find the biggest element. First up, we'll want to get a list of the raw values for each elf. There's a blank line, so we can split a double newline:

```py
elves = self.input.split("\n\n")
```

Next we have to turn the value of each elf (currently `"1000\n2000\n3000"`) into a series of numbers, then add them. The verbose way to do this is as follows:

```py
...

calorie_counts = []
for elf in elves:
    total = 0
    for snack in elf.split("\n"):
        total += int(snack)
    calorie_counts.append(total)
```

Now that we have the calorie value of each elf's snacks, we can return the `max` to wrap up part one:

```py
...

return max(calorie_counts)
```

## Part 2

Now we we need the sum of the top 3 elves, not just the first one. We can combine our solutions, since they use the same setup. Instead of returning only the `max` of `calorie_counts`, we'll need to sort the list and _also_ return a subset of the list. Luckily, Python makes that simple:

```py
...

calorie_counts.sort()

#      part 1              part 2
return calorie_counts[-1], sum(calorie_counts[-3:])
```

This takes advantage of being able to use negative values in list slices- the `[-3:]` translates to "give me the items between third-from-the-end and the end of the list", which are the 3 elves. Sum those up, and we have our part 2 answer!

## Cleanup

While there's nothing wrong with our code, we can make it less verbose using some Python conveniences. Namely, we can combine all the integer parsing into a 1-liner using `map`. Here's the full solution:

```py
raw_elves = self.input.split("\n\n")
elves = sorted(sum(map(int, elf.split("\n"))) for elf in raw_elves)
return elves[-1], sum(elves[-3:])
```

There's two cool things in this snippet: `map` and the lack of intermediate lists. Let's break them down.

The global `map` function ([docs](https://docs.python.org/3.11/library/functions.html#map)) takes a function and an iterable (aka "anything you can iterate over") and calls the function on each item.[^1] It does the same thing as a list comprehension (make a new list by doing something to every item in an old list), but is cleaner if your operation is simple.

The other interesting thing is how we don't have any square brackets here, meaning we don't have any lists! That's a little odd, right? In the past, you've probably written list comprehensions like this:

```py
nums = [1, 2, 3]
higher_nums = [i + 1 for i in nums] # [2, 3, 4]
```

If you don't include the square brackets, you get a syntax error. So why does our smaller solution work without any brackets?

```py
sorted(
    # --- what is this?
    sum(
        map(
            int,
            elf.split("\n")
        )
    )
    for elf
    in raw_elves
    # ---
)
```

To answer that question, let's look at what type(s) we can return from a comprehension:

```py
# a list, the most common result
[sum(map(int, elf.split("\n"))) for elf in ['1\n2', '2\n1']]
# [3, 3]

# a set, which removes duplicates
{sum(map(int, elf.split("\n"))) for elf in ['1\n2', '2\n1']}
# {3}

# a tuple, called explicitly
tuple(sum(map(int, elf.split("\n"))) for elf in ['1\n2', '2\n1'])
# (3, 3)

# something else entirely
(sum(map(int, elf.split("\n"))) for elf in ['1\n2', '2\n1'])
# <generator object <genexpr> at 0x104c92b90>
```

In addition to the usual containers, there's a `generator` object. These objects are specialized functions that can generate the next item in a series on demand. They're more common than you think, and you can read more about them [here](https://realpython.com/introduction-to-python-generators/#building-generators-with-generator-expressions).

The key thing to know is while they don't act like any of the other objects above (for instance, you can't get the first element with `[0]`), they _are_ iterable. This means that functions that iterate over their inputs will work equally well with a generator as they will with say, a list. That's why we can pass it directly into `sorted` in our cleaned up function without wrapping it in square brackets:

```py
...

gen = (sum(map(int, elf.split("\n"))) for elf in raw_elves)
# can't get items out of `gen` or do much with it, yet
elves = sorted(gen)
# [1, 2, 3] # now it's a list again!
```

In our case, we don't need the list of numbers before it's sorted, so there's no need to have an intermediate list. This is a common pattern when writing more concise Python code, so it's good to be familiar with it.

Interestingly, an iterable object is also what comes out of `map`:

```py
map(int, [])
# <map object at 0x104bb8820>
```

Because we were immediately passing it into `sum`, we didn't even notice.

Anyway, that should do it for today. See you tomorrow!

[^1]: This is very common in a coding paradigm called "functional programming", where all values are expressed in terms of chains of functions. You don't need to know that here, but it's a great term to be aware of.
