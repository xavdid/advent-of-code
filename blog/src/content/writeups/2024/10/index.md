---
year: 2024
day: 10
slug: "2024/day/10"
title: "Hoof It"
# concepts: [dfs]
pub_date: "2024-12-13"
---

## Part 1

Today's task is pathfinding, a well-studied area of computer science. The goal is to count the number of unique `9`s we can reach from a given `0`. There are many approaches, but the simplest is a basic [depth-first-search](https://en.wikipedia.org/wiki/Depth-first_search). If we're not worried about a shortest path, the steps are simple:

1. pick a starting point and put it in a list
2. while there's a queue, pop the last value off the list; this is your current location
3. if you've visited it before, GOTO 2
4. mark the point as visited
5. if it's your destination, increment the counter and continue
6. otherwise, add all valid destinations from your current location to the queue
7. GOTO 2

Eventually you'll stop adding new things to the queue and it'll empty, exiting the loop.

DFS is usually used in conjunction with [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) to find the shortest path between two points, but we're not concerned with length- just that we can eventually reach a `9` after starting on a `0`.

So, let's code that up. Since we'll be starting from a bunch of trailheads, lets wrap the whole thing in a function:

```py
type GridPoint = tuple[int, int]
type IntGrid = dict[GridPoint, int]

def score_trailhead(grid: IntGrid, trailhead: GridPoint) -> int:
    score = 0
    visited: set[GridPoint] = set()

    queue: list[GridPoint] = [trailhead] # 1

    while queue: # 2
        cur = queue.pop() # 2

        if cur in visited: # 3
            continue

        visited.add(cur) # 4

        if (val := grid[cur]) == 9: # 5
            score += 1
            continue

        queue.extend( # 6
            n for n in neighbors(cur, num_directions=4) if grid.get(n) == val + 1
        )
        # 7 - now we loop

    return score
```

For this puzzle, valid moves are neighbors whose value is exactly 1 more than the current location. My `neighbors` helper is doing most of the heavy lifting. It's responsible for finding orthogonal neighbors for a given point. For more background, check out my writeup for [day 4](/writeups/2024/day/4/).

Tracking our `visited` positions is important because we never want to double land on a point. If we do, we'll end up double-counting destinations points. Once we hit a given point, we'll eventually make our way to all the `9`s it can reach. So if we'd ever hit it again, we skip it and don't re-queue its neighbors.

Next, we actually have to parse the grid. Luckily, I've got another helper for that! The actual visiting is straightforward too, since a comprehension can help us find all the positions whose value is `0`:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, int_vals=True)

        return sum(
            score_trailhead(grid, trailhead)
            for trailhead, v in grid.items()
            if v == 0
        )
```

## Part 2

Now we _do_ want to double count our destinations, so we'll need to tweak our scoring function slightly.

On an undirected graph (where you can move freely between any two neighbors) you _always_ have to track your `visited` points because you'l get stuck in a loop otherwise (moving from `A` to `B` to `A` to...). But, because the value must strictly increase, we'll never move back to a place we've been.

As a result, every time we access a point, we must have taken a unique path to get there. Since we're counting unique paths, this is very convenient! To solve part 2, we just need to tweak our part 1 code to not skip visited points. All we need is an extra arg:

```py rem={3,13} add={4,14}
...

def score_trailhead(grid: IntGrid, trailhead: GridPoint) -> int:
def score_trailhead(grid: IntGrid, trailhead: GridPoint, *, skip_visited: bool) -> int:
    score = 0
    visited: set[GridPoint] = set()

    queue: list[GridPoint] = [trailhead]

    while queue:
        cur = queue.pop()

        if skip_visited:
            if cur in visited:
                continue

            visited.add(cur)

        if (val := grid[cur]) == 9:
            score += 1
            continue

        queue.extend(
            n for n in neighbors(cur, num_directions=4) if grid.get(n) == val + 1
        )

    return score
```

Now, we only add items to (and check) `visited` if we're skipping on duplicates. Otherwise, we continue on our merry way.

Also, note the `*` in the function signature. This tells Python that any arguments that come after it _must_ be specified as keyword args (instead of positional ones). This helps enforce readable code, since it's hard to know what a boolean does on its own. See the difference:

```py
score_trailhead(grid, trailhead, True)
# vs
score_trailhead(grid, trailhead, skip_visited=True)
```

Only in the second case can you guess what the argument at the end does without reading the implementation. As a result, I tend to like this pattern.

Anyway, to wrap up, we call our function twice for each `0` in the grid. We can wrap both parts into a single function:

```py
...

class Solution(StrSplitSolution):
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, int_vals=True)

        # typechecker doesn't realize this will always be the 2-tuple we expect
        return tuple(  # type: ignore
            sum(
                score_trailhead(grid, trailhead, skip_visited=skip_visited)
                for trailhead, v in grid.items()
                if v == 0
            )
            for skip_visited in (True, False)
        )
```

The ordering of `(True, False)` at the end there is important because that's the order of our parts 1 and 2. Everything else should feel fairly familiar.

That's our first double-digit day down!
