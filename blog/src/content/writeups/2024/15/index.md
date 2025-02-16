---
year: 2024
day: 15
slug: "2024/day/15"
title: "Warehouse Woes"
# concepts: []
pub_date: "2025-02-15"
---

## Part 1

Another day, another grid. I'm still using my grid parsing helper (discussed most recently on [day 12](/writeups/2024/day/12/)). It lets us ignore specific characters, so we can skip parsing our walls. We also parse out our `moves`, taking care to treat that second block as one long line instead of a series of lines:

```py
from ...utils.graphs import parse_grid

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        grid = parse_grid(self.input[0].splitlines(), ignore_chars="#")
        moves = self.input[1].replace("\n", "")

        loc = next(k for k, v in grid.items() if v == "@")
```

I knew the tricky part today would be dealing with the boxes, so I opted to start in the simple case: moving through empty space and not walking into walls. We move 4 directions, so there are 4 offsets. Each time we move, the place we're going becomes a `@` and the spot we're leaving becomes a `.`. That code is straightforward:

```py
from ...utils.graphs import add_points, parse_grid

OFFSETS = {
    "<": (0, -1),
    ">": (0, 1),
    "^": (-1, 0),
    "v": (1, 0),
}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for move in moves:
            offset = OFFSETS[move]
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc
```

This works, but we're blowing through our `O` boxes. We can still move onto those spaces, but we have to move the boxes in response. The simplest case is where there's a single box and an empty space behind it. In that case, the empty space becomes a box, the old box is where we land and the space we leave becomes empty:

```py ins={12-17}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for move in moves:
            offset = OFFSETS[move]
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            if grid[next_loc] == "O":
                next_block = next_loc
                if grid.get(next_block := add_points(next_block, offset)) == ".":
                    grid[next_block] = "O"
                else:
                    continue

            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc
```

Because we're checking that the place we're landing is clear, this code already handles trying to move a box into a wall. It also signals to the code that moves _us_ that, since we're unable to move the box, we're unable to take the step we were planning on.

Of course, there's not always a single block; sometimes there's a chain of them! So instead of a single `if` to check the space behind the box, we want to keep walking in that direction until we hit a space or a wall:

```py rem={12} ins={13-14,16}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for move in moves:
            ...

            if grid[next_loc] == "O":
                next_block = next_loc
                if grid.get(next_block := add_points(next_block, offset)) == ".":
                while grid.get(next_block) == "O":
                    next_block = add_points(next_block, offset)

                if grid.get(next_block) == ".":
                    grid[next_block] = "O"
                else:
                    continue
```

Intriguingly, we didn't have to change anything to shift all the boxes instead of a "line" of 1. That's because we don't actually have to move every box! The next result of shifting a whole line of boxes is there's one fewer in the front and one more in the back. For example:

```
.ABC.
```

Can be pushed by swapping `A` to the back:

```
..BCA
```

`B` and `C` never have to move at all! So no matter the line length, we can always push a row of boxes with a single swap (assuming there's space). A great example of "work smarter, not harder".

Once we've gone through all our moves, we can iterate over the boxes to return the total. Our `row, col` grid formation here makes this simple:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        return sum(100 * row + col for (row, col), c in grid.items() if c == "O")
```

## Part 2

Part 2 is the same basic idea, but our grid is double wide nwo. This has the unfortunate side effect of complicating our push operations, since we have to make sure both halves of the boxes stay together.

One approach would be to treat boxes as objects (that can't be split) instead of individual characters, but I sort of liked the exercise of defining each operation carefully. Let's do it!

First, we update our grid parsing. The easiest place to do this is while it's still a string, since `parse_grid` will still handle it correctly:

```py rem={4,6} ins={5,7-14}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def part_2(self) -> int:
        grid = parse_grid(self.input[0].splitlines(), ignore_chars="#")
        raw_wide_grid = [
            s.replace(".", "..")
            .replace("#", "##")
            .replace("@", "@.")
            .replace("O", "[]")
            for s in self.input[0].splitlines()
        ]
        grid = parse_grid(raw_wide_grid, ignore_chars="#")
```

<!-- italic code looks weird, so make the blockquote manually -->
<blockquote style="font-style: normal">

Aside: **Printing the grid**

Being able to easily see the state of the world while working was an especially important tool today. Here's my grid printing function (which is relegated to an "aside", since it's not part of the actual solution):

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        num_rows = len(raw_wide_grid)
        num_cols = len(raw_wide_grid[0])
        def print_grid():
            print("\n   ", end="")
            for cc in range(num_cols):
                print(f"{str(cc)[0] if cc >= 10 else '0'}", end="")
            print()
            print("   ", end="")
            for cc in range(num_cols):
                print(f"{str(cc)[-1]}", end="")
            print()
            for r in range(num_rows):
                print(f"{r:02} ", end="")
                for c in range(num_cols):
                    print(grid.get((r, c), "#"), end="")
                print()
            print()
```

Which shows our example grid with grid markers:

```
   00000000001111111111
   01234567890123456789
00 ####################
01 ##....[]....[]..[]##
02 ##............[]..##
03 ##..[][]....[]..[]##
04 ##....[]@.....[]..##
05 ##[]##....[]......##
06 ##[]....[]....[]..##
07 ##..[][]..[]..[][]##
08 ##........[]......##
09 ####################
```

</blockquote>

Now, actually moving. We can keep all of the part 1 code besides the box moving portion:

```py rem={17,18} ins={19-23}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        loc = next(k for k, v in grid.items() if v == "@")
        moves = self.input[1].replace("\n", "")

        for move in moves:
            offset = OFFSETS[move]
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            if grid[next_loc] == "O":
                ...
            if grid[next_loc] in "[]":
                if move in "v^":
                    # TODO
                else:
                    # TODO

            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc
```

Of course, those todo blocks are where the trick is. Let's start with the simpler of the two: moving horizontally.

While we could swap the first and last characters in part 1, that won't work for part 2:

```
.[][].
..][][
```

So we _will_ have to shift every character over by one. We'll walk horizontally, collecting points until we hit a wall or a space (just like before):

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        for move in moves:
            if grid[next_loc] in "[]":
                if move in "v^":
                    # TODO
                else:
                    target_loc = next_loc
                    blocks = [target_loc]
                    while grid.get(target_loc, "x") in "[]":
                        target_loc = add_points(target_loc, offset)
                        blocks.append(target_loc)
```

> I wrote `grid.get(target_loc, "x")` because `'' in '[]'` always evaluates to `True`; that was a fun bug.

If we stopped because there's a space, we know the operation will succeed. To "push" the blocks, we swap each bracket for its opposite half and replace the open space at the end of the line with the opposite of the first block. You can verify that approach against this example:

```
.[][].
..[][]
```

The code is straightforward:

```py
...

SWAPS = {
    "[": "]",
    "]": "[",
}

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        for move in moves:
            if grid[next_loc] in "[]":
                if move in "v^":
                    # TODO
                else:
                    ...

                    if grid.get(target_loc) == ".":
                        grid[target_loc] = SWAPS[grid[blocks[0]]]
                        for b in blocks[:-1]:
                            grid[b] = SWAPS[grid[b]]
                    else:
                        continue
```

That's the simple half covered. Now let's look at moving vertically.

We can't "push" items in a single column anymore, since our moves will affect _at least_ 2 columns (the width of a box). Let's start with the simplest case:

```
....
.[].
.@..
....
```

To push this successfully, we need to shift both the `[` directly and the `]` by association. We know the location of the `[` and can find its neighbor based on the direction it's facing (and some new keys in `OFFSETS`):

```py ins={5,6,18-21}
...

OFFSETS = {
    # ...
    "[": (0, 1),
    "]": (0, -1),
}

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        for move in moves:
            if grid[next_loc] in "[]":
                if move in "v^":
                    points_to_move = [
                        next_loc,
                        add_points(next_loc, OFFSETS[grid[next_loc]])
                    ]
                else:
                    ... # above
```

Once we know those points, we can check each of the spaces we'd try to move into and bail if they're not all available:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        for move in moves:
            if grid[next_loc] in "[]":
                if move in "v^":
                    ...

                    if all(
                        grid.get(add_points(p, offset)) == "." for p in points_to_move
                    ):
                        for p in points_to_move:
                            dest = add_points(p, offset)
                            grid[dest] = grid[p]
                            grid[p] = "."
```

This works great when we're only pushing a single box, but we have to account for additional rows of boxes. Here's a slightly more complex example:

```
....
..[]
.[].
.@..
```

We need to:

1. find the box we're pushing directly
2. find it's pair
3. for each of those boxes, find any box parts they'd bump into. If none, goto 6
4. find their pairs
5. if we found any boxes, goto 3
6. if the way is clear, bump every box part by one row

So we'll need a loop and a slightly different way to store our boxes. Each row is assessed separately, so a list of list of boxes will help us keep everything straight:

```py rem={12-15,49-51} ins={16-23,24-46,52-55}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        for move in moves:
            if grid[next_loc] in "[]":
                if move in "v^":
                    points_to_move = [
                        next_loc,
                        add_points(next_loc, OFFSETS[grid[next_loc]])
                    ]
                    can_move = True
                    rows: list[list[GridPoint]] = [
                        [
                            # step 1
                            next_loc,
                            # step 2
                            add_points(next_loc, OFFSETS[grid[next_loc]])
                        ]
                    ]
                    while True:
                        # step 3
                        next_row = {add_points(offset, p) for p in rows[-1]}

                        # step 4
                        next_row |= {
                            add_points(p, OFFSETS[grid[p]])
                            for p in next_row
                            if grid.get(p, "x") in "[]"
                        }

                        # check for blockages
                        if any(p not in grid for p in next_row):
                            can_move = False
                            break

                        # step 5
                        if next_boxes := [p for p in next_row if grid[p] in "[]"]:
                            # loop with new farthest row of boxes
                            rows.append(next_boxes)
                        else:
                            break

                    # step 6
                    if all(
                        grid.get(add_points(p, offset)) == "." for p in points_to_move
                    ):
                    if not can_move:
                        continue
                    # move boxes from farthest to closest
                    for row in reversed(rows):
                        for p in row:
                            dest = add_points(p, offset)
                            grid[dest] = grid[p]
                            grid[p] = "."
```

Our bottom code got slightly more simple since if we could move, we know there's nothing blocking us. Past that, we're adding new rows, finding anything they can touch, and sliding everything by a row. Nothing too complex!

Lastly, we tweak our result calculation slightly:

```py rem={9} ins={10}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        return sum(100 * row + col for (row, col), c in grid.items() if c == "O")
        return sum(100 * row + col for (row, col), c in grid.items() if c == "[")
```
