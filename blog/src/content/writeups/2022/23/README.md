---
year: 2022
day: 23
title: "Unstable Diffusion"
slug: "2022/day/23"
pub_date: "2023-07-25"
---

## Part 1

Today's task is a spin on the widely-studied [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) - a big grid of individual ~~cells~~ elves moves each turn based on their surroundings. Calculating these moves efficiently will require a grid, probably a sparse one like we had [yesterday](/writeups/2022/day/22/). Because the only thing we need to know about a point is whether or not there's an elf currently in it, we don't even need a `dict`; a `set` of elf locations will suffice:

```py
GridPoint = tuple[int, int]

class Grid:
    def __init__(self, raw_grid: str) -> None:
        self.grid: set[GridPoint] = set()

        for row, line in enumerate(raw_grid.split("\n")):
            for col, c in enumerate(line):
                if c == "#":
                    self.grid.add((row, col))
```

Before we get into the meat of the solution, we need to be able to correctly find the bounds of the rectangle that surrounds the elves. It's simple, but repetitive:

```py
from operator import itemgetter

class Grid:
    ...

    def get_corners(self):
        min_row: int = min(map(itemgetter(0), self.grid))
        max_row: int = max(map(itemgetter(0), self.grid))

        min_col: int = min(map(itemgetter(1), self.grid))
        max_col: int = max(map(itemgetter(1), self.grid))

        return min_row, max_row, min_col, max_col
```

We used `itemgetter` on days [12](/writeups/2022/day/12/) and [15](/writeups/2022/day/15/), so it's hopefully familiar by now. It remains a nice way to simplify repetitive code.

Because our rectangle is the smallest that contains every elf, we can easily count the empty floor spaces by getting the area of the square and subtracting the number of elves (a fixed number):

```py
...

class Grid:
    ...

    def get_area(self) -> int:
        min_row, max_row, min_col, max_col = self.get_corners()

        grid_size = (max_row - min_row + 1) * (max_col - min_col + 1)
        return grid_size - len(self.grid)
```

Now for the meat of the problem: simulating the rounds. For each elf, it needs to:

- decide if it moves at all
- declare a direction to move

Then, one each elf has done that, we have to actually move the unique ones. Our `potential_moves` tracker will need to know where everyone wants to go and an easy way to compare them. An simple way to do this is a `dict`, mapping a destination to the elves who want to move there:

```py
from collections import defaultdict

...

class Grid:
    ...

    def step(self) -> bool:
        potential_moves: defaultdict[GridPoint, list[GridPoint]] = defaultdict(list)
```

Next, we calculate the moves for each elf. This reuses my handy `neighbors` function mentioned in [day 12](/writeups/2022/day/12/) (which you can see in its entirety [here](https://github.com/xavdid/advent-of-code/blob/513f070cd043b898d5b745e248ab0dd466d689f0/solutions/base.py#L300-L350)).

So we:

1. skip this elf if they have no neighbors at all
2. find the first direction in which they have a neighbor and use that to suggest their new spot

That's pretty straightforward:

```py
...

def calculate_offset(tile: GridPoint, offset: GridPoint) -> GridPoint:
    return tuple(map(sum, zip(tile, offset)))

OFFSETS: dict[str, list[tuple[int, int]]] = {
    "N": [(-1, -1), (-1, 0), (-1, 1)],
    "E": [(-1, 1), (0, 1), (1, 1)],
    "S": [(1, 1), (1, 0), (1, -1)],
    "W": [(1, -1), (0, -1), (-1, -1)],
}

class Grid:
    directions = ["N", "S", "W", "E"]

    ...

    def check_direction(self, elf: GridPoint, d: str) -> Optional[GridPoint]:
        """
        returns the move destination if there are no elves in the 3 points in `direction` from `elf`
        """
        if not any(calculate_offset(elf, o) in self.grid for o in OFFSETS[d]):
            return calculate_offset(elf, OFFSETS[d][1])

    def step(self) -> bool:
        ...

        for elf in self.grid:
            # elves with no neighbors don't move
            if not any(n in self.grid for n in neighbors(elf)):
                continue

            for d in self.directions:
                if new_position := self.check_direction(elf, d):
                    potential_moves[new_position].append(elf)
                    break
```

All pretty straightforward - we have 3 offsets for each direction, which we can add to an elf's position to get a new position (if they have any neighbors at all). That the "first half of the round", as described in the prompt.

The second half involves untangling our `potential_moves`. We skip any destination that has multiple elves vying for it, which is simple enough. For any spots that remain, we update the elf's position by removing the old spot and adding the new:

```py
...

class Grid:
    ...

    def step(self) -> bool:
        ...

        for destination, applicants in potential_moves.items():
            if len(applicants) > 1:
                continue

            self.grid.remove(applicants[0])
            self.grid.add(destination)
```

The last piece is we have to "rotate" our directions order by moving the first one from this round to the end. You could use a `collections.deque`, but a bit of static list manipulation is pretty readable:

```py
...

class Grid:
    ...

    def step(self) -> bool:
        ...

        self.directions = self.directions[1:] + [self.directions[0]]
```

Back at the root, we need to call the grid code and return the score after 10 rounds:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        grid = Grid(self.input)
        for _ in range(10):
            grid.step()
        return grid.get_area()
```

## Part 2

Because we already set up our grid so nicely, part 2 requires very little change. I had a feeling this was coming when I read `At this point, no Elves need to move, and so the process ends.` in the part 1 description.

Lucky for us, we already know if there are any moves! If `potential_moves` is empty, then there must have been no valid changes (and there never will be). So let's modify the end of `step` to return whether or not anything changed:

```py
...

class Grid:
    ...

    def step(self) -> bool:
        ...

        return bool(potential_moves)
```

We'll want to adjust our main code as well:

```py
...

class Solution(TextSolution):
    def solve(self) -> tuple[int, int]:
        grid = Grid(self.input)

        part_1 = 0
        part_2 = 0

        for r in range(1, 1500):
            any_moves = grid.step()
            if r == 10:
                part_1 = grid.get_area()

            if not any_moves:
                part_2 = r
                break

        return part_1, part_2
```

That's all there is to it!
