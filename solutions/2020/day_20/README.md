# Day 20 (2020)

`Jurassic Jigsaw` ([prompt](https://adventofcode.com/2020/day/20))

## Part 1

For part one, we're identifying corner tiles. How do we tell a corner from any other type of piece?

The prompt tells us that each interior edge has a twin. So if we count the occurances for each edge, we'll know which ones only show up once. Those must be our exterior edges! And any tiles that have two such edges? Corners.

Let's parse some input.

Given that we'll be working closesly with these tiles, I thought it worthwhile to put them into a class. It'll take a `list` of `string`s (each newline-separated block describing a tile) and will store both the unique `id` and the actual points:

```py
class Tile:
    def __init__(self, data: List[str]) -> None:
        lines = data.split("\n")

        self.num = int(lines[0].split(" ")[1][:-1])
        self.points = [tuple(line) for line in lines[1:]]
```

In our quests to get all sides of a tile, we'll need to both rotate and flip the tiles:

```py
def rotate(self) -> None:
    """
    Rotates the grid 90deg clockwise. Modifies the tile.

    https://stackoverflow.com/a/8421412/1825390
    """
    self.points = list(zip(*self.points[::-1]))

def flip(self) -> None:
    """
    Flips a tile horizontally
    """
    for i in range(len(self.points)):
        self.points[i] = tuple(reversed(self.points[i]))
```

Nothing much to call out here. I _did_ pull the 2D List rotation from StackOverlfow because I couldn't be bothered to walk through how to do something I figured existed already.

Next, we need a function to get all 8 versions of the edges of a tile. Why 8? Because the tiles can flip, so read left-to-right, there's 2 versions of each of the 4 sides of a tile. Using the above, we'll need to flip and rotate our way around a tile and get its top row as a string:

```py
@property
def top_row(self) -> str:
    return "".join(self.points[0])

def all_tops(self, skip_flip=False) -> List[str]:
    """
    Rotates and flips the tile to return each of the 8 versions of the top row.
    Modifies the tile when it runs, but has a net-zero effect on position.

    By default, does all 8 sides. Can optionally only get the non-flipped sides.
    """
    res = []
    for _ in range(4):
        res.append(self.top_row)
        self.rotate()
    if skip_flip:
        return res

    self.flip()
    for _ in range(4):
        res.append(self.top_row)
        self.rotate()
    self.flip()
    return res
```

Now for our solution. We'll use a `Counter`, which will quickly count all unique edges it sees.

```py
tiles = [Tile(x) for x in self.input.split("\n\n")]

c = Counter()
for tile in tiles:
    c.update(tile.all_tops())
```

Printing that `Counter` to check our work and we see that most edges were counted twice and exactly 24 (of the prompt's example) were counted once (3 segments on 4 sides, plus the flipped ones).

Now we need to step through the tiles and count how many edges on that tile were only seen once. We don't need to flip anymore, so I added a `kwarg`, `skip_flip` (that you may have been wondering about above), to help. Our final answer is the product of the corner ids, so we'll compute that as we go:

```py
result = 1
for tile in tiles:
    # find the tiles who have 2 sides that only show up once
    if len([s for s in tile.all_tops(skip_flip=True) if c[s] == 1]) == 2:
        result *= tile.num

return result
```

It's a bit of a dense line, but we look at the 4 sides of an un-flipped tile and count up those whose value in the counter is 1. If _that_ total is 2, we know we've got our 2 unmatched sides and we multiply the running result with the `num` of that tile. Tada!

## Part 2
