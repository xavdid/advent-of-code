---
year: 2020
day: 9
title: "Encoding Error"
slug: "2020/day/9"
pub_date: "2020-12-09"
---

## Part 1

Once again, we don't have to do anything too fancy here. Summing numbers is fast, so it's ok if we do it a lot. Combining that with a `set` for fast lookup and we can safely repeat a lot of work.

On each step of our loop, we want an element and all of the sums for the 25 previous elements. I use a `PREAMBLE_SIZE` variable so I could easily set it to `5` and `25` for testing as needed, but it's not super necessary.

We'll look at each index starting at `PREAMBLE_SIZE`:

```py
for i in range(PREAMBLE_SIZE, len(self.input)):
```

Next, the sums. Just like [day 1](https://github.com/xavdid/advent-of-code/tree/main/solutions/202001), we'll reach for `itertools.combinations`:

```py
sums = {
    sum(pair) for pair in combinations(self.input[i - PREAMBLE_SIZE : i], 2)
}
```

This strikes me as a great example of Python code being both readable and concise (not to toot my own horn). Each piece should be familiar:

- `self.input[i - PREAMBLE_SIZE : i]` gets the 25 elements directly before our index
- `combinations(X, 2)` gets us all of our pairs (like `[(1, 2), (2, 3), (1, 3)]`)
- `{sum(pair) for pair in X}` gives us a set of each of those sums

Lastly, we run through our loop and return the number that isn't in the set:

```py
if self.input[i] not in sums:
    return self.input[i]
```

## Part 2

This is another day where my `solve` function comes into play (running both parts at once instead of doing it separately). The answer from `part_1` is stored as `bad_num`.

This will be another brute-force approach. We have to step very slowly through the input, taking an increasingly large range until we meet or exceed the `bad_num`.

We start at the very beginning and initialize a running sum:

```py
for range_start in range(len(self.input)):
    running_sum = self.input[range_start] = self.input[range_start]
```

Then, we iterate again (which feels unavoidable at this point), incrementally summing the ongoing range until either:

- `running_sum == bad_num`, in which case we can finish
- `running_sum > bad num`, so we have to start a new range

```py
for range_end in range(range_start + 1, len(self.input)):
    running_sum += self.input[range_end]
    if running_sum == bad_num:
        continuous_range = self.input[range_start : range_end + 1]
        return bad_num, min(continuous_range) + max(continuous_range)
    if running_sum > bad_num:
        break
```

This is another example where we can get away with returning from deep in a loop because we _know_ we'll get there sometime. Otherwise we'd need a plan for if we fail-to-find.
