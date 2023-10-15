---
year: 2022
day: 8
title: "Treetop Tree House"
slug: "2022/day/8"
pub_date: "2022-12-08"
---

## Part 1

Ah, the fabled AoC grid. There are usually a number of grid-based puzzles. This one _seems_ complex, but really, a bit of organization and a lot of iterating will get us there without too much trouble.

First, we parse the grid. We'll be using a pretty standard 2-D list (aka `row, col`) system, where `0, 0` is in the top left. `row` increases down, and `col` increases right:

```
0  col -> 4

r  .....
o  .....
w  .....
|  .....
V  .....
4
```

Here's the parsed sample:

```py
[[3, 0, 3, 7, 3],
 [2, 5, 5, 1, 2],
 [6, 5, 3, 3, 2],
 [3, 3, 5, 4, 9],
 [3, 5, 3, 9, 0]]
```

The first row of interior trees we'll be considering (`5`, `5`, and `1`) are at coordinates `(1,1)`, `(1,2)`, and `(1,3)`.

Parsing the grid is a nested list comprehension, but nothing too unusual:

```py
class Solution(StrSplitSolution):
    def parse_grid(self) -> int:
        self.grid = [[int(i) for i in row] for row in self.input]
        assert len(self.grid) == len(self.grid[0]), "not a square grid"
        return len(self.grid)
```

We assert that the grid is square, since we'll make some important assumptions based on that soon.

Now we can take a step back and consider how we'll be solving the problem. We'll need to iterate over all of the inner trees, totaling up which return `True` from an `is_visible` function which we'll write in a minute).

Our outermost loop looks like this:

```py
class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        grid_size = self.parse_grid()

        # the size of the border
        # the size of the top+bottom rows, plus the size of the
        # L and R columns - 2 (their overlap with the top and bottom)
        num_visible_trees = grid_size * 2 + (grid_size - 2) * 2

        for row in range(1, grid_size - 1):
            for col in range(1, grid_size - 1):
                if self.grid[row][col] == 0:
                    continue  # 0s are never visible
                num_visible_trees += self.is_visible(row, col)

        return num_visible_trees
```

We start with an initial value, then iterate all interior grid and sum up whichever are visible. We're once again relying on `bool`s being secret `int`s, so we can add them without extra conditionals.

Now, the visibility calculation. I did this as 4 functions, each starting at a point and iterating in a cardinal direction until they hit the edge of the grid:

```py
class Solution(StrSplitSolution):
    ...

    def is_visible_from_above(self, row: int, col: int) -> bool:
        for look_row in range(row - 1, -1, -1):
            if self.grid[look_row][col] >= self.grid[row][col]:
                return False
        return True

    def is_visible_from_below(self, row: int, col: int) -> bool:
        for look_row in range(row + 1, len(self.grid)):
            if self.grid[look_row][col] >= self.grid[row][col]:
                return False
        return True

    def is_visible_from_left(self, row: int, col: int) -> bool:
        for other_tree in self.grid[row][:col]:
            if other_tree >= self.grid[row][col]:
                return False
        return True

    def is_visible_from_right(self, row: int, col: int) -> bool:
        for other_tree in self.grid[row][col + 1 :]:
            if other_tree >= self.grid[row][col]:
                return False
        return True
```

There's not much to these. The important things are:

- return as soon as we've found a blocker
- do your `range` calculations carefully

I'll look into cleaning these up at the end, but for now, they work nicely.

Last thing is a function to wrap them all:

```py
class Solution(StrSplitSolution):
    ...

    def is_visible(self, row: int, col: int) -> bool:
        return (
            self.is_visible_from_above(row, col)
            or self.is_visible_from_right(row, col)
            or self.is_visible_from_below(row, col)
            or self.is_visible_from_left(row, col)
        )
```

Onwards!

## Part 2

We've actually done a lot of the work here already. We know at what distance our blocking tree is- it's where the iterator stopped! So we need to capture the index of where we stop iterating, a job for `enumerate`. We'll be making the same changes to each of the 4 directional function, so for brevity, I'll just show the one:

```py
class Solution(StrSplitSolution):
    ...

    def is_visible_from_left(self, row: int, col: int) -> Tuple[bool, int]:
        # initialize i
        i = -100
        # add `i` and `enumerate`
        for i, other_tree in enumerate(reversed(self.grid[row][:col])):
            if other_tree >= self.grid[row][col]:
                # return both the bool and `i` in both cases
                return False, i
        # return both the bool and `i` in both cases
        return True, i
```

Nothing too unusual here. Also note that I picked `left` to highlight because it had a bug that only mattered in part 2. Originally, we were iterating `self.grid[row][:col]`, which was the right bounds but the _wrong_ direction. That didn't matter before- we were iterating more than we needed to, but the length we iterated didn't matter. Now that it does, we drop a `reversed` in and it's all good.[^1]

That new return type in hand, we need to plumb that through our other functions:

```py
class Solution(StrSplitSolution):
    ...

    def is_visible(self, row: int, col: int) -> Tuple[bool, int]:
        is_visible = False
        result = 1
        for func in (
            self.is_visible_from_above,
            self.is_visible_from_right,
            self.is_visible_from_below,
            self.is_visible_from_left,
        ):
            visible, dist = func(row, col)
            is_visible = is_visible or visible
            result *= dist + 1 # because it's a distance, minimum 1

        return is_visible, result

    def solve(self) -> Tuple[int, int]:
        grid_size = self.parse_grid()

        # the size of the border
        num_visible_trees = grid_size * 2 + (grid_size - 2) * 2

        best_view = 0

        for row in range(1, grid_size - 1):
            for col in range(1, grid_size - 1):
                if self.grid[row][col] == 0:
                    continue  # 0s are never visible and never the best tree
                visible, view_score = self.is_visible(row, col)
                num_visible_trees += visible
                best_view = max(best_view, view_score)

        return num_visible_trees, best_view
```

Nothing to fancy to wrap up our 8th day.

[^1]: This would also work with a reverse slice, but I was having trouble making that work the way I want, so I just went with the easier thing.
