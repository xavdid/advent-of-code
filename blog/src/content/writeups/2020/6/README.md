---
year: 2020
day: 6
title: "Custom Customs"
slug: "2020/day/6"
pub_date: "2020-12-06"
---

## Part 1

The input parsing here looks a lot like that in [Day 4](/writeups/2020/day/4/#part-1) - we'll want to take our big input as a string and split it by the double newline.

Ultimately, we need to flatten each group into one long string and count the unique characters. Splitting each group into a list of characters is straightforward enough:

```py
groups = self.input.split("\n\n")
for group in groups:
    chars = list("".join(group.split("\n")))

['a', 'b', 'c', 'x', 'a', 'b', 'c', 'y', 'a', 'b', 'c', 'z']
['a', 'b', 'c']
['a', 'b', 'c']
['a', 'b', 'a', 'c']
['a', 'a', 'a', 'a']
['b']
```

That's great, but we still need to remove the duplicates. Python's `set`s are perfect for this exact thing. They're collections (like `list`s), but differ in two important ways:

- there are no duplicates (adding an element again is ignored)
- there's no order to the elements

Sounds perfect for us! Let's swap `set` in for `list`:

```py
groups = self.input.split("\n\n")
for group in groups:
    chars = set("".join(group.split("\n")))

{'b', 'y', 'x', 'a', 'z', 'c'}
{'b', 'c', 'a'}
{'b', 'c', 'a'}
{'b', 'c', 'a'}
{'a'}
{'b'}
```

Then to get our answer, we need to sum up all of the set sizes. Wrap that in a [list comprehension](https://docs.python.org/3.8/tutorial/datastructures.html#list-comprehensions) (a succinct way to write loops) and putting _that_ in a `sum` call nets us our answer as a one-liner:

```py
return sum(
    [len(set("".join(group.split("\n")))) for group in self.input.split("\n\n")]
)
```

But, for readability's sake, it's worth breaking it up a little bit:

```py
groups = self.input.split("\n\n")
total = 0
for group in groups:
    all_chars_as_str = "".join(group.split("\n"))
    total += len(set(all_chars_as_str))
return total
```

Unless you're literally trying to fit code in the fewest bytes possible, a clear, reable solution is always better than a concise, clever one!

## Part 2

For part two, we need to find the letters that appear in all rows of a group. Though we don't need sets for their de-duplication abilities, they do provide an `intersection` method that'll do exactly what we want:

```py
{1,2,3}.intersection({1, 2, 4}, {1})

{1}
```

So our setup will be mostly the same as before:

```py
...
answers = [set(x) for x in group.split("\n")]
```

Now, a quandary. To use the `.intersection` method, we need a set object to call it on. But if we make a fresh one, then our result will always be empty:

```py
set().intersection({1}, {1})

set() # empty, we wanted {1}
```

Never fear - we can use the first set in our list as the base:

```py
answers[0].intersection(answers[1:])

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'set'
```

Python doesn't like us passing a `list` to `.intersection` (because `list`s are mutable and therefore can't go into a set). So we need to turn our `list` into a bunch of arguments.

Enter Python's `*` operator (sometimes called "splat" or "unpacking" operator). Used with a `list` or `set`, it provides them individually to a function:

```py
def func(a, b, c):
    print(a, b, c)

func([1,2,3])

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: func() missing 2 required positional arguments: 'b' and 'c'

func(*[1,2,3])
1 2 3
```

Hey, that's what we need to do!

```py
groups = self.input.split("\n\n")
total = 0
for group in groups:
    answers = [set(x) for x in group.split("\n")]
    total += len(answers[0].intersection(*answers[1:]))

return total
```

Python's `*` and `**` (not covered here, but it's got similar behavior, but for `dict`s) are powerful tools for programmatically calling functions. Definitely worth [reading more about them](https://stackoverflow.com/a/36908/1825390).
