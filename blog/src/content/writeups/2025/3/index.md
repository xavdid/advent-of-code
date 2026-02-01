---
year: 2025
day: 3
slug: "2025/day/3"
title: "TKTK"
concepts: [recursion]
# pub_date: "TBD"
---

## Part 1

Today seemed intimidating until I realized that these numbers are only 2 digits. I just need to find two numbers:

- the biggest number that's not the last one in the line
- the biggest number to the right of that

Everything that starts with a `9` will be bigger than any `8`, and so on. The only real trick is remembering not to lead with the last number in a line, since nothing can follow it.

The code itself is similarly straightforward. Python's [slice syntax](https://realpython.com/ref/glossary/slicing/) makes it easy to get "everything but the last element" or "everything starting at index N". Wrap that in a little function and we've got our answer:

```py
def highest_joltage(num: str) -> int:
    digits = [int(i) for i in num]

    best_lead = max(digits[:-1])
    lead_index = digits.index(best_lead)

    best_follow = max(digits[lead_index + 1 :])

    return best_lead * 10 + best_follow

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return sum(highest_joltage(line) for line in self.input)
```

## Part 2

Well, that didn't last long. Luckily, our general approach is sound, but we need to tweak the algorithm so that the size of our number is configurable. Believe it or not, this is a great use case for recursion!

Part 1 illustrated the two steps in our algorithm: find a lead digit and find a tail digit. If we wanted to find a 3-digit number, the process would be mostly the same. We'd find a lead digit that has at least 2 numbers after it, then find a 2-digit number to its right. A 4-digit number is a lead digit that's 3+ spots from the end followed by our 3-digit number above. And so the recursive shape of this problem starts to take shape.

To find a number of any length `N`, we find the highest lead with enough space behind it followed by the largest `N-1`-digit number. On each recursion, we pass the digits to the right of the last lead digit and decrement its length. Eventually we just need a 1 digit number, which will be the `max` of the digits (with no more recursion).

We'll restructure our code to separate concerns a bit. Now our function will _only_ find numbers, not do any of the type conversion we'll need for the actual problem. Here's the diff:

```py del={1,3,7,11,13} ins={2,4-5,8,14}
def highest_joltage(num: str) -> int:
def _recursive_joltage(digits: list[int], length: int) -> list[int]:
    digits = [int(i) for i in num]
    if length == 1:
        return [max(digits)]

    best_lead = max(digits[:-1])
    best_lead = max(digits[: -(length - 1)])
    lead_index = digits.index(best_lead)

    best_follow = max(digits[lead_index + 1 :])

    return best_lead * 10 + best_follow
    return [best_lead] + _recursive_joltage(digits[lead_index + 1 :], length - 1)
```

It's the same basic approach, with a couple of key differences:

- as mentioned, we're only dealing with `list[int]`. The conversion from string goes elsewhere
- we're returning a `list[int]` that gets built up as we recurse
- the length we recurse shrinks until it hits `1` (our **base case**)
- the index we stop at has changed: it's now calculated based on length. For a 2-digit number, we used `-1`. So for an `N` digit number, we stop at `-(N-1)`

Now we need the last couple of functions: converting to and from a string and our actual solving func, for reuse:

```py del={10} ins={11}
def highest_joltage(num: str, length: int) -> int:
    digits = _recursive_joltage([int(i) for i in num], length)
    return int("".join(map(str, digits)))

class Solution(StrSplitSolution):
    def _solve(self, length: int) -> int:
        return sum(highest_joltage(line, length) for line in self.input)

    def part_1(self) -> int:
        return sum(highest_joltage(line) for line in self.input)
        return self._solve(2)

    def part_2(self) -> int:
        return self._solve(12)
```

We even got to simplify our part 1 code to use this function
