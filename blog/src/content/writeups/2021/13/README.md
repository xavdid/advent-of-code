---
year: 2021
day: 13
title: "Transparent Origami"
slug: "2021/day/13"
pub_date: "2021-12-13"
---

## Part 1

Wow, grid heavy puzzles this year. Because we don't need to calculate neighbors (or the empty space), we can store the grid as `set` of `Point`s (which is in turn a `Tuple[int, int]`). This makes it fast to iterate and, when we re-add a point to the grid (when it folds onto itself), it doesn't create a duplicate entry. Let's do some parsing!

```py
from typing import Tuple, Set, cast, List

Point = Tuple[int, int]
Grid = Set[Point]

# there's only one empty line, so that's the divider
break_index = self.input.index("")
dots: Grid = {
    cast(Point, tuple(map(int, s.split(",")))) for s in self.input[:break_index]
}
```

That `dots` is a little dense, but the gist is:

1. split the line by `,`
2. for the 2-item array (`["6", "10"]`), call `int` on each using the `map` function
3. Tell Python that this tuple (which, as far as it knows, could be any length) is a 2-tuple full of its with the `cast` function
4. Wrap that in a `set` comprehension- note that it's wrapped in curly braces, just like a `dict` comprehension. But, there's no `key: value` pattern; it's more like declaring a `set` with `{1, 2, 3}`

Before we get to parsing the fold instructions, I found it helpful to figure out how we were going to use those instructions with our grid. To know we're doing that right, then we should be able to print the grid. It's a pretty standard 2d iteration:

```py
def print_grid(dots: Grid):
    max_x = max(x[0] for x in dots)
    max_y = max(y[1] for y in dots)

    for y in range(max_y + 1):
        for x in range(max_x + 1):
            print("#" if (x, y) in dots else ".", end="")
        print() # newline!
    print() # space after the print
```

Passing the `end` kwarg to `print` lets us skip the regular newline. We also add `1` to the `range` since it stops _before_ the end value otherwise.

Now we're ready to do some folding. Folds happen in two directions, either across a vertical or horizontal line. In each mode, only one of the values (`x` or `y`) will change; the other stays the same. So we'll be creating a new set, adding half of the points as is (the left or top halves depending on direction) and a modified version of the other half. For the points that we're modifying, I made variables to note which index in the `Point` tuple is changing. That way, it works no matter which direction the fold is. Here's how that looks:

```py
def fold_grid(dots: Grid, horiz: bool, val: int) -> Grid:
    result: Grid = set()
    modified_index, same_index = (1, 0) if horiz else (0, 1)

    for p in dots:
        # if being folded onto, no change
        if p[modified_index] < val:
            result.add(p)
            continue

        updated_point = [-1, -1]
        # one half of the points is unmodified
        updated_point[same_index] = p[same_index]

        # the other half changes based on its distance to the line
        updated_point[modified_index] = 2 * val - p[modified_index]

        result.add(cast(Point, tuple(updated_point)))

    return result
```

In the half that's being folded _onto_, nothing changes. We add those to the result and `continue`. Then, the index that's not changing (eg the horizontal value in a vertical fold) is copied over. Last is the index that _does_ change, which loses its distance to the fold line twice (eg. 14 -> 7 and then 7 -> 0 in the example).

We can fold our grid and see the result. All that's left is to be able to parse the fold instructions. The odd shape lends itself well to Regular Expressions (aka regex). This is a specially structured string that looks for patterns in other strings. It's a super powerful feature found in most programming languages.

In our case, we're looking for:

1. the letter `x` or the letter `y`
2. followed by an `=`
3. followed by a number of any length

In regex, that's: `(x|y)=(\d+)`. The parens denote capture groups, or the specific parts of a match we're interested in. `x|y` means `x or y`. `=` means give us literally that character. `\d` means a digit and `+` is "of 1+ length", which is what we want! You can see an interactive demo of this on [regex101](https://regex101.com/r/7vriRA/1). Here's the Python function:

```py
import re

def parse_folds(folds: List[str]) -> List[Tuple[bool, int]]:
    result: List[Tuple[bool, int]] = []
    for fold in folds:
        fold_desc = re.search(r"(x|y)=(\d+)", fold)
        assert fold_desc
        result.append((fold_desc.group(1) == "y", int(fold_desc.group(2))))

    return result
```

The result of a regex search in Python is either a match object (if it finds) or `None` if it doesn't. Since we know our input is well-formatted and this will always work, we can use `assert` to tell any type-checking tools (and Python itself) that "We promise we'll find something - error if we don't!".

Each capture group is accessed with `.group()`, 1-indexed. So our fold result is the tuple `(True, 7)` for `fold along y=7`. A list of those describes all our folds.

Finally, we've got all the pieces we need to do part 1! Here is the whole thing:

```py
break_index = self.input.index("")
dots: Grid = {
   cast(Point, tuple(map(int, s.split(",")))) for s in self.input[:break_index]
}
folds = parse_folds(self.input[break_index + 1 :])

dots = fold_grid(dots, *folds[0])
return len(dots)
```

## Part 2

And, now we have to do the rest. Luckily, we've got all we need already!

```py
dots = fold_grid(dots, *folds[0])
size_after_first_fold = len(dots)

for fold_ins in folds[1:]:
   dots = fold_grid(dots, *fold_ins)

print()
print_grid(dots)

return size_after_first_fold, "look at the ascii art"
```

This is the rare example where we can't (conveniently) parse out the answer in the code. So we'll just tell the human reader to interpret it for themselves. :boom:
