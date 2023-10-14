---
year: 2022
day: 12
title: "Hill Climbing Algorithm"
slug: "2022/day/12"
pub_date: "2022-12-13"
---

## Part 1

One of the best things that AoC does is provide practical awareness about classic CS algorithms. Today's beneficiary is [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm), one of the foremost [shortest path algorithms](https://en.wikipedia.org/wiki/Shortest_path_problem). I've written about it at length in previous years, such as [on 2021 day 15](https://github.com/xavdid/advent-of-code/blob/main/solutions/2021/day_15/README.md), so I'm going to be brief here. I recommend giving day 15 a skim, since it goes into great detail.

But, I don't want to leave you empty handed, so here are the sparknotes.

Dijkstra is all about finding the shortest path across a graph. To implement, you need to track the following:

1. points you've visited (the `seen` set)
2. the shortest distance you've found so far to a given point (a `dict` of `distances`)
3. an always-sorted list of points you've seen (but not visited directly) along with _a_ distance you can reach them via (the `queue`); initialized to `[(0, start)]`

Those in hand, you perform the following steps until the queue is empty or you've found your destination:

1. pop the first point + `distance` pair from the queue
2. if that point is your destination, return `distance`
3. if you've visited that point before, skip
4. add that point to `visited`
5. for each neighbor you can visit:
   1. if that neighbor is in `visited`, skip
   2. calculate the distance it would take to reach the neighbor
   3. if the calculated distance is the shorter than the shortest path to the point so far, update the shortest distance and add the neighbor to the queue

If you're a visual learner, here's a great gif from [Wikimedia](https://commons.wikimedia.org/w/index.php?curid=6282617):

![](../../2021/15/images/animation.gif)

---

That out of the way, let's apply that to today's problem. First, as always, input parsing!

```py
GridPoint = tuple[int, int] # so useful, I actually have it in my base class

class Solution(StrSplitSolution):
    grid: List[List[str]] = []

    def parse_grid(self) -> GridPoint:
        self.grid = [list(l) for l in self.input]
        for row, line in enumerate(self.input):
            if (col := line.find("S")) >= 0:
                return row, col
        raise ValueError("Unable to find start point")
```

Nothing too fancy, but we do have a chance to use the "[walrus operator](https://peps.python.org/pep-0572/)", which combines assignment with a conditional. Basically, it prevents us having to write:

```py
for row, line in enumerate(self.input):
    if line.find("S") >= 0:
        col = line.find("S")
        return row, col
# or
    ...
    col = line.find("S")
    if col >= 0:
        return row, col
```

Anyway, we parse our input into nested lists and return the location of our starting point. Next, we set up our variables as mentioned above:

```py
from collections import defaultdict

...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        start = self.parse_grid()

        visited: set[GridPoint] = set() # thing to track #1
        distances = defaultdict(lambda: 10_000) # thing to track #2
        queue: list[tuple[int, GridPoint]] = [(0, start)] # thing to track #3
```

We're using Python's `defaultdict`, a superbly useful data structure. Instead of ever throwing a `KeyError`, it'll instead call a function you provide. It's most commonly used with a basic data type (as `defaultdict(int)`, since `int()` returns `0`), but can be anything. We're worried about finding minimum distances, so the default, unvisited distance should be bigger than we're ever going to see. Given the size of our input grid (42x84), 10k seemed like plenty.

You'll also notice that our priority queue is just a regular `list`. Python's built-in priority queue is a function that takes (and modifies) a list, so we don't need to do anything fancy to initialize it.

Then, the algorithm itself, annotated with the numbered step from above:

```py
from heapq import heappop, heappush
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...

        while queue:
            # 1
            distance, current = heappop(queue)
            src = self.grid[current[0]][current[1]]

            # 2
            if src == "E":
                return distance

            # 3
            if current in visited:
                continue

            # 4
            visited.add(current)

            # 5.2
            new_distance = distance + 1

            for n in neighbors(
                current,
                4,
                ignore_negatives=True,
                max_x_size=num_rows,
                max_y_size=num_cols,
            ):
                # 5.1
                if n in visited:
                    continue

                if not can_step(src, self.grid[n[0]][n[1]]):
                    continue

                # 5.3
                if new_distance < distances[n]:
                    distances[n] = new_distance
                    heappush(queue, (new_distance, n))

        return -1  # no path found
```

We can take a slight shortcut with step `5.2`- because each step adds exactly 1 to the distance, we can pre-calculate that; usually Dijkstra's is used on a graph with weighted edges (where the cost to visit each neighbor is variable).

I also used two functions that I hadn't already defined because they didn't make sense out of the context. One determines if we can move from a letter to another letter, based on the height rules:

```py
def can_step(src: str, dst: str) -> bool:
    if dst == "E":
        dst = "z"

    if src == "S":
        src = "a"

    return ord(src) + 1 >= ord(dst)
```

The other gives a bunch of neighboring tuples based on a center point. It comes up enough in AoC that I've made a generic version of it:

```py
from itertools import product
from operator import itemgetter

DIRECTIONS = sorted(product((-1, 0, 1), repeat=2), key=itemgetter(1))

def neighbors(
    center: GridPoint,
    num_directions=8,
    *,
    ignore_negatives: bool = False,
    max_x_size: int = 0,
    max_y_size: int = 0,
) -> Iterator[Tuple[int, int]]:
    """
    given a point (2-tuple) it yields each neighboring point.
    Iterates from top left to bottom right, skipping any points as described below:

    * `num_directions`: Can get cardinal directions (4), include diagonals (8), or include self (9)
    * `ignore_negatives`: skips points where either value is less than 0
    * `max_DIM_size`: if specified, skips points where the dimension value is greater than the max grid size in that dimension. If doing a 2D-List based (aka `(row,col)` grid) rather than a pure `(x,y)` grid, the max values should be `len(DIM) - 1`.

    For a 2D list-based grid, neighbors will come out in (row, col) format.
    """
    assert num_directions in {4, 8, 9}

    for dx, dy in DIRECTIONS:
        if num_directions == 4 and dx and dy:
            # diagonal; skip
            continue

        if num_directions != 9 and not (dx or dy):
            # skip self
            continue

        rx = center[0] + dx
        ry = center[1] + dy

        if ignore_negatives and (rx < 0 or ry < 0):
            continue

        if max_x_size and (rx > max_x_size):
            continue

        if max_y_size and (ry > max_y_size):
            continue

        yield (rx, ry)
```

Honestly, the fanciest part is `DIRECTIONS`, which uses a couple of neat tricks to produce the following list:

```py
[(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
```

Namely, it:

- uses `itertools.product` with the `repeat` kwarg to get every pair of 2 numbers from `(-1, 0, 1)`.
- Then it sorts them using the 2nd item of each tuple (and not swapping if it doesn't need to).
- This gives us offsets from top-left to bottom right, read left-to-right and top-to-bottom

Finally, you can see the `heappush` and `heappop` functions in action: they ensure the list is still sorted after each operation, an important feature for a priority queue.

That'll do it! Great job implementing a classic today.

## Part 2

Like the other days, we need to put the bulk of our work into a function and call it with slightly smaller inputs. Our `part_1` becomes `def _solve(self, start: GridPoint) -> int:` and the call to `parse_grid` is removed.

Next, we refactor `parse_grid` to the following:

```py
class Solution(StrSplitSolution):
    ...

    def find_letters(self, letter: str):
        for row, line in enumerate(self.grid):
            for col, c in enumerate(line):
                if c == letter:
                    yield row, col
```

This yields all the occurrences of a given letter (instead of manually finding `S`). This lets us right a unified solve:

```py
class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        self.grid = [list(l) for l in self.input]

        shortest_path_from_start = self._solve(next(self.find_letters("S")))

        shortest_path = min(
            filter(
                lambda x: x >= 0, (self._solve(loc) for loc in self.find_letters("a"))
            )
        )

        return shortest_path_from_start, shortest_path
```

We've inlined our grid parsing, since there wasn't much to it. We manually call `next` once to get our starting position (which will error if one isn't found) and then iterate like normal through all the `a`'s. We could have done a nested list comprehension instead of a call to `filter`, but I find them less readable, so I went this way today instead.
