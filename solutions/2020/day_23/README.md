# Day 23 (2020)

`Crab Cups` ([prompt](https://adventofcode.com/2020/day/23))

## Part 1

I started by trying to do a simple list and manage insertions and removals by slicing the array. Having to manage wrapping around the end of the list quickly got out of hand, so I had to go a different direction.

The puzzle doesn't care about the absolute position of the numbers in the list, just their order relative to each other. We can rotate the list freely as long as that's all we're doing. Doing that carefully will also make insertion much easier. A `deque` is perfect for this, since it handles rotation for us.

We'll start by parsing input and setting up our loop:

```py
cups = deque(map(int, self.input))
current_cup_value = cups[0]

for _ in range(100):
    ...
```

Now to fill in that `...`. Each step, we remove the 3 items after our `current`. So, let's put our `current` 4 from the end:

```py
assert current_cup_value in cups
while cups[-4] != current_cup_value:
    cups.rotate()
```

Note the `assert` statement. By validating in-code that our `while` loop will eventually exit, we protect ourselves from infinite loops.

Now we "pick up" cups by removing them from the list:

```py
to_insert = [cups.pop(), cups.pop(), cups.pop()]
to_insert.reverse()
```

Since Python statements are evaluated left-to-right, `to_insert` starts with the last item in the `deque`. Hence, we need to `reverse` our list so items retain their order. Next, finding the target and rotating the list:

```py
target_value = 9 if current_cup_value == 1 else current_cup_value - 1
while target_value in to_insert:
    target_value = 9 if target_value == 1 else target_value - 1

assert target_value in cups
while cups[-1] != target_value:
    cups.rotate()
cups.extend(to_insert)
```

The ternary statements there aren't the cleanest thing (and would need to be abstracted away if this was handling list lengths other than exactly 9), but it works. We've got another `assert`, after which our target is the last item in the list. Then we can re-add our removed cups.

Lastly, we need to reset our `current_cup_value`. This'll use the _very_ common pattern of `list[(something + 1) % len(list)]` for simulating a loop:

```py
current_cup_value = cups[(cups.index(current_cup_value) + 1) % 9]
```

Lastly, we rotate until `1` is at the front and join the rest as a string:

```py
assert 1 in cups
while cups[0] != 1:
    cups.rotate()

return "".join(map(str, cups))[1:]
```

## Part 2

This is a classic AoC move - part 1 can be solved by stepping through the puzzle instructions, but part 2 blows the numbers up so large that another, more technical approach is required. I couldn't come up with one off the top of my head, so let's adapt a Reddit solution, specifically [this one](https://www.reddit.com/r/adventofcode/comments/kimluc/2020_day_23_solutions/ggrtcop/).

We're going to use a design pattern common in academia called a [linked list](https://en.wikipedia.org/wiki/Linked_list).

Instead of storing a (very long) `deque` that we'll have to rotate many times per loop, we can use a structure with fast lookups (a `dict`) that point to `Node`s. We need to know the order of items though, so each value in the `dict` will have a pointer to the next `Node` in the sequence. You might think that this would take a lot of space, but it's quite efficient. Python variables are memory pointers, so all of the `Node`s are stored once and each just holds a little sign pointing to another. There's hardly any memory overhead at all.

... To be continued
