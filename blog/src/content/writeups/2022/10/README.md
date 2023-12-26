---
year: 2022
day: 10
title: "Cathode-Ray Tube"
slug: "2022/day/10"
pub_date: "2022-12-11"
---

## Part 1

I'll be honest, today looked intimidating. I was worried that tracking which parts of my program were supposed to happen before/during/after the cycle would be really tricky. All it took were some well placed comments and I was feeling better about it.

The other tricky thing to wrap your head around is that unlike most days, we're not iterating over `self.input`. Instead, we're counting up the current `cycle` and reading selectively from `self.input`.

Anyway, the code. First things first, we need the bones of our solution. We're counting up to 220 cycles, so we can wrap everything in a `range`:

```py
REPORTING_CYCLES = {20, 60, 100, 140, 180, 220}

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        result = 0

        x = 1 # starts at 1, not 0!

        for cycle in range(1, 221):
            # start cycle!

            if cycle in REPORTING_CYCLES:
                result += cycle * x

            # end cycle!

        return result
```

So far so good. We know where to put the code that happens during and after each cycle. Our answer calculation is set up right (except that `x` never changes, we'll fix that soon).

Next are the instructions! Instead of iterating through them each time there's a cycle, we need to store and increment an index that points to the instruction we're currently processing. We'll increment that after a cycle if we completed an `addx` instruction or if it was a `noop`. So, we also need code to track if we're processing an `addx`. Lastly, we should apply modifications to `x` Let's put that all in:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ... # initialize values
        instruction_pointer = 0
        in_addx = False
        for cycle in range(1, 221):
            # start cycle!

            instruction = self.input[instruction_pointer].split()
            addx = 0

            if instruction == ["noop"]:
                pass
            elif instruction[0] == "addx":
                in_addx = False
                addx = int(instruction[1])
            else:
                in_addx = True

            ... # report values

            # end cycle!

            if not in_addx:
                x += addx
                instruction_pointer += 1

        ...
```

With that code in place, we'll start an `addx` instruction during a cycle and we won't modify `x` until after the next cycle. We also store the modification to `x` and apply it as needed. Then, once we've finished the instruction (by modifying `x`), we increment our instruction index.

It's a little funny looking, but it works swimmingly. On to part 2!

## Part 2

This is another one that takes some time to wrap our head around. The value of `x` is actually represents a small range. If our `cycle` is within that range (during the cycle) then we light up a pixel. Otherwise, we don't. Luckily, we don't have much code to add!

```py
class Solution(StrSplitSolution):
    # renamed part_1 -> solve
    def solve(self) -> Tuple[int, str]:
        ...
        pixels = []
        # update 221 -> 241
        for cycle in range(1, 241):
            # start cycle!

            ...

            if x - 1 <= (cycle - 1) % 40 <= x + 1:
                pixels.append("#")
            else:
                pixels.append(".")

            # end cycle!

            ...

        print()
        print(
            "\n".join(
                "".join(l) for l in [pixels[i : i + 40] for i in range(0, 241, 40)]
            )
        )
```

`x` is actually the range of `(x-1, x+1)`, so we check if `cycle` (shifted to a 0-index, mod 40) is in that range.[^1] That part is straightforward enough, but our printing bears breaking down a little bit.

This is actually the same algorithm we used in [day 3](/writeups/2022/day/3/#part-2) to get chunks from a list. For reach chunk, we join all of the pixels in that slice (which is exactly 40-long), and then join those stringified lines with newlines to make a little monitor. We could have also broken it out like this:

```py
lines = []
for i in range(0, 241, 40):
    lines.append(''.join(pixels[i : i + 40]))

print("\n".join(lines))
```

But, we might as well nest some list comprehensions at the finish line.

[^1]: It wasn't until my little monitor printed a correct-looking first line and a blank rest of everything did I realize the `% 40` was important here.
