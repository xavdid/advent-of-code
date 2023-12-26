---
year: 2020
day: 17
title: "Conway Cubes"
slug: "2020/day/17"
pub_date: "2020-12-19"
---

## Part 1

Similar to [day 11](/writeups/2020/day/11/), we're doing a spin on [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) (albeit with a much more direct reference).

The rules are simple enough:

- if a cube is inactive and exactly 3 neighbors are active, it becomes active
- if a cube is active and it's active neighbor count is anything besides 2 or 3, it becomes inactive

The slightly tricky thing is that we have to consider all the cubes in an infinite 3d space. Knowing what to iterate over may be tricky, but nothing we can't handle. Instead of keeping an array structure (which gets confusing in 3D), let's take a different approach: a `defaultdict` where the key is an `(x,y,z)` tuple and the value is boolean denoting "active". It'll be able to grow easily, be checked quickly, and we can iterate all stored points.

Our grid is infinite in all directions, but we only need to worry about items next to our cubes. Anything outside that bubble will never become active (because it's always surrounded by only inactive cubes and lacks any active neighbors).

Honestly, my approach is here mostly utility functions. We start with a class that handles our input:

```py
class ConwayCube:
    cubes: DefaultDict[Tuple[int, int, int], bool] = defaultdict(bool)

    def __init__(self, initial_state: List[str]) -> None:
        # read input, which is 2D
        for neg_y, line in enumerate(initial_state):
            for x, val in enumerate(line):
                self.cubes[(x, -neg_y, 0)] = val == "#"
```

Note that we use `-y` since we're counting down; positive `y` values would be _above_ our input.

The next thing we'll need to know is the bounds of our cube space - the biggest and smallest value for each of `x`, `y`, and `z`. We already have all the points we've looked at, so we need to find the `min` and `max` of each index for each key:

```py
@property
def min_z(self):
    min({p[0] for p in self.cubes})

@property
def min_y(self):
    min({p[1] for p in self.cubes})

...
```

We use `@property` mostly for style reasons. The functions don't take arguments and there are no side effects when calling, so we can think of them more as static values. Plus, `self.min_x` is a little cleaner than `self.min_x()`. But, [there aren't rules](https://stackoverflow.com/questions/1554546/when-and-how-to-use-the-builtin-function-property-in-python), so follow your own preference.

In any case, you'll notice that all 6 of these functions are _very_ similar. So much so that we can abstract them down:

```py
def _extreme_coord(self, index: int, func: Callable) -> int:
    return func({c[index] for c in self.cubes})

@property
def min_x(self) -> int:
    return self._extreme_coord(0, min)

@property
def min_y(self) -> int:
    return self._extreme_coord(1, min)

...
```

Did you catch that? We're using the built-in `min` and `max` functions as arguments! All `_extreme_coord` knows is that it gets a function and where to use said function. This approach doesn't really reduce our boilerplate, but it does keep our implementation in a single spot, which is nice for maintainability.

Now that we know the bounds of the space we're interested in, we can iterate over those coordinates:

```py
def all_cube_coords(self):
    # +1 to be range inclusive
    for x in range(self.min_x, self.max_x + 1):
        for y in range(self.min_y, self.max_y + 1):
            for z in range(self.min_z, self.max_z + 1):
                yield (x, y, z)
```

That's perfectly correct, but a little ugly because of the extreme nesting. Luckily, Python's `itertools` has just the function for us:

```py
from itertools import product

def all_cube_coords(self):
    # +1 to be range inclusive
    return product(
        range(self.min_x, self.max_x + 1),
        range(self.min_y, self.max_y + 1),
        range(self.min_z, self.max_z + 1),
    )
```

Both of the above are equivalent because `product` itself returns a `generator`.

Ok, so we'll be able to look at each cube in our problem space - what do we do with each? To be stepping forward in time, we'll be looking at each neighbor for each of those cubes, counting up the active ones, and doing something as a result. Sounds like a couple more functions!

```py
COORD_OFFSETS = (-1, 0, 1)

def neighbors(self, cube_x: int, cube_y: int, cube_z: int):
    for x, y, z in product(COORD_OFFSETS, repeat=3):
        if not any([x, y, z]):
            # can't be our own neighbor
            continue
        yield (cube_x + x, cube_y + y, cube_z + z)
```

This approach uses the `repeat=` `kwarg` of `product` to well, repeat. While `product('AB')` gives `['A', 'B']`, `product('AB', repeat=2)` gives `['AA', 'AB', 'BA', 'BB']`. That's what we want with the offsets: each combination of `+1`, `-1` and neutral in each direction. We also make sure to skip `(0,0,0)` because you're not your own neighbor. Now that we can iterate, we can count the `True` both around a point and globally:

```py
def num_active_neighbors(self, x: int, y: int, z: int) -> int:
    return len(
        [
            self.cubes[neighbor]
            for neighbor in self.neighbors(x, y, z)
            if self.cubes[neighbor]
        ]
    )

@property
def num_active(self) -> int:
    return len([x for x in self.cubes.values() if x])
```

Lastly, our step function:

```py
def step(self) -> None:
    next_state = defaultdict(bool)

    for coord in self.all_cube_coords():
        for cube in self.neighbors(*coord):
            num_active_neighbors = self.num_active_neighbors(*cube)
            if not self.cubes[cube] and num_active_neighbors == 3:
                next_state[cube] = True
            elif self.cubes[cube] and num_active_neighbors not in (2, 3):
                next_state[cube] = False
            else:
                next_state[cube] = self.cubes[cube]

    self.cubes = next_state
```

A couple of uses of `*` to prevent having to write `(x,y,z)` over and over, but otherwise simple. Finally, we can get an answer:

```py
cubes = ConwayCube(self.input)
for _ in range(6):
    cubes.step()
return cubes.num_active
```

## Part 2

Part 2 is the same puzzle, but with an added `w` every time there's an `(x,y,z)`. I subclassed my `ConwayCube` and tweaked some functions as needed... which wasn't near fast enough. Off to [reddit](https://old.reddit.com/r/adventofcode/comments/keqsfa/2020_day_17_solutions/) we go!

Seems like we're falling victim of the [curse of dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality), where adding a dimension further increases sparseness. `/u/mstksg` [summarizes it well](https://old.reddit.com/r/adventofcode/comments/keqsfa/2020_day_17_solutions/gg4hsdy/):

> It means that when we get to 3D and 4D, our world will become vanishingly sparse. In my own input, only about 4% of the 3D space ended up being active, and 2% of my 4D space ends up being active. This means that holding a dense vector of all possible active points (which will be `(6+8+6)^n`) is up to 98% wasteful. And because of the way this process works, we have to completely copy our entire space at every iteration.

We're storing (and looping over) a ton of extra, empty space. Conway's Game of Life is pretty well-trod, so let's find a cleaner solution. I really like [this approach](https://old.reddit.com/r/adventofcode/comments/keqsfa/2020_day_17_solutions/gg648nj/), from `/u/ssnoyes`.

They start with a dumb function that's the rough equivalent of our `neighbors` above:

```py
def get_neighbors(cell: Tuple[int, ...]):
    neighbors = [
        tuple(cell[i] + v[i] for i in range(len(cell)))
        for v in product([-1, 0, 1], repeat=len(cell))
    ]
    neighbors.remove(cell)
    return neighbors
```

From the main loop, we use that to build `neighbors`, a `Counter` which tracks how many time each neighbor is looked at. The key is the cell-tuple and the value is the number of occurrences:

```py
neighbors = Counter(
    neighbor for cell in living for neighbor in get_neighbors(cell)
)

# --- or, less concisely

neighbors = []
for cell in living:
    for neighbor in get_neighbors(cell):
        neighbors.append(cell)

neighbors = Counter(neighbors)
```

I like this approach a lot because it's the inverse of mine - instead of calculating the number of active neighbors for a given square, we count the number of times each coordinate is mentioned as the neighbor of an active cell. This took me a couple of passes to wrap my head around, so here's a quick diagram. If we had this 2D setup:

```
.#.
#.#
.#.
```

We could either:

- iterate over all 9 coordinates and (inefficiently) look at all 8 neighbors for every one (9 cells \* 8 neighbors)
- Iterate over the living cells and have them announce all their neighbors (4 \* 8)

In the second case, the number of times a cell is mentioned must equal the number of active cells for which it is a neighbor. Since that's the exact metric we use to calculate the next step, a complete `Counter` makes this easy:

```py
living = {
    cell
    for cell, times_seen in neighbors.items()
    if times_seen == 3 or (cell in living and times_seen == 2)
}
```

Because all tuple are iterated over, as long as the initial input-reading appends the right number of 0s, everything adjusts accordingly. After `N` times calculating neighbors and living, `len(living)` is our answer.

I really like this solution - sometimes I need to remember to think outside the box a little more.
