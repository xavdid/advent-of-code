---
year: 2020
day: 3
title: "Toboggan Trajectory"
slug: "2020/day/3"
pub_date: "2020-12-03"
---

## Part 1

This is simpler than it looked at first glance. We only look at each row once and we need to loop around when the reach the end of the list. The modulo operator (`%`) is perfect for this:

```py
trees = 0
width = len(self.input[0]) # only need to calculate once
for index, line in enumerate(self.input):
    if line[(index * 3) % width] == "#":
        trees += 1
return trees
```

## Part 2

At first I thought part 2 was as easy as making my function generic and adding a skip if `down > 1`:

```py
def count_trees(self, right: int, down: int) -> int:
    width = len(self.input[0])
    trees = 0

    for index, line in enumerate(self.input):
        if down > 1 and index % down != 0:
            continue

        if line[(index * right) % width] == "#":
            trees += 1
    return trees
```

For the example, this yielded `[2, 7, 3, 4, 1]` which is _nearly_ right. We got `1` for `Right 1, Down 2` instead of `2`. Previously, we could use `index` to see how many lines we've looked at, but now that we're skipping some lines, we'll have to account for that in our indexing:

```py
def count_trees(self, right: int, down: int) -> int:
    width = len(self.input[0])
    trees = 0

    for index, line in enumerate(self.input):
        if down > 1 and index % down != 0:
            continue

        if line[(index // down * right) % width] == "#":
            trees += 1

    return trees
```

This gives us a nice generic function that we can fulfill both parts of the puzzle with!
