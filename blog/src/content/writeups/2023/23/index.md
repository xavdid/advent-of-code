---
year: 2023
day: 23
slug: 2023/day/23
title: "TKTK"
# concepts: [dfs]
# pub_date: "TBD"
---

## Part 1

Today's task is finding the longest path between two points. This can be a [notoriously tricky problem](https://en.wikipedia.org/wiki/Longest_path_problem), but the design of our input simplifies things. We're given long hallways connected by exit-only intersections, there aren't _that_ many paths through the maze. If we find them all, comparing their lengths is easy. This won't work if there are too many intersections, but I bet this'll work.

To do this, we'll walk the maze, keeping track of where we step. Any time we reach an intersection, we'll "fork" our journey with a new starting point and a copy of the path up to this point.

Code wise, we'll start by parsing our grid. We reach once again for my `parse_grid` [utility function](https://github.com/xavdid/advent-of-code/blob/d01344a90578d5168a3e511e6c9c247c3eccd7fe/solutions/utils/graphs.py#L65) (set to ignore `#` characters), which gives us a sparse grid in a `dict`. We'll also look for the start and target points as the only points in the first and last rows:

```py
from ...utils.graphs import parse_grid

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        grid = parse_grid(self.input, ignore_chars="#")

        start = next(p for p in grid if p[0] == 0)
        target = next(p for p in grid if p[0] == len(self.input) - 1)
```

Next, we'll do our actual walking. We'll start simple, by tracking our steps in a `set` and using my [`neighbors` util](https://github.com/xavdid/advent-of-code/blob/d01344a90578d5168a3e511e6c9c247c3eccd7fe/solutions/utils/graphs.py#L12) to find our next moves:

```py
from ...utils.graphs import GridPoint, neighbors, parse_grid

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        cur = start
        seen: set[GridPoint] = set()

        while True:
            seen.add(cur)

            moves = [
                n
                for n in neighbors(cur, num_directions=4)
                if n in grid and n not in seen
            ]

            if len(moves) == 1:
                cur = moves[0]
            else:
                # TODO: intersection!
                print(f'found intersection at {cur}, bailing!')
                break
```

Running this code on the sample gets us to `(5, 3)` successfully. Now for the actual exploration. We want to do what we just did, but starting again in each of the possible directions. To track that, we need to store new start points and our in-progress paths. This requires a slight shift on our existing code:

```py ins={7,9,10,19} rem={18}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        paths: list[tuple[GridPoint, set[GridPoint]]] = [(start, {start})]

        while paths:
            cur, seen = paths.pop()

            while True: # same code, but indented one more level
                ...

                if len(moves) == 1:
                    cur = moves[0]
                else:
                    print(f"found intersection at {cur}, bailing!")
                    paths += [(n, seen.copy()) for n in moves]
                    break
```

Next, we need to account for the slides. This is a change to how we build our `moves` list. If we're standing on a slide, our only valid move is the direction it's pointing. By storing those offsets, it's easy to know what our next position will be (and if we've seen it):

```py ins={20-25}
...

OFFSETS = {
    ">": (0, 1),
    "v": (1, 0),
    "<": (0, -1),
    "^": (0, -1),
}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while paths:
            ...

            while True:
                ...

                if slide := OFFSETS.get(grid[cur]):
                    if (step := add_points(cur, slide)) not in seen:
                        moves = [step]
                    else:
                        moves = []
                else:
                    moves = [ # same, but indented
                        n
                        for n in neighbors(cur, num_directions=4)
                        if n in grid and n not in seen
                    ]
```

The empty `moves` mean no further paths are added and this line of exploration never found the ending... which is something we haven't actually written yet. Let's rectify that:

```py ins={7,13-15,19}
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        distances: list[int] = []

        while paths:
            ...

            while True:
                if cur == target:
                    distances.append(len(seen))
                    break

                ...

        return max(distances)
```

If we ever land on the target, we store how long (this particular route) took to get there. At the end, we return the longest one!

I thought this would take too long to run on the real input, but I got my answer in `.2` seconds! I had ~ 250 possible unique paths through the maze, but later ones don't have far to check. Onward!

## Part 2

Unfortunately, the removal of the slides mean there are now _many_ paths through the map, so we'll need another approach.
