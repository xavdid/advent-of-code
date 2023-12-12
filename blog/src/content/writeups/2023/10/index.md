---
year: 2023
day: 10
title: "Pipe Maze"
slug: 2023/day/10
pub_date: "2023-12-11"
---

## Part 1

Welcome to day 10! We're into the double digits!

Since we'll be doing lookups across a 2-D plane, our first order of business is parsing a grid. I've got a util for this because it comes up so much. I parse the grid into a dict where each key is a 2-tuple of `(row, column)` and the value is the character. You can see the whole thing here:

```py
GridPoint = tuple[int, int]
Grid = dict[GridPoint, str]

def parse_grid(raw_grid: list[str]) -> Grid:
    """
    returns 2-tuples of (row, col) with their value

    (0, 0) ------> (0, 9)
      |              |
      |              |
      |              |
      |              |
      |              V
    (9, 0) ------> (9, 9)
    """
    result = {}

    for row, line in enumerate(raw_grid):
        for col, c in enumerate(line):
            result[row, col] = c

    return result
```

These coordinates may feel odd if you're used to a more traditional `(x, y)` grid. But, this approach plays more nicely with Python; I always found it confusing that my `y` needed to get bigger to move lower when we store things in actual 2-D arrays. It also saves me having to do everything in a negative `y` (since, unless we have a defined origin, the grid starts in the top left). In any case, you're welcome to label your points however you like, I don't think it matters much today.

Now, for the puzzle itself. For now, the only thing we care about is location of the single loop. To walk the loop, we _do_ need to parse the whole grid into points. We'll also need to find the starting location. Util function in hand, that's not too bad:

```py
class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input)
        start = next(k for k, v in grid.items() if v == "S")
```

Here, we use `next` to manually advance a generator whose only item will be the location of the `S`.

Now we actually have to walk the loop. But, we don't know which of the 4 neighbors of `S` connects to it. Assuming a well-formed input (which is a safe assumption for AoC), exactly 2 neighbors will have pipes that can connect from that point to `S`. We have to find either of those neighbors. Luckily, this is another task that comes up often enough that I have a util function for it. I won't paste the whole thing here, but you can [read it on GitHub](https://github.com/xavdid/advent-of-code/blob/ae5ce0c2a9d291e5e5d6cea47728b2110858df3d/solutions/utils/graphs.py#L9-L59). The gist is that it takes a center point and can give you the 4, 8, (or 9, including the center) neighbors. It also supports a max array size and ignoring negatives in either dimension.

So, given the location of our `start`, we can find all 4 neighbors. But, without some extra work, we don't know which of those can connect to `start`. Our next task is turning these funny pipe shapes into actual coordinates.

The function we need takes a location and returns the two points you can reach from that spot (based on the pipe shape). We know that the two points will be exactly 1 step from the input location, but their direction depends on the pipe type. My typical approach for problems like this is to return _offsets_, 2-tuples whose elements are only `0`, `1`, or `-1`. By adding the elements of a location and an offset, we get a new location:

```py
def add_points(a: GridPoint, b: GridPoint) -> GridPoint:
    """
    add a pair of 2-tuples together. Useful for calculating a new position from a location and an offset
    """
    return a[0] + b[0], a[1] + b[1]
```

The last thing our function needs is a way to get the offsets for each pipe; that's just a lookup `dict`:

```py
OFFSETS = {
    "|": ((1, 0), (-1, 0)),
    "-": ((0, 1), (0, -1)),
    "L": ((-1, 0), (0, 1)),
    "J": ((-1, 0), (0, -1)),
    "7": ((0, -1), (1, 0)),
    "F": ((0, 1), (1, 0)),
}
```

Putting that all together, we can get the possible moves for a given location:

```py
def possible_moves(current: GridPoint, c: str) -> tuple[GridPoint, GridPoint]:
    res = tuple(add_points(current, o) for o in OFFSETS[c])
    assert len(res) == 2
    return res
```

Which, finally, lets us figure out the valid pipes next to `start`! They'll be the 2 neighbors who list `start` in their possible moves:

```py
def find_start_adjacent(grid: Grid, grid_size: int, start: GridPoint) -> GridPoint:
    result = []
    for neighbor in neighbors(start, 4, max_size=grid_size - 1, ignore_negatives=True):
        if grid[neighbor] == ".":
            continue

        if start in possible_moves(neighbor, grid[neighbor]):
            result.append(neighbor)

    assert (
        len(result) == 2
    ), f"didn't find exactly 2 points that could reach start: {result}"
    return result[0]
```

For each neighbor that isn't empty (`.`), we look at its 2 moves. If either is `start`, `start` must also be able to move to it (despite not knowing `start`'s shape). There should be exactly 2 results, which we validate. We ultimately can return either result, so I went with the first. That's a lot of code, but now we have everything we need to walk the loop!

For each step we'll have 2 possible moves; we need to move to the one we didn't just come from. We'll also need to know the full length of the loop, so keeping track of all the points (in order) is called for. If we'll move to `start`, then we know we've completed the loop and can return! Check it out:

```py ins={7,9,11-14,16,17,19}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        start = next(k for k, v in grid.items() if v == "S")
        points = [start]

        current = find_start_adjacent(grid, len(self.input), start)

        while True:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])

            if (a == start or b == start) and last != start:
                return ceil(len(points) / 2)

            current = a if b == last else b
```

Do you catch our little trick with the `return`? The puzzle wants the farthest point from the start, which will be the halfway point on the loop. We've found the whole loop, so halfway around will be the furthest point!

## Part 2

I sat with this one for a while. The thing I was stuck with was determining which side was the inside. The best approach I came up with was modifying the input (mid program) to build a big wall around the input and do a flood fill to see if I hit a wall. That might have been workable, but I could also imagine a case where that doesn't work at all. Ultimately, I figured there must be a pre-existing formula for finding the space in a weird shape. A quick glance through [the Reddit thread](https://old.reddit.com/r/adventofcode/comments/18evyu9/2023_day_10_solutions/) confirmed it! There's 2 parts; we'll go through each.

First is [Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem), which calculates the area of a shape given the number of interior and exterior points. The number of interior points is our part 2 answer. We know the number of exterior points (the full list of points from part 1). So, we still need the area. That calls for a second formula.

Next up is the [shoelace formula](https://en.wikipedia.org/wiki/Shoelace_formula), which can calculate the area of a shape enclosed by a bunch of points. Luckily for us, we have those! The formula itself is simple:

```py
def interior_area(points: list[GridPoint]) -> float:
    padded_points = [*points, points[0]]  # form pair with last and first
    return (
        sum(
            row1 * col2 - row2 * col1
            for (row1, col1), (row2, col2) in zip(padded_points, padded_points[1:])
        )
        / 2
    )
```

For each pair of points on the boundary of the shape, we add `row1 * col2 - row2 * col1` to a total (and take half of the result). The only other trick is that we need to include the last and first points (in that order), which isn't included in our `zip` call. So, we pad the last with the start so our total is correct.

With the area of our shape, we can plug that into Pick's theorem and solve. The code slots right into the end of our part 1 solution:

```py ins={13,18-19,21-22,24} ins="solve" ins="tuple[int, int]"
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        while True:
            last = points[-1]
            points.append(current)
            a, b = possible_moves(current, grid[current])

            if (a == start or b == start) and last != start:
                farthest_loop_distance = ceil(len(points) / 2)
                break

            current = a if b == last else b

        # shoelace - find the float area in a shape
        area = interior_area(points)

        # pick's theorem - find the number of points in a shape given its area
        num_interior_points = int(abs(area) - 0.5 * len(points) + 1)

        return farthest_loop_distance, num_interior_points
```
