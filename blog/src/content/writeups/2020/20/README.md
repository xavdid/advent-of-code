---
year: 2020
day: 20
title: "Jurassic Jigsaw"
slug: "2020/day/20"
pub_date: "2020-12-29"
---

## Part 1

For part one, we're identifying corner tiles. How do we tell a corner from any other type of piece?

The prompt tells us that each interior edge has a twin. So if we count the occurrences for each edge, we'll know which ones only show up once. Those must be our exterior edges! And any tiles that have two such edges? Corners.

Let's parse some input.

Given that we'll be working closely with these tiles, I thought it worthwhile to put them into a class. It'll take a `list` of `string`s (each newline-separated block describing a tile) and will store both the unique `id` and the actual points:

```py
class Tile:
    def __init__(self, data: List[str]) -> None:
        lines = data.split("\n")

        self.num = int(lines[0].split(" ")[1][:-1])
        self.points = [tuple(line) for line in lines[1:]]
```

In our quests to get all sides of a tile, we'll need to both rotate and flip the tiles:

```py
class Tile:
    ...

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
class Tile:
    ...

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

This part seems intimidating, and it requires a lot of code, but algorithmically, it's straightforward. I've tweaked some part 1 code that I'll reference below, but you should recognize it.

We'll eventually need to look through a completed puzzle for monsters, so we must solve the puzzle. We know that given a tile, we'll always be able to find an adjacent tile. So if we start with a corner (just like we would with any puzzle), then we can keep finding adjacent tiles until we're done.

To start, we need to identify a corner. During part 1, we were already finding corners, so let's stash an ID while we're at it.

```py
# part 1
corner_num_product = 1
corner_num = None
for tile in self.tiles:
    # find the tiles who have 2 sides that only show up once
    num_outside_edges = len(
        [s for s in tile.all_tops(skip_flip=True) if self.edge_counts[s] == 1]
    )
    if num_outside_edges == 2:
        corner_num_product *= tile.num
        if corner_num is None:
            corner_num = tile.num
```

So now we've got a corner. We need to make sure it's facing the right way, so we need to be able to read any side of a tile. Let's add some methods to match our `top_row`:

```py
class Tile:
    ...

    # renamed to match others
    @property
    def top_side(self) -> str:
        """
        read left to right
        """
        return "".join(self.points[0])

    @property
    def bottom_side(self) -> str:
        """
        read left to right
        """
        return "".join(self.points[-1])

    @property
    def left_side(self) -> str:
        """
        read top to bottom
        """
        return "".join(x[0] for x in self.points)

    @property
    def right_side(self) -> str:
        """
        read top to bottom
        """
        return "".join(x[-1] for x in self.points)

    def get_side(self, side) -> str:
        return getattr(self, f"{side}_side")
```

Now we can grab any side both programmatically and by name. This lets us write a function to specify where a corner's exterior sides should be:

```py
class Solution():
    ...

    def align_corner(self, tile: Tile, side_a: str, side_b: str) -> None:
        """
        Modifies the `tile` so each of the passed sides are edges
        """
        while not (
            self.edge_counts[tile.get_side(side_a)] == 1
            and self.edge_counts[tile.get_side(side_b)] == 1
        ):
            tile.rotate()

# in Solution.solve()
next_tile = next(t for t in self.tiles if t.num == corner_num)
self.align_corner(next_tile, "left", "top")
```

Now, with our top-left corner, we can begin. We know the grid is always a square (the example is 9 tiles, the puzzle input is 144), so the height and width are both `int(sqrt(len(self.tiles)))`. To solve the whole puzzle, we need to actually build that grid structure. If we're at the very start of our 2d grid, we'll grab and orient our corner:

```py
solved: List[List[Tile]] = []
for row in range(grid_size):
    next_row: List[Tile] = []
    for column in range(grid_size):
        if column == 0 and row == 0:
            # start with any corner
            next_tile = next(t for t in self.tiles if t.num == corner_num)
            self.align_corner(next_tile, "left", "top")
```

It doesn't matter which corner we start with because the puzzle can only be solved one way (and in any orientation). We'll worry about that later.

Once we've got the first tile, we find whatever tiles pairs with its right side. We need a method to iterate over all tiles to find the matching one and another to orient it:

```py
class Tile:
    ...

    def match_side(self, side: str, target: str) -> None:
        """
        Flips and rotates the tile until it's in the correct orientation for
        its `side` side to match the given one
        """
        for _ in range(4):
            if self.get_side(side) == target:
                return
            self.rotate()

        self.flip()
        for _ in range(4):
            if self.get_side(side) == target:
                return
            self.rotate()

        raise ValueError("Non-matching tile")

class Solution:
    ...

    def find_and_rotate_tile(self, side: str, target: str) -> Tile:
        for tile in self.tiles:
            if target in tile.all_tops():
                tile.match_side(side, target)
                return tile

        raise ValueError("Unable to find tile", side, target)
```

Back in our main loop:

```py
    ...

    if column == 0 and row == 0:
        ...
    else:
        next_tile = self.find_and_rotate_tile(
            "left", next_row[-1].right_side
        )

    self.tiles.remove(next_tile)
    next_row.append(next_tile)
```

The first time through `row, column` we grab and store a corner. On subsequent loops, we find a tile whose `left` side matches the `.right_side` of the last tile we found. We can keep that up through the end of the row... until we get to the next row. Now `next_row` is empty and there's no previous tile. Instead, we need to match off the `bottom` of the first tile in the row above:

```py
    ...
    if column == 0 and row == 0:
        ...
    elif column == 0:
        next_tile = self.find_and_rotate_tile(
            "top", solved[-1][column].bottom_side
        )
    else:
        ...

solved.append(next_row)
```

Now we can match every tile for each row and column in the grid. No matter which one we find, we remove it from `self.tiles` so we don't check it in future loops. Once it completes (and our search functions error if they fail to find, so you'll know), we have a 2D array with our tiles connected correctly.

Now let's start part 2.

We need to build the actual grid contents by dropping the borders of our tile:

```py
class Tile():
    ...

    def drop_border(self) -> List[str]:
        return ["".join(row[1:-1]) for row in self.points[1:-1]]
```

Each row of our actual image is all of the tiles in that row (each one is 9 lines tall). So we need to zoom out a bit and build strings that are the top row of points for each tile in the `solved` row. If our first row is 3 tiles:

```
ABC DEF GHI
DEF GHI ABC
GHI ABC DEF
```

then our result should be:

```py
[
    'ABCDEFGHI',
    'DEFGHIABC',
    'GHIABCDEF',
]
```

We can leverage the `zip` function, which is perfect for this. If we feed it 3 iterables (remember, `tile.drop_border()` gives a list of strings), it'll give us the first item from each, the second from each, etc:

```py
tiles = [['ABC', 'DEF', 'GHI'], ['DEF', 'GHI', 'ABC'], ['GHI', 'ABC', 'DEF']]
list(zip(*tiles))

# gives
[('ABC', 'DEF', 'GHI'), ('DEF', 'GHI', 'ABC'), ('GHI', 'ABC', 'DEF')]
```

Which is exactly what we want:

```py
actual_image_strs = []
for row in solved:
    for subrow in zip(*[t.drop_border() for t in row]):
        actual_image_strs.append("".join(subrow))
```

So now we've got a `list` of `str`ings that we need to flip, rotate, and search through. As luck would have it, we've got just the class for that! We're going to add some new functions that will only work on a big completed image though, so let's create a subclass:

```py
class Image(Tile):
    def __init__(self, data: List[str]) -> None:
        # create a fake header so it looks like a huge tile
        super().__init__("\n".join(["tile 0000:", *data]))
        self.stringify_points()

    def stringify_points(self) -> None:
        self.points = ["".join(line) for line in self.points]

    def rotate(self) -> None:
        super().rotate()
        self.stringify_points()

    def flip(self) -> None:
        super().flip()
        self.stringify_points()
```

While `Tile` stores its `points` as a `List[Tuple[str]]`, we're going to be searching through our `Image` as strings. So every time we modify the internal representation, we should re-stringify the data. It saves us having to do so in our actual algorithm code. In any case, we now have a working image:

```py
actual_image = Image(actual_image_strs)
```

The last big piece is finding monsters. Monsters follow a nice regular pattern, so they're pretty easy to spot. They exist on 3 lines:

- the middle line is `#....##....##....###`
- the bottom line is `#..#..#..#..#..#` (but it starts 1 spot after the middle)
- the top is a single `#` exactly 18 characters after the start of the middle line

In each case, the `#` need to be exactly that while the `.` can be either an actual period or a hash mark. Sounds like a job for some carefully applied regular expressions. I say carefully applied because we unfortunately can't just count all the matches. Python doesn't allow overlapping matches when matching regex. For example, if we're looking for `ABBA` in the string `ABBABBA`, a human might see `ABBA` twice. Python only sees a single match though (even in "multi" mode), because once the middle `A` is matched with the first instance, only `BBA` is left and it fails to match. In our case, each valid regex match might not be a valid monster. It could be missing either the head or tail, so we can't discount the whole string until we know we've found one.

To verify a sighting is actually pretty easy. Given a row and a column where the middle of a monster has been found, we can check the surrounding rows to ensure they match:

```py
MONSTER_BOTTOM = r"#..#..#..#..#..#"

class Image:
    ...

    def is_monster(self, row_num: int, tail_start: int) -> bool:
        found_head = self.points[row_num - 1][tail_start + 18] == "#"
        found_bottom = bool(
            re.match(MONSTER_BOTTOM, self.points[row_num + 1][tail_start + 1 :])
        )
        return found_head and found_bottom
```

Note the use of `re.match` instead of the more versatile `re.search`. Since the bottom needs to start exactly 1 element after the start of the middle, we use `.match` to ensure the found match is at the start of the supplied string. We could also use the regex `^` character, but not building a regex string if we could avoid it is a little cleaner.

Next, actually walking the image. While we hunt for `MONSTER_MIDDLE`s, we don't need to consider the first or last lines (since the head or bottom would be cut off). But, if we `enumerate(self.points[1:-1])`, then our index variable will be off-by-one; the index will be `0`, but the row will actually be `1` (this was a nasty bug). So, we have a sort of dumb block (that totally works, which makes it not-dumb):

```py
MONSTER_MIDDLE = r"#....##....##....###"

class Image:
    ...

    def count_monsters(self) -> int:
        # the middle of the monster can't be in the first or last line
        total = 0
        for row_num, line in enumerate(self.points[:-1]):
            # so our indexing isn't off-by-1
            if row_num == 0:
                continue
```

Next, we walk over each line with an `int`. Using an `int` directly instead of `for x in line` lets us jump manually, which will become very important. If the character we're looking at isn't `#`, we can skip it (can't be the start of a tail). Then we `re.match` for the `MONSTER_MIDDLE`. If that's found, we call `is_monster` for that `row_num` and index (named `i`). If _that's_ true, then we increment `i` by `20`, the total width of a monster. Sound reasonable?

```py
def count_monsters(self):
    ...

    for row_num, line in enumerate(self.points[:-1]):
        ...

        i = 0
        while i < len(line):
            if line[i] != "#":
                i += 1
                continue
            match = re.match(MONSTER_MIDDLE, line[i:])
            if match:
                if self.is_monster(row_num, i):
                    total += 1
                    i += 20  # total length of sea monster

            i += 1

    return total
```

Finally, if our image is oriented the right way, we can find and count monsters correctly. Home stretch.

The prompt makes it sound like there's only one orientation of the image that will show monsters, so we can rotate and flip until we find any. We can use a generator function to do this. We don't have to `yield` anything in particular - they're great for "do a thing and then stop and then later, pick up where you left off":

```py
class Image(Tile):
    ...

    def each_orientation(self):
        for _ in range(4):
            self.rotate()
            yield None

        self.flip()
        for _ in range(4):
            self.rotate()
            yield None

    def find_monsters(self) -> int:
        for _ in self.each_orientation():
            res = self.count_monsters()
            if res:
                return res
        raise ValueError("Unable to find monster")
```

We search for monsters in each orientation and return if we get a non-zero answer.

Lastly, we need to count the number of `#` that aren't part of the monsters. Each monster is comprised of exactly 15 `#`, so we can count them all and subtract `15 * num_mosters`:

```py
class Image(Tile):
    ...

    def count_waves(self, num_monsters):
        return sum([line.count("#") for line in self.points]) - (num_monsters * 15)
```

At long last, we can return to our actual solution, which is sort of underwhelming after all of that:

```py
actual_image = Image(actual_image_strs)
num_monsters = actual_image.find_monsters()
num_waves = actual_image.count_waves(num_monsters)
```

Thanks for hanging in there!
