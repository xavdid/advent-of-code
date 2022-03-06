# Day 19 (2021)

`Beacon Scanner` ([prompt](https://adventofcode.com/2021/day/19))

## Part 1

This is one I [avoided as long as I could](https://github.com/xavdid/advent-of-code/blob/4a5f321100735e80e0fd1183148da08eccb249c6/solutions/2021/day_19/README.md). It wasn't one I had any idea how to approach. After spinning my wheels on it, I caved and checked out the [solution thread](https://www.reddit.com/r/adventofcode/comments/rjpf7f/2021_day_19_solutions/). Turns out that the "easy" solution was to know [linear algebra](https://simple.wikipedia.org/wiki/Linear_algebra), which is something I've got absolutely no experience with. The `tl;dr` is that it's a branch of mathematics that uses matrices to solve for `x` and `y` in sets of linear functions. For a reason I don't quite grok, it't super applicable to other engineering fields. Luckily, it didn't end up being _required_ today, just helpful. Let's walk through [this solution](https://www.reddit.com/r/adventofcode/comments/rjpf7f/2021_day_19_solutions/hp78lpo/) by `/u/p88h` to see how it's solvable with good, old-fashioned programming.

Input parsing! Not too bad today, just a little verbose. For each block (separated by `\n\n`), we need to split the line by a comma and turn each element into `int`s. Here's my function with a big docstring and some concise parsing:

```py
Point3D = Tuple[int, int, int]

class Solution:
    ...

    def parse_input(self) -> List[List[Point3D]]:
        """
        Parses each individual scanner block into a list of tuples

        This:

            --- scanner 0 ---
            404,-588,-901
            528,-643,409
            ...

            --- scanner 1 ---
            686,422,578
            605,423,415
            ...

        becomes:

            [
                [
                    (404, -588,-901),
                    (528, -643, 409),
                    ...
                ],
                [
                    (686, 422, 578),
                    (605, 423, 415),
                    ...
                ],
            ]
        """
        return [
            [tuple(map(int, line.split(","))) for line in block.split("\n")[1:]]
            for block in self.input.split("\n\n")
        ]
```

That in hand, let's dig into the the hard part: we have to write a function that can tell if two scanners report overlapping points. The rotation made this seem really hard and, while it certainly complicates it, it's not as bad as I thought. The key to the whole thing is that all of the points, no matter the rotation, will _have the same offsets_. So, if we count the distances between every combination of points reported by 2 scanners and there's at least 12 that have the exact same offset in a given dimension, then we know how far away the scanners must be from each other. That sounds like a lot, but some examples should help clear it up.

Let's imagine a simple case where there's a line of beacons (`B`) between scanners `S` and `T`.

```
B....
.B...
S.B..
...BT
```

Scanner `S` reports the top 3 points as (top to bottom):

```
0,2
1,1
2,0
3,-1
```

While `T` reports them like so:

```
-4,3
-3,2
-2,1
-1,0
```

We don't know where S and T are relative to each other. But, we know that if a beacon is reported by both scanners, then the difference between the two reported values will be the same across each matched beacon. We can see this in our example:

| `S`'s `x` value | `T`'s `x` value | difference (`Sx - Tx`) |
| --------------- | --------------- | ---------------------- |
| 0               | -4              | 4                      |
| 1               | -3              | 4                      |
| 2               | -2              | 4                      |
| 3               | -1              | 4                      |

The same holds true for the `y` values:

| `Sy` | `Ty` | difference |
| ---- | ---- | ---------- |
| 2    | 3    | -1         |
| 1    | 2    | -1         |
| 0    | 1    | -1         |
| -1   | 0    | -1         |

Of course, the points aren't sorted in our puzzle input. So, we have to compare differences between every possible pair of `Sx` and `Tx` (using a nested `for` loop, or the `itertools.product` function). Here's the full combination table for the `x` values:

| `Sx` | `Tx` | difference |
| ---- | ---- | ---------- |
| 0    | -4   | 4          |
| 0    | -3   | 3          |
| 0    | -2   | 2          |
| 0    | -1   | 1          |
| 1    | -4   | 5          |
| 1    | -3   | 4          |
| 1    | -2   | 3          |
| 1    | -1   | 2          |
| 2    | -4   | 6          |
| 2    | -3   | 5          |
| 2    | -2   | 4          |
| 2    | -1   | 3          |
| 3    | -4   | 7          |
| 3    | -3   | 6          |
| 3    | -2   | 5          |
| 3    | -1   | 4          |

If we run the `difference` column through a `Counter`, we get:

```py
Counter({
    # difference : # occurrences
    4: 4,
    3: 3,
    5: 3,
    2: 2,
    6: 2,
    1: 1,
    7: 1
})
```

This tells us that for `x` values, there are 4 overlapping beacons. In the actual puzzle, we need 12, but this validates that our initial plan works! We see similar results with the `y` offsets counter:

```py
Counter({
    -1: 4,
     0: 3,
    -2: 3,
     1: 2,
    -3: 2,
     2: 1,
    -4: 1
})
```

It's worth noting that this approach depends on the fact that each beacon is unique in each dimension (an assumption we can verify in the example output). I suspect this approach wouldn't be viable with a random dataset; luckily, we don't have one of those!

Most importantly, it tells us that the `T` scanner is at point `4, -1` if `S` is at `(0, 0)`. And that's true!

Of course, there's another wrinkle- the rotation/flipping of each scanner. In our last example, `S` and `T` were oriented the same way. But what about when they're not? If we rotate `T` 90 degrees, suddenly the world looks very different. The original map:

```
B....
.B...
S.B..
...BT
```

becomes:

```
.S.B
..B.
.B..
B...
T...
```

when `T` reports it. It now announces the beacons as:

```
0,1
1,2
2,3
3,4
```

If we compare the `x` values like we did before, the differences are all `0`! That can't be right; that means the points are on top of each other. Instead, we have to change which columns we're comparing to each other. The column that `S` sees as `+x` (going to the right) becomes `-y` (going down). What before was `+y` (up) now becomes `+x` (right). It helped me to picture it like a clock:

```
+y
 ^
 |
 |
 |---> +x
```

when rotated 90 degrees clockwise, becomes:

```
 |---> +x
 |
 |
 V
-y
```

As a result, our comparison tables must change:

| `Sx` | `Ty * -1` | difference |
| ---- | --------- | ---------- |
| 0    | -1        | 1          |
| 0    | -2        | 2          |
| 0    | -3        | 3          |
| 0    | -4        | 4          |
| 1    | -1        | 2          |
| 1    | -2        | 3          |
| 1    | -3        | 4          |
| 1    | -4        | 5          |
| 2    | -1        | 3          |
| 2    | -2        | 4          |
| 2    | -3        | 5          |
| 2    | -4        | 6          |
| 3    | -1        | 4          |
| 3    | -2        | 5          |
| 3    | -3        | 6          |
| 3    | -4        | 7          |

Which counts up to:

```py
Counter({4: 4, 3: 3, 5: 3, 2: 2, 6: 2, 1: 1, 7: 1})
```

This tells us that, accounting for rotation, `T` is still `4` from `S`. Comparing the `Ty` column to `Sx` yields the same result. Knowing that, we can re-orient all the points reported by `T` and express them using `S` as the basis. Now, the points that both scanners report will be identical numbers, and we can de-duplicate them! This is the key to the puzzle.

Astute readers will notice we've gone _quite_ a while without actually writing any code; let's remedy that! Now that we sort of know what we need to do, I'm going to swap over to the actual example (where `scanner 0` starts with `404,-588,-901`) instead of my little one. We should be developing against our actual input to make sure our solution will solve the puzzle, not my contrived example.

We'll now write a function that'll take a pair of scanner reports (`List[Point3D]`) and returns both:

- the points of the second report, oriented in terms of the first, and
- the location of the second scanner relative to the first

And we do that only if we find at least 12 overlapping points (per the prompt). We'll need to compare each column of our source scanner with each column (including the inverses) of our potential overlap to search for our common offsets. Because we're calculating each column independently, we'll store them that way too (and collect the results at the bottom).

```py
def try_align(
    source_scanner: List[Point3D], possible_overlapping_scanner: List[Point3D]
) -> Tuple[List[Point3D], Point3D]:

```

## Part 2
