---
year: 2021
day: 25
title: "Sea Cucumber"
slug: "2021/day/25"
pub_date: "2022-03-03"
---

## Part 1

This one has a couple of corner cases, but on the whole, it's not too bad. As always, we parse the grid. Like previous days, our grid is sparse- we only store keys if they're not a `.`. We can also reverse it and have a little printing function for debugging:

```py
class Solution:
    ...

    def parse_grid(self) -> Grid:
        grid: Grid = {}
        row = col = 0
        for row, line in enumerate(self.input):
            for col, c in enumerate(line):
                if c == ".":
                    continue
                grid[row, col] = c

        self.max_row = row + 1
        self.max_col = col + 1
        return grid

    def print_grid(self, grid: Grid):
        for row in range(self.max_row):
            for col in range(self.max_col):
                print(grid.get((row, col), "."), end="")
            print()
```

Now, the steps. Each time we step, we have to calculate all the moves for the `>` cucumbers first. They can move if the place they're about to move is empty:

```py
for i in range(999):
    next_grid: Grid = {}
    for (row, col), c in grid.items():
        if c == ">":
            new_col = (col + 1) % self.max_col
            new_point = (row, new_col)

            if new_point not in grid:
                next_grid[row, new_col] = c
            else:
                next_grid[row, col] = c
```

Next, we do the same thing for the `v` characters:

```py
for i in range(999):
    next_grid: Grid = {}
    ...

    for (row, col), c in grid.items():
        if c == "v":
            new_row = (row + 1) % self.max_row
            new_point = (new_row, col)

            # 1. check that no one moved into it
            # 2. check that the old resident isn't a v
            can_move = new_point not in next_grid and grid.get(new_point) != "v"

            if can_move:
                next_grid[new_point] = c
            else:
                next_grid[row, col] = c
```

This second block is quite similar to the first- the big difference is check about whether or not the character can move. We have to check that the place we want to move wasn't just filled by a `>` or a `v` that will move (but not in time for this one).

After that, we just check if our new grid has changed from our old grid:

```py
if grid == next_grid:
    return i + 1

grid = next_grid
```

And that'll do it! We have some cleanup you can do if you'd like, but otherwise, you can take the W and be done!

### Cleanup

I liked my solution well enough, but I didn't love the fact that I basically wrote the same block twice, but not in a function. We have a couple of variables to account for:

1. the location of the new point (do we increment the `row` or the `column`)
2. whether or not the cucumber can move

One of those is easy to account for- we can write a little function to get our `new_point`:

```py
class Solution:
    ...

    def new_point(self, row: int, col: int, c: str) -> Tuple[int, int]:
        if c == ">":
            col = (col + 1) % self.max_col
        if c == "v":
            row = (row + 1) % self.max_row

        return row, col
```

Now we can build most of our `step` function:

```py
for i in range(999):
    # pylint: disable=cell-var-from-loop
    next_grid: Grid = {}

    def step(mode: str, can_move: Callable[[GridPoint], bool]):
        for (row, col), c in grid.items():
            if c != mode:
                continue
            new_point = self.new_point(row, col, c)

            can_move = ... # TODO

            if can_move:
                next_grid[new_point] = c
            else:
                next_grid[row, col] = c

    step(">")
    step("v")

    if grid == next_grid:
        return i + 1
```

Unfortunately, our `can_move` conditions are a little more involved. We need to calculate them for each point in the `step` function. We could do something like:

```py
if mode == '>':
    can_move = new_point not in grid
else:
    can_move = new_point not in next_grid and grid.get(new_point) != "v"
```

But, that makes our `step` function more context-aware. It would be nice if it were "dumb", and took all its configuration via arguments. So, let's parameterize those functions!

```py
...

def step(mode: str, can_move: Callable[[GridPoint], bool]):
    ...

    if can_move(new_point):
        next_grid[new_point] = c
    else:
        next_grid[row, col] = c

step(">", lambda new_point: new_point not in grid)
step(
    "v",
    lambda new_point: new_point not in next_grid
    and grid.get(new_point) != "v",
)
```

Now we pre-define the function that decides whether our cucumber can move, and we call it and act accordingly. Doing inline lambda functions like that is playing a little fast-and-loose with variable scopes here, but it works! And I kind of like it, so we're going to call it good.

## Part 2

Nothing extra needed here! If you've followed the rest of [the guides](https://github.com/xavdid/advent-of-code/tree/main/solutions/2021) and got all your stars, just click the button and you're all set.

Congrats on completing Advent of Code 2021!
