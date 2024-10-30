---
year: 2023
day: 23
slug: 2023/day/23
title: "A Long Walk"
# concepts: [dfs]
pub_date: "2024-10-29"
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

Unfortunately, the removal of the slides mean there are now _many_ paths through the map, so we'll need another approach. The best way to start is to reduce the number of graph nodes down to the actual places we can stop.

Because everything is hallways, we're really only making choices when we reach intersections. If we pre-calculate all those distances, we can save ourselves a lot of computation when we're exploring all the possible routes.

Ultimately, we want to build a graph where each intersection knows the distance to each intersection it can reach directly (and how far away it is). For the test input, that'll be:

```py
{
    (0, 1): {(5, 3): 15},
    (3, 11): {(5, 3): 22, (11, 21): 30, (13, 13): 24},
    (5, 3): {(3, 11): 22, (13, 5): 22},
    (11, 21): {(3, 11): 30, (13, 13): 18, (19, 19): 10},
    (13, 5): {(5, 3): 22, (13, 13): 12, (19, 13): 38},
    (13, 13): {(3, 11): 24, (11, 21): 18, (13, 5): 12, (19, 13): 10},
    (19, 13): {(13, 5): 38, (13, 13): 10, (19, 19): 10},
    (19, 19): {(11, 21): 10, (19, 13): 10, (22, 21): 5}
}
```

> NOTE: I kept my parts 1 and 2 solutions separate, but I'll mark the changes I made to the existing code to keep everything easier to follow.

We'll walk the grid again, but the data structure we use to track paths has changed. Instead of mapping a whole path and forking it, we just need to record the distance between each intersection:

```py ins={1,12,15,19-20} rem={11,14,18}
from collections import defaultdict

...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ... # parse graph, find start

        paths: list[tuple[GridPoint, set[GridPoint]]] = [(start, {start})]
        paths: list[tuple[GridPoint, GridPoint]] = [(start, start)]

        distances: list[int] = []
        graph: defaultdict[GridPoint, dict[GridPoint, int]] = defaultdict(dict)

        while paths:
            cur, seen = paths.pop()
            starting_point, cur = paths.pop()
            seen = {starting_point}

            ...
```

Beginning with `(start, start)` looks a little silly, but we'll be passing different things when we hit intersections.

Next, we'll change how we calculate next steps. We don't care about the slides anymore, so we can simplify this section a bit:

```py ins={15,26-27,30,34-37,39} rem={14,31-33}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        while paths:
            ...

            while True:
                if cur == target:
                    distances.append(len(seen))
                    graph[starting_point][cur] = len(seen)
                    break

                seen.add(cur)

                moves = [
                    n
                    for n in neighbors(cur, num_directions=4)
                    if n in grid and n not in seen
                ]

                if not moves:
                    break
                if len(moves) == 1:
                    cur = moves[0]
                    continue
                else:
                    paths += [(n, seen.copy()) for n in moves]
                    break
                if cur not in graph[starting_point]:
                    # we started on the first step, so we have to offset by 1
                    graph[starting_point][cur] = len(seen) - 1
                    paths += [(cur, n) for n in moves]

                break
```

If there are no moves, we just stop, and if we take a single step in a hallway, we keep trucking.

The key piece here is right at the bottom - if there are multiple moves, you've reached an intersection! First, store your distance from the original starting point to here. Then, queue up the next segments: an expedition to chart from (`cur`) and the neighbor representing the first step (`n`). Once we've hit an intersection, we stop whether or not we've queued further steps.

And, once we're standing on the target, we can store that distance (even though it's not an intersection).

Next, we need to traverse the graph and find all the routes. This looks like a simplified version of our part 1 code:

```py ins={14,17-28}
...

class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        graph: defaultdict[GridPoint, dict[GridPoint, int]] = defaultdict(dict)

        while paths:
            ...

        stack: list[tuple[GridPoint, int, set[GridPoint]]] = [(start, 0, set())]
        distances: list[int] = []

        while stack:
            cur, distance, seen = stack.pop()

            if cur == target:
                distances.append(distance)
                continue

            seen.add(cur)

            for intersection, d in graph[cur].items():
                if intersection not in seen:
                    stack.append((intersection, distance + d, seen.copy()))

        return max(distances)
```

Each time we step, we check each other node we could visit and add anything we haven't visited on this trip and summing our distance as we go. We do the same forking we did in part 1, where every journey gets its own copy of the trail.

While part 1 was fast, running this takes ~ 17 seconds on my laptop. Definitely faster than I'd like, but there are only so many ways to explore this many nodes. There could be other tricks, but sometimes things just take a while!
