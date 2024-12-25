---
year: 2024
day: 13
slug: "2024/day/13"
title: "Claw Contraption"
# concepts: [algebra]
pub_date: "2024-12-25"
---

## Part 1

When I read "smallest number of tokens", I thought this would be finding the shortest path through a series of choices. But looking more closely, it's really a pair of linear equations with two unknowns. We can solve that with a bit of algebra!

If we group the `X` and `Y` operations into their own equations (since they operate independently), we can see what we have to work with:

- `A*94 + B*22 == 8400`
- `A*34 + B*67 == 5400`

Our task is to solve for both `A` and `B` (the number of times we press each button). The best (only?) way to solve for two unknowns is to eliminate one of them, so let's start there.

If both equations have the same value for `B`, we can ignore it from both. So let's multiply each by the coefficient of `B` in the other:

```py
# step 1

67 * (A*94 + B*22 == 8400)
# => 6298*A + 1474*B == 562800


# step 1.5

22 * (A*34 + B*67 == 5400)
# => 748*A + 1474*B == 118800
```

Now that both equations have `1474*B`, we can subtract one from the other to eliminate it entirely:

```py
# step 2

(6298*A + 1474*B) - (748*A + 1474*B) == 562800 - 118800
# => (5550*A + 0*B) == 444000
```

The `B` disappears, leaving us with some basic division to find `A`:

```py
# step 2.5

# 5550*A      444000
# ------  ==  ------
#  5550        5550

A == 80
```

Now that we have one of our unknowns, we can use it to demystify the other (by plugging `A` back into either of our original equations):

```py
# step 3

A*94 + B*22 == 8400
# -> 80*94 + B*22 == 8400
# => 7520 + B*22 == 8400

7520 + B*22 == 8400
# -> B*22 == 8400 - 7520
# => B*22 == 880

# B*22     880
# ---- == -----
#  22      22

B == 40
```

Because each of `A` and `B` are integers, there is an even number of button presses that will solve this claw machine. So we can do the multiplication (`3*A + B`) and add it to our total.

Of course, the point is to solve these with Python, not by hand. We can write a function with all of the numbers from a piece of input:

```py
def find_intersection(
    a_x: int, a_y: int, b_x: int, b_y: int, x_prize: int, y_prize: int
) -> tuple[float, float]:
    ... # TODO
```

The argument ordering may seem a little strange, but it'll make more sense soon (when we parse our input). Now we do our same steps. The variable names are a little overly descriptive, but I was having trouble keeping everything straight. Readability is more important than clever naming!

```py
def find_intersection(
    a_x: int, a_y: int, b_x: int, b_y: int, x_prize: int, y_prize: int
) -> tuple[float, float]:
    # step 1
    a_x_with_b_y = a_x * b_y
    x_prize_with_b_y = x_prize * b_y
    # step 1.5
    a_y_with_b_x = a_y * b_x
    y_prize_with_b_x = y_prize * b_x
```

Next, we do step 2, subtracting and dividing everything that's got `B` in it:

```py
def find_intersection(
    a_x: int, a_y: int, b_x: int, b_y: int, x_prize: int, y_prize: int
) -> tuple[float, float]:
    ...

    # subtraction is step 2, division is step 2.5
    a = (x_prize_with_b_y - y_prize_with_b_x) / (a_x_with_b_y - a_y_with_b_x)
```

Lastly, we unwind our initial equation:

```py
def find_intersection(
    a_x: int, a_y: int, b_x: int, b_y: int, x_prize: int, y_prize: int
) -> tuple[float, float]:
    ...

    # step 3 as a 1-liner
    b = (y_prize - a_y * a) / b_y

    return a, b
```

Now to call it! A regex to find every number can pull our 6 values out of the input if it's treated as a big string:

```py
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        for block in self.input:
            vals = [int(s) for s in findall(r"\d+", block)]
```

Then all we need is to sum up the blocks for which both their `a` and `b` are nice round floats:

```py ins={11-22}
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        total = 0
        for block in self.input:
            vals = parse_ints(findall(r"\d+", block))

            a, b = find_intersection(*vals)
            if a.is_integer() and b.is_integer():
                total += a * 3 + b

        return int(total)
```

## Part 2

We're doing the same thing, but now it's way farther than we thought. Luckily, our algebraic approach works for basically any prize values, no matter how large.

All we need for part 2 is a conditional to increase our target. Since we can re-use part 1, I moved it all into a helper function:

```py rem={6,22} ins={7,11-13,23,25-26}
...

class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
    def _solve(self, increase_distance=False) -> int:
        total = 0
        for block in self.input:
            vals = parse_ints(findall(r"\d+", block))
            if increase_distance:
                vals[4] += PART_2_INCREASE
                vals[5] += PART_2_INCREASE

            a, b = find_intersection(*vals)
            if a.is_integer() and b.is_integer():
                total += a * 3 + b

        return int(total)

    def part_1(self) -> int:
        # previous code moved above
        return self._solve()

    def part_2(self) -> int:
        return self._solve(increase_distance=True)
```

My original implementation wasn't this clean, but it shows how far a clean code structure can go!
