---
year: 2021
day: 24
title: "Arithmetic Logic Unit"
slug: "2021/day/24"
pub_date: "2022-02-17"
---

## Part 1

I started this so confidently. It seemed so straightforward! I whipped up a [proof of concept](https://gist.github.com/xavdid/bb3b304f614e048d138d54b2d3578cdf) of the ALU operations. I got to use [structural pattern matching](https://www.python.org/dev/peps/pep-0636/). It would try every 14-digit number until it hit. Only problem- it was way too slow. That's the problem with 14-digit numbers: there are a lot of them.

Most days, there's a more efficient ways to write our code that's too slow. Sometimes, we can do something clever with how we store our data, or take shortcuts during calculations. Today, we're going a different direction: we're going to reverse engineer our input.

Usually we treat the puzzle input as sort of a black box. We typically write a solution that works on the example, our input, and _any_ valid puzzle input. Today, we'll build a solution for our _specific_ input. As such, our code isn't not a general-purpose ALU implementation; given another valid ALU program, the solution won't produce the right output. But, it solves today's puzzle, and that's all that matters.

Before you read ahead, take 2 minutes and read over your puzzle input. Jot down everything interesting you notice. How many lines are there? Are there patterns in the input? What's consistent in that pattern, what isn't? For the numbers, try to add some constraints to them. Do they fall in a certain range, or set?

Do this for a minute or two, then read on to find what I found most helpful.

---

Digging in, we see that the input program follows a pattern. There are 14 nearly-identical 18-line blocks of instructions. We'll "call" them each in order. The blocks are identical except for 3 specific lines, which have a different number on each. These are lines `5`, `6`, and `16`. In my input, they follow a few simple rules:

1. `L5` is only ever `1` or `26`. There's exactly 7 of each in the 14 blocks
2. `L6` is always between `10` and `15` when `L5` is `1`. It's always negative when `L5` is `26` (my negative values were `<= -8`, but there's likely some variation)
3. `L16` is always a positive number (mine ranged from `1-16`, but there's probably range here too)

Let's walk through the first block of my input (translated into Python) and break down what we know. Your input will be similar, but will have different numbers on the `VAR` lines. Here's each step using `7` as the input digit:

```py
w, x, y, z = 0, 0, 0, 0

w = 7           # 1. read from input; can only be a single digit. Using 7 for example's sake

# top section
x *= 0          # 2. RESET X
x += z          # 3. X = Z = 0 (initially); Z will have a value in later blocks
x %= 26         # 4. 0 % 26 == 0; no-op
z //= 1         # 5. VAR; no-op when value is 1
x += 15         # 6. VAR; X = 15 + Z = 15
x = int(x == w) # 7. X == W? Always false, see below; X = 0
x = int(x == 0) # 8. X = !X; Always true, see below; X = 1

# middle section
y *= 0          # 9. RESET Y
y += 25         # 10. Y = 25
y *= x          # 11. Y = 25 * 1; no-op
y += 1          # 12. Y = 26
z *= y          # 13. Whatever Z was when we started (hasn't changed yet) * 26 = 0

# bottom section
y *= 0          # 14. RESET Y
y += w          # 15. Y = W = 7
y += 13         # 16. VAR; Y = 20
y *= x          # 17. Y = 20 * 1; no-op
z += y          # 18. Z = 20
```

As we step through it, we realize we can pull a lot of lines out

1. On `L4`, if Z was `> 26`, X is any value `0`-`25`. Otherwise, it's a no-op
2. Upon reaching `L6`, `X` is equal to the variable on that line + `Z % 26`
3. When we're in "`1`" mode, `L7` is always false because `X` + `< something greater than 10 >` will never equal the single digit we got as input
4. So, `L8` must always be true
5. `L11` is always a no-op when `L5` is `1`, because we established that `X` is always `1`
6. On `L18`, we set `Z` equal to the digit input (`7`) + the variable on `L16`. That's what get carried into the next block; everything else is reset

Given all those no-ops, we can simplify these mode-`1` blocks into the following Python function:

```py
def block_mode_1(digit, line_16_var, z=0):
    # top section - ignored
    # it sets X to 1 and then we multiply and divide by that result later
    # so we skip the whole thing

    # middle section
    z *= 26

    # bottom section
    return z + digit + line_16_var
```

That's a lot more approachable, right? In cases where `L6` is `1`, we multiply `Z` by `26` and add `digit` (which you choose) and whatever's in your puzzle input. Unfortunately, our ALU code needs to finish with `0` in the `Z` register- that'll never happen in a `1`-block (we only add and multiply). Let's take a peek at a `26`-block:

```py
w, x, y, z = 0, 0, 0, 20 # using the output of the last example

w = 7           # 1. read from input; can only be a single digit. Using 7 for example's sake

# top section
x *= 0          # 2. RESET X
x += z          # 3. X = Z = 20 (result of last 1-block
x %= 26         # 4. 20 % 26 == 0; no-op
z //= 26        # 5. VAR; Z = 0
x += -11        # 6. VAR; X = -11 + 20 = 9
x = int(x == w) # 7. X == W? No; X = 0
x = int(x == 0) # 8. X = !X; X = 1

# middle section
y *= 0          # 9. RESET Y
y += 25         # 10. Y = 25
y *= x          # 11. Y = 25 * 1; no-op
y += 1          # 12. Y = 26
z *= y          # 13. Whatever Z was when we started (20) * 26 = 9200

# bottom section
y *= 0          # 14. RESET Y
y += w          # 15. Y = W = 7
y += 6          # 16. VAR; Y = 13
y *= x          # 17. Y = 13 * 1; no-op
z += y          # 18. Z = 9213
```

Looks fairly similar, with an important difference: the variable on `L6` is negative. That means, depending on the value of `Z`, it's now possible that `L7` evaluates to `1`, meaning `L8` is `0`. That causes a big change in the rest of the block!

We can see that with `Z = 20` and `W` (our chosen input digit) equal to `7`, we were 2 short of our match on `L6`. But good news- we get to pick that value! Let's pick `9` instead. Here's how that plays out:

```py
w, x, y, z = 0, 0, 0, 20 # using the output of the block-1 example

w = 9           # 1. read from input; can only be a single digit.

# top section
x *= 0          # 2. RESET X
x += z          # 3. X = Z = 20 (result of last 1-block
x %= 26         # 4. 20 % 26 == 0; no-op
z //= 26        # 5. VAR; Z = 0
x += -11        # 6. VAR; X = -11 + 20 = 9
x = int(x == w) # 7. X == W? Yes! X = 1
x = int(x == 0) # 8. X = !X; X = 0; <--- big change!

# middle section
y *= 0          # 9. RESET Y
y += 25         # 10. Y = 25
y *= x          # 11. Y = 0
y += 1          # 12. Y = 1
z *= y          # 13. Z = 0 * 1 = 0

# bottom section
y *= 0          # 14. RESET Y
y += w          # 15. Y = W = 9
y += 6          # 16. VAR; Y = 15
y *= x          # 17. Y = 13 * 0 = 0
z += y          # 18. Z = 0 + 0 = 0!
```

That's more like it! This 26-block does the opposite of the 1-block. If X is made to match Z, everything gets reduced (or, if Z was small enough, zeroed out!).

So, we can re-write the 26-blocks as the following Python:

```py
def block_mode_26(digit, line_6_var, line_16_var, z):
    # top section
    x = z % 26 + line_6_var

    if x == digit:
        # if x is equal, the rest of the script is a no-op
        return z // 26

    # middle section
    z *= 26 # oh no

    # bottom section
    return z + digit + line_16_var
```

These blocks are the only chance we have to make Z smaller. Eventually, `Z` needs to be `0`. Since the `1`-blocks can only ever make Z bigger, it's important that _every_ one of these `26`-blocks returns early. How do we guarantee that though?

Well, whenever we enter one of these blocks, we get to pick `digit`. So, we need to do so strategically to ensure a match. Let's put everything we have together and simplify it for some clarity:

```py
def block_mode_1(digit_1,  line_16_var, z=0):
    return z * 26 + digit_1 + line_16_var

def block_mode_26(digit_2, line_6_var,  z):
    # top section
    x = z % 26 + line_6_var

    if x == digit_2:
        # if x is equal, the rest of the script is a no-op
        return z // 26

    return -1 # no match!
```

The `26`s cancel out (because of the mod division in the 2nd function)! That's awfully convenient. For the second function to return `0`, `digit_1 + line_16_var + line_6_var` must equal `digit_2`. Make sense? We can even verify this real quick:

```py
line_16_var = 15
line_6_var = -11 # copied from my puzzle input

for x in range(1,10):
    for y in range(1,10):
        z = block_mode_1(x, line_16_var)
        res = block_mode_26(y, line_6_var, z)
        if res == 0:
            print(x,y)
```

gives us:

```
1 5
2 6
3 7
4 8
5 9
```

Boom! That lines up exactly with what we're seeing. `1 + 15 - 11` equals `5`, so the second function is successful! Of course, there's more to it- there's a few `1`-blocks in a row, so values of `Z` will be pretty big before we get to the first `26`-block. Luckily, that's where that math in the middle with the `26`s works out.

Because of the way we multiply by 26 and then add an offset, we can roll back those operations later. Check it out:

```py
z = 0

# add 5, 9, then 3 during a few 1-block loops
z *= 26 # 0
z += 5 # 5
# ---
z *= 26 # 130
z += 9 # 139
# ---
z *= 26 # 3614
z += 3 # 3617


# now, unroll:
x = z % 26 # 3, the last number we added
z //= 26 # 139
# ---
x = z % 26 # 9, the second number we added
z //= 26 # 5
# ---
x = z % 26 # 5, the first number we added
z //= 26 # 0, tada!
```

So, using only basic math, we've got a system to that can add and remove values in a last-in-first-out pattern. Sounds a lot like a [stack](<https://en.wikipedia.org/wiki/Stack_(abstract_data_type)>)!

Our `1`-blocks "push" a number to the stack and our `26`-blocks (hopefully) "pop" them off! When done correctly, the stack is empty when the program finishes. We already have our little equation for the math to get a pair of operations to cancel out. All that remains is to line everything up correctly.

Now, finally, we can write some code!

---

As always, first we need to process our input. Looking at the simplified functions above, we only ever need two of the 3 variables: the operation (push or pop) and one of the other variables (push uses the `L16` variable while pop only needs the `L6`). We can walk through the input and store what we need:

```py
from dataclasses import dataclass
from typing import Iterable, List

# https://stackoverflow.com/a/312464/1825390
def blocks(l: List[str]) -> Iterable[List[str]]:
    """
    Yield each block of the program - 18 lines at a time
    """
    n = 18
    for i in range(0, len(l), n):
        yield l[i : i + n]

def get_int_from_line(line: str) -> int:
    """
    Get the integer we need from a given line
    """
    return int(line.split(" ")[-1])

PUSH_OP = 1


@dataclass
class Frame:
    # which place this frame represents in the final number
    digit: int
    # push or pop
    operation: int
    # the relevant variable for this operation
    var: int


stack: List[Frame] = []
result: List[str] = [""] * 14

for idx, block in enumerate(blocks(self.input)):
    op = get_int_from_line(block[4]) # either 1 or 26
    var = get_int_from_line(block[15 if op == PUSH_OP else 5])

    curr = Frame(idx, op, var)

    if curr.operation == PUSH_OP:
        stack.append(curr)
        continue
```

Pretty straightforward- we find our relevant lines and add them into the stack as a stack `Frame`. We keep pushing things onto the stack until we get a pop:

```py
for idx, block in enumerate(blocks(self.input)):
    ...

    # the higher-power number
    prev = stack.pop()

    # the pair of numbers must differ by this much
    diff = prev.var + curr.var
```

One last thing to figure out. What's the highest digit we can store? We know what the _difference_ between the two digits needs to be. So, to maximize our resulting number, one of the two digits should be `9` and the other one will be `9 - diff`. But, there's a catch- sometimes, the `diff` is negative! In that case, the earlier number should be `9` and the later number is `9 + diff` (which will make it a lower number. Here's that in action:

```py
result: List[str] = [""] * 14
...

for idx, block in enumerate(blocks(self.input)):
    ...
    if diff > 0:
        result[prev.digit] = str(9 - diff)
        result[curr.digit] = str(9)
    else:
        result[prev.digit] = str(9)
        result[curr.digit] = str(9 + diff)

assert all(result)
assert len(result) == 14
out = "".join(result)
assert len(out) == 14

return int(out)
```

We wrap it up with a _bunch_ of assertions that helped me catch some bugs, and we're all set!

## Part 2

Now, we need to find the lowest number instead of the highest. Luckily, all this takes is a tweak to our final logic. Instead of `9`s, we'll be using `1`s wherever we can. We can wrap the logic with a boolean to control the behavior:

```py
def _solve(self, find_high: bool) -> int:
    ...
    for idx, block in enumerate(blocks(self.input)):
        ...
        if find_high:
            ...
            # part 1
        else:
            if diff > 0:
                result[prev.digit] = str(1)
                result[curr.digit] = str(1 + diff)
            else:
                result[prev.digit] = str(1 - diff)
                result[curr.digit] = str(1)
```

Same basic idea, but inverted at each step. There's probably a cleaner way to do this, but this covered all my cases well and was clearer than any other ideas we had.

Great job today! It was tough to get started, but once we had a handle on what was going on, we breezed right through. Home stretch!
