---
year: 2024
day: 12
slug: "2024/day/12"
title: "Garden Groups"
# concepts: []
pub_date: "2024-12-23"
---

## Part 1

I split my solution today into two separate phases: parsing out the regions and then calculating their prices.

Parsing is pretty straightforward. We can use my grid parser (see days: [4](/writeups/2024/day/4), [6](/writeups/2024/day/6), [8](/writeups/2024/day/8), or [10](/writeups/2024/day/10); I'm sensing a pattern...) and a simple DFS (see [day 10](/writeups/2024/day/10)). We run the DFS for each point in the grid, skipping any that have already been seen in a region. Here's what that looks like:

```py
from ...utils.graphs import parse_grid, neighbors

type GridPoint = tuple[int, int]

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input)
        regions: list[set[GridPoint]] = []

        # every plant should show up in exactly one set so we track them globally
        all_points: set[GridPoint] = set()

        for point in grid:
            if point in all_points:
                continue

            # now we're standing on a new region
            region = set()

            queue = [point]
            while queue:
                cur = queue.pop()
                if cur in region:
                    continue

                region.add(cur)

                for n in neighbors(cur, num_directions=4):
                    if grid.get(n) != grid[cur]:
                        continue
                    queue.append(n)

            all_points |= region
            regions.append(region)
```

This is a lot like the bits we've seen before, so I'll mostly let it speak for itself. But, there's one cool trick- instead of writing `all_points = all_points | region` to track any point in either set, we use `|=`. It's the equivalent of `+=` or `*=`, but uses the pipe (`|`) instead. It's one of those things where of course it works, but people never think to try it!

Next up is the perimeter calculation. Let's start with the simplest case: the solitary `D`. It's got 4 sides and 4 neighbors who don't match it, so it has a perimeter of 4. The next smallest is the horizontal line of `E`s. The outermost `E`s each have a perimeter of 3 since 3 of their sides are exterior and 1 is shared with the middle `E`. It contributes 2 to the perimeter, since it has 2 matching neighbors.

Following this trend, we can say that each point contributes `4 - num_matching_neighbors` to its region's perimeter. We've got all the regions separated out already, so this is straightforward to code:

```py
class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        total = 0
        for region in regions:
            perimeter = 0
            for p in region:
                num_matching_neighbors = len(
                    [
                        n
                        for n in neighbors(p, num_directions=4)
                        if grid[p] == grid.get(n)
                    ]
                )
                perimeter += 4 - num_matching_neighbors

            total += perimeter * len(region)

        return total
```

This code works and gets us our answer, but there's still some cleanup we can do. If you're happy with what we wrote, skip down to [Part 2](#part-2). Otherwise, read on!

### Cleanup

The biggest thing is that we're reusing our code that counts neighbors. Let's move that into a function that can access the `grid`:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        def matching_neighbors(point: GridPoint):
            for n in neighbors(point, num_directions=4):
                if grid.get(n) == grid[point]:
                    yield n
```

Now we can replace our use of neighbors in the DFS:

```py rem={13-15} ins={16}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for point in grid:
            ...

            while queue:
                ...

                for n in neighbors(cur, num_directions=4):
                    if grid.get(n) != grid[cur]:
                        continue
                for n in matching_neighbors(cur):
                    queue.append(n)
```

But we can do even better! Because we're adding every item from an iterable into a new iterable, we can use `list.extend()`:

```py rem={13,14} ins={15}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        for point in grid:
            ...

            while queue:
                ...

                for n in matching_neighbors(cur):
                    queue.append(n)
                queue.extend(matching_neighbors(cur))
```

Next, we can simplify the perimeter calculation. Most of the time you write a `for` loop with a single calculation that modifies a variable right outside the loop, you can safely rewrite that as a comprehension of some kind. In our cae, we want to sum 4 minus the the number of matching neighbors of each point in a region. It's a _little_ dense, but it can be written as:

```py rem={9-18} ins={19}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        total = 0
        for region in regions:
            perimeter = 0
            for p in region:
                num_matching_neighbors = len(
                    [
                        n
                        for n in neighbors(p, num_directions=4)
                        if grid[p] == grid.get(n)
                    ]
                )
                perimeter += 4 - num_matching_neighbors
            perimeter = sum(4 - len(list(matching_neighbors(p))) for p in region)
            total += perimeter * len(region)

        return total
```

If we _really_ wanted to, we could shrink it once more:

```py
return sum(
    sum(4 - len(list(matching_neighbors(p))) for p in region) * len(region)
    for region in regions
)
```

But that gets a little hard to read for my taste.

Lastly, we can actually shrink one more thing: our `matching_neighbors` function! We've got a `for` loop and a conditional. We can combine them both (once again) into a comprehension and use `yield from` to use that as our generator directly:

```py rem={8-10} ins={11-15}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        def matching_neighbors(point: GridPoint):
            for n in neighbors(point, num_directions=4):
                if grid.get(n) == grid[point]:
                    yield n
            yield from (
                n
                for n in neighbors(point, num_directions=4)
                if grid.get(n) == grid[point]
            )
```

If we want, we can shrink it once more via the `filter` function (which also returns an iterable):

```py rem={8-12} ins={13-15}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        def matching_neighbors(point: GridPoint):
            yield from (
                n
                for n in neighbors(point, num_directions=4)
                if grid.get(n) == grid[point]
            )
            yield from filter(
                lambda n: grid.get(n) == grid[point], neighbors(point, num_directions=4)
            )
```

It's sort of a "6 one way, half dozen the other", but I like not having to write `n for n in ...` unnecessarily.

Anyway, iterating like this is a great way to improve our design with small steps! We end up in a much better place overall.

## Part 2

I finished part 1 days ago but have been spinning my wheels while I overthink part 2. Finding sides _sounds_ like it should be just like finding the perimeter. But, I kept getting caught up in how I'd need to group points to build (and deduplicate) sides.

To unblock myself, I found some hints on the subreddit. The most important one was that we can count corners as a proxy for sides. Every side has 2 corners and every corner connects 2 sides. So, how do we determine if a given point is a corner?

A corner is formed by a point with two neighbors outside its region(in an `L` shape). Thus, each of these `A`s is a corner (I've numbered their exterior `L` shaped pairs of neighbors):

```
.12.
1AA2
4AA3
.43.
```

A point can also have multiple exterior corners if it has multiple pairs of `L`-shaped exterior neighbors:

```
.½.
1A2
3A4
.¾.
```

These are "exterior" corners, which are the kind you'd expect from learning your shapes. But, there are also "interior" corners, like you'd find in a `+` shape:

```
BAAB
AAAA
AAAA
BAAB
```

Here are the 4 interior corners of the `A` region as digits:

```
BAAB
A12A
A43A
BAAB
```

Interior corners are sort of the inverse of the exterior ones. They have 2 neighbors in an `L` shape who _are_ in the region, but the point between those neighbors (diagonal from the original point) is not in-region (labeled `B` above).

Now that we know how to identify corners (and we know that the number of corners is equal to the number of sides), then all that remains is to write the code!

Like part 1, we'll iterate through each region in turn, so we can adapt our `part_1` to a both-parts `solve` and re-use our loop. We'll also be looking at each point, so we'll unroll a bit of our part 1 code:

```py rem={4,9,16,22,26} ins={5,10-11,14,17-18,23,24,27}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        # region parsing
        ...

        total = 0 # renamed
        perimeter_price = 0
        side_price = 0
        for region in regions:
            perimeter = 0
            num_corners = 0

            perimeter = sum(4 - len(list(matching_neighbors(p))) for p in region)
            for point in region:
                perimeter += 4 - len(list(matching_neighbors(point))) # only 1 point now

                # TODO: part 2

            total += perimeter * len(region)
            perimeter_price += perimeter * len(region)
            side_price += perimeter * len(region)

        return total
        return perimeter_price, side_price
```

We haven't added any net new code yet, but we're ready to. And part 1 still works, which is always an important part of any refactor.

So. For each point, we need to check its `L` neighbors in each direction. Each point has 4 such pairs of these neighbors: the product of +1/-1 on the row and +1/-1 on the column. `itertools.product` does this nicely:

```py
from itertools import product

list(product([1,-1],repeat=2))
# => [(1, 1), (1, -1), (-1, 1), (-1, -1)]
```

For each point, it's an exterior corner if neither neighbor is in the region. It's an interior corner if both neighbors are in, but their combined offset (the diagonal) is out:

```py ins={19-36}
from itertools import product
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        ...

        perimeter_price = 0
        side_price = 0
        for region in regions:
            perimeter = 0
            num_corners = 0

            for point in region:
                # part 1
                perimeter += 4 - len(list(matching_neighbors(point)))

                # part 2
                row, col = point

                for row_offset, col_offset in product([1, -1], repeat=2):
                    row_neighbor = (row + row_offset, col)
                    col_neighbor = (row, col + col_offset)
                    diagonal_neighbor = (row + row_offset, col + col_offset)

                    # exterior corners
                    if row_neighbor not in region and col_neighbor not in region:
                        num_corners += 1

                    # interior corners
                    if (
                        row_neighbor in region
                        and col_neighbor in region
                        and diagonal_neighbor not in region
                    ):
                        num_corners += 1

            perimeter_price += perimeter * len(region)
            side_price += num_corners * len(region)

        return perimeter_price, side_price
```

Not too bad once we figured out how to find corners. It's a good lesson to myself- don't overthink it!
