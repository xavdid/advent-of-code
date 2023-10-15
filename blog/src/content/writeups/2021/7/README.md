---
year: 2021
day: 7
title: "The Treachery of Whales"
slug: "2021/day/7"
pub_date: "2021-12-07"
---

## Part 1

Much like yesterday, I started by doing this in the most literal way possible. Hopefully it's still useful for part 2.

For each value from 0 to the max of the input, we should sum the amount of fuel it would take for that value and find the min. We start with the distance to `0`, which is just the sum of the input. Then, we loop and get the distance from `i` to the value (using `abs`, since we don't care about negatives). If it's less than our previous best, we store it. At the end, whatever's left is the answer! Here's how that looks:

```py
min_result = sum(self.input)  # distance to 0
for i in range(1, max(self.input)):
    distance_to_i = sum([abs(i - x) for x in self.input])
    min_result = min(min_result, distance_to_i)

return min_result
```

Surprisingly, that's all there was to it.

## Part 2

Part 2 can _likely_ be brute forced again, but it'll help us to recognize repeated work when we see it. Namely, the two numbers in the equation don't actually matter, just their distance from each other. That fuel value is `sum(range(1, distance))`. We have a couple of options for computing that sum:

1. do it fresh every time, adding numbers is fast!
2. keep track of the `that_number`s we've seen so we only do the calculation once per distance
3. know the trick about adding a range of numbers, as relayed in this probably apocryphal math anecdote:

> In the 1780s a provincial German schoolmaster gave his class the tedious assignment of summing the first 100 integers. The teacher's aim was to keep the kids quiet for half an hour, but one young pupil almost immediately produced an answer: 1 + 2 + 3 + ... + 98 + 99 + 100 = 5,050. The smart aleck was Carl Friedrich Gauss, who would go on to join the short list of candidates for greatest mathematician ever. Gauss was not a calculating prodigy who added up all those numbers in his head. He had a deeper insight: If you "fold" the series of numbers in the middle and add them in pairs -- 1 + 100, 2 + 99, 3 + 98, and so on -- all the pairs sum to 101. There are 50 such pairs, and so the grand total is simply 50×101. The more general formula, for a list of consecutive numbers from 1 through n, is `n(n + 1)/2`.

_copied from [American Scientist](https://www.americanscientist.org/article/gausss-day-of-reckoning)_

Using that last one, our part 2 code looks remarkably similar to part 1:

```py
def range_sum(i: int) -> int:
    return i * (i + 1) // 2

min_result = 100_000_000
for i in range(1, max(self.input)):
   distance_to_i = sum([range_sum(abs(i - x)) for x in self.input])
   min_result = min(min_result, distance_to_i)

return min_result
```

Instead of calculating the correct value for `0`, I just picked an arbitrarily large value and assumed the value for `1` would probably be less than that.

That's our answer, so we can stop here for the day. There's also a little bonus discussions around performance below for extra credit.

---

On my machine, running both parts as written took ~ `.4` seconds (`time ./advent 7`). Out of curiosity, I stuck a `cache` on `range_sum` and it got it down to `.3` seconds. A 25% improvement!

```py
from functools import cache # python 3.9+

@cache
def range_sum(i: int) -> int:
    return i * (i + 1) // 2
```

`cache` is some very simple magic. It's a function decorator that keeps track of how the function is called and what the result was. If we've seen a value before, we skip the calculation and just return the same result as before. Since we're likely to have a lot of repeated ranges across all loops above, this saves us a decent amount of computation (even if that computation is otherwise fast; the fastest code is the code that doesn't run at all).

A simple implementation of a cache in a function decorator is as follows:

```py
def cache(func):
    results = {}

    # this is the function that runs when a user calls the wrapped function
    def _function_wrapper(*args):
        hashable_args = tuple(args)  # so it can be used as a dict key
        if hashable_args in results:
            print("HIT")
            return results[hashable_args]
        else:
            print("MISS")
            result = func(*args)
            results[hashable_args] = result
            return result

    return _function_wrapper
```

Writing a function decorator can be a little mind-boggling. You write a function (`cache`) which takes as its argument a function (`func`) and then _returns_ a function (`_function_wrapper`) which calls `func` at some point. Let's see it in action:

```py
@cache
def add(a, b):
    return a + b


add(1, 2) # MISS
add(1, 2) # HIT
add(2, 1) # MISS

add(2, 2) # MISS

add(2, 3) # MISS
add(2, 3) # HIt
```

In the above example, `func` is `add` and `(a,b)` is `args`. The first time our wrapped `add` is called with `(1,2)`, it's not in our `results`. So, we actually run the now-obscrued `add` function (because remember, the user is _really_ calling `_function_wrapper` when they write `add(1,2)`), get our result, store it for later, and return it. The second time `add` is called with `(1,2)`, we know we've done that exact calculation before, so we just return the value in the dict.

It looks a lot harder than it actually is. There are some [great resources](https://realpython.com/primer-on-python-decorators) if you want to dig into them further. In my opinion, they're one of Python's best features!
