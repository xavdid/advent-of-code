---
year: 2021
day: 10
title: "Syntax Scoring"
slug: "2021/day/10"
pub_date: "2021-12-10"
---

## Part 1

This is a fun one! The punctuation may look daunting, but it's a straightforward puzzle. On each line, you can always add an open bracket. But, if it's a close bracket, it must be of the same type as the most recent open. This is a common task that programming language parsers face called "matching brackets".

There are many ways to do this, but the easiest is with a stack. In Computer Science, a _stack_ is a "last in, first out" structure. It's the opposite of a _queue_, which is "first in, first out".

Some languages have built-in `Stack` classes - Python isn't one of them. The native `list` has `.append()` and `.pop()`, which get us what we need. We can add and remove from the end of the list, so the last element we added will be the first removed. Sounds like a stack to me!

I started by defining the constants I was going to need. Namely, which pairs of characters matched and how much the various end pieces were worth:

```py
OPENERS = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
}
CLOSERS_INVALID = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}
```

Next, we could go through lines. On each line, I'd add all the open brackets to our stack. When we get to a closing bracket, we verify that the last item in the stack is its pair. If it is, great! We remove that opener from our stack and move on. If it's not, then we have found an invalid line and can score it appropriately:

```py
invalid_score = 0
for line in self.input:
    incomplete_pairs = []
    for c in line:
        if c in OPENERS:
            incomplete_pairs.append(c)
        else:
            if OPENERS[incomplete_pairs[-1]] != c:
                # invalid line!
                invalid_score += CLOSERS[c]
                break

            incomplete_pairs.pop()

return total
```

If that code is hard to follow, I recommend adding some `print` statements to show when a character is added or removed. Should make it very easy to step through the function.

Now, I wonder what we'll do with these not-invalid lines...

## Part 2

We'll complete them! We got lucky here- we've already done the hard work. When our `for c in line` loop above finishes, `pairs` will have all of the unmatched openers. Well, [that was a freebie](https://youtu.be/9ltqCJn7qkc?t=18).

We can adapt our part 1 code a bit to give us all the pairs from the valid lines and then get to the scoring. Here's that but adapted to keep the valid lines:

```py
invalid_score = 0
valid_line_scores: List[int] = []
for line in self.input:
    was_valid_line = True
    incomplete_pairs: List[str] = []
    for c in line:
        if c in OPENERS:
            incomplete_pairs.append(c)
        else:
            if OPENERS[incomplete_pairs[-1]] != c:
                # invalid line!
                invalid_score += CLOSERS_INVALID[c]
                was_valid_line = False
                break

            incomplete_pairs.pop()
```

Now we write a little scoring method:

```py
def closing_score(nums) -> int:
    score = 0
    for i in nums:
        score *= 5
        score += i
    return score
```

And a way to transform our remaining openers into a list of scores:

```py
CLOSERS_MATCHING = {
    ")": 1,
    "]": 2,
    "}": 3,
    ">": 4,
}

for line in self.input:
    ...

    if was_valid_line:
        closers_needed = reversed(
            [CLOSERS_MATCHING[OPENERS[p]] for p in incomplete_pairs]
        )
        valid_line_scores.append(closing_score(closers_needed))
```

When that's all said and done, we're back at the top of our loop and can get the middle score. To get the middle, we need to sort the list and get the index of rounding down the `len / 2`. Python's integer division does this for us:

```py
5 / 2
# => 2.5

5 // 2
# => 2
```

So:

```py
middle_score = sorted(valid_line_scores)[len(valid_line_scores) // 2]

return invalid_score, middle_score
```

Looked intimidating, but didn't end up being terribly significant code!
