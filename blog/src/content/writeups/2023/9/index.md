---
year: 2023
day: 9
title: "Mirage Maintenance"
slug: 2023/day/9
pub_date: "2023-12-09"
---

## Part 1

Our puzzle today calls for a list of `int`s, which will grow into a list of list of `int`s. Let's parse some input!

```py
NestedList = list[list[int]]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        histories: NestedList = [list(map(int, line.split())) for line in self.input]
```

It's a little bit dense, but we're just turning strings into numbers; it's not rocket science.

Next, we need a function to "simplify" a list of `int`s into a bunch of zeroes. It'll keep looping until every item is `0`:

```py
...

def simplify(nums: list[int]) -> NestedList:
    result = [nums]

    while True:
        last = result[-1]
        if all(e == 0 for e in last):
            return result

        result.append([r - l for l, r in zip(last, last[1:])])
        last = result[-1]
```

This approach takes advantage of a fun Python trick - `zip(l, l[1:])` - which gets us tuples of each consecutive pair of items in a list:

```py
a = [1,2,3,4,5]
print(list(zip(a, a[1:])))
# [(1, 2), (2, 3), (3, 4), (4, 5)]
```

Anyway, now we've got the `NestedList` that represents the input and every layer down to the `0`s. Now, we need to add an element to each list representing the last item in it and the layer below it. There's a couple of ways to approach this, but I figure we stick with our zip trick from before. We want to look at each pair of lists (from the bottom up) and add their last elements:

```py
def extrapolate(layers: NestedList) -> int:
    for l, r in zip(layers[::-1], layers[::-1][1:]):
        r.append(l[-1] + r[-1])

    return layers[0][-1]
```

This also uses `list[::-1]` to reverse the list in question, which is what we need.

To put it all together, we need a comprehension:

```py ins={7}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        histories: NestedList = [list(map(int, line.split())) for line in self.input]

        return sum(extrapolate(simplify(h)) for h in histories)
```

## Part 2

Part 2 is about the same as part 1, we just have to tweak our extrapolation approach. First, let's refactor our existing code ot make space for part 2:

```py del={3} ins={4,10,13,18} ins={_solve}
...

def extrapolate(layers: NestedList) -> int:
def extrapolate_right(layers: NestedList) -> int:
    ...

class Solution(StrSplitSolution):
    ...

    def _parse_input(self) -> NestedList:
        return [list(map(int, line.split())) for line in self.input]

    def _solve(self, extrapolator: Callable[[NestedList], int]) -> int:
        histories = self._parse_input()
        return sum(extrapolator(simplify(h)) for h in histories)

    def part_1(self) -> int:
        return self._solve(extrapolate_right)
```

Next, we need a new extrapolator that pulls/adds data from the front, not the back (differences highlighted):

```py ins={3} ins="_left" ins="layers[0][0]"
def extrapolate_left(layers: NestedList) -> int:
    for l, r in zip(layers[::-1], layers[::-1][1:]):
        r.insert(0, r[0] - l[0])

    return layers[0][0]
```

Ultimately we could probably make an extrapolate function to handle both cases, but it would be twice as complicated as our simpler, repetitious functions.

Lastly, we call our tweaked solve method and call it a day!

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return self._solve(extrapolate_left)
```

---

_edit_: After writing all of the above, I checked Reddit and saw a solution so simple I can't believe it didn't occur to me. Part 1 and 2 are the same except we go in the opposite direction. So, instead of changing our extrapolation at all, we could just reverse the list! Duh.

```py rem={3,7} ins={4,8,13,16} ins="h[::-1] if reverse else h"
...

def extrapolate_right(layers: NestedList) -> int:
def extrapolate(layers: NestedList) -> int:

class Solution(StrSplitSolution):
    def _solve(self, extrapolator: Callable[[NestedList], int]) -> int:
    def _solve(self, reverse: bool) -> int:
        histories = self._parse_input()
        return sum(extrapolate(simplify(h[::-1] if reverse else h)) for h in histories)

    def part_1(self) -> int:
        return self._solve(reverse=False)

    def part_2(self) -> int:
        return self._solve(reverse=True)
```
