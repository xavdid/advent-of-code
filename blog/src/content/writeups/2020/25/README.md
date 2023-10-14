---
year: 2020
day: 25
title: "Combo Breaker"
slug: "2020/day/25"
pub_date: "2021-01-08"
---

## Part 1

For our final day, we'll be cracking the [Diffie–Hellman key exchange](https://en.wikipedia.org/wiki/Diffie–Hellman_key_exchange), the very foundation of the secure internet. Let's start with the `transform` function the prompt describes:

```py
def transform(subject_num: int, loop_size: int) -> int:
    value = 1
    for _ in range(loop_size):
        value *= subject_num
        value %= 20201227
    return value
```

We get the public keys from our input, so our task is to figure out what number(s) multiply into those pubic keys. We start at 1 and keep feeding potential loop size into that `transform` function until we get our card's public key:

```py
from itertools import count

card_public_key, door_public_key = self.input
card_loop_size = next(
    potential_loop_size
    for potential_loop_size in count(start=1)
    if card_public_key == transform(7, potential_loop_size)
)
```

`itertools.count` simply counts up. Easier than `for x in range(1, 10000...)` for some arbitrarily large number. In any case, that gives us our card's loop size.

Once we know that, we transform it with the door's public key, giving us the shared secret:

```py
return transform(door_public_key, card_loop_size)
```

That works for the example, but runs far too long for our actual program input. Let's speed it up. Our issue lies in the `transform` function.

There are a couple of patterns to take advantage of. Firstly, while `value` is less than `20201227`, the `%` operation doesn't do anything. So for number of loops, we're doing `1 * 7 * 7 * 7 * 7 * ...`. Instead of multiplying, we can save some time using an exponent: `7 ** loop_size` will get us the same result (assuming the result is less than `20201227`).

But what about when it's more than `20201227`? Turns out it just works. Wild, right? Because `Y % X` (when `Y > X`) has to be less than `X` and `Y % X` (when `Y < X`) is `Y`, we know that `Y % X == Y % X % X` (for any number of modulo operations).

So given all that, we only have to `% 20201227` once, no matter what exponent we raise `7` to.

```
7 % 20201227 * 7 % 20201227 * 7 % 20201227

is the same as

7 * 7 * 7 % 20201227 % 20201227 % 20201227

is the same as

7 * 7 * 7 % 20201227

is the same as

7 ** 3 % 20201227
```

With that simplification in hand, we no longer even need a loop. Our whole `transform` function is:

```py
def transform(subject_num: int, loop_size: int) -> int:
    # return subject_num ** loop_size % 20201227
    # --- or
    return pow(subject_num, loop_size, 20201227)
```

As luck would have it, Python's build-in `pow` function does exactly that.

With that one change, I got my puzzle answer in ~40 seconds. Tada! That's star number 49.

But heck, it's the last day, we can do it even faster. After profiling our solution, we see that `pow` takes _huge_ amounts of time. Getting a single exponent is pretty fast, but my final `card_loop_size` was nearly 18 million. So we're repeating a ton of work calculating exponents. When calculating, `7 ** 100`, we reuse most of the work from `7 ** 99`, but add another 7. Instead, we should save the previous result and multiply it by 7. That changes the shape of our loop, but should be familiar:

```py
card_public_key, door_public_key = self.input

val = 1
card_loop_size = None  # to help pylance
for card_loop_size in count(start=1):
    val = (val * 7) % DIVISOR
    if val == card_public_key:
        break

return pow(door_public_key, card_loop_size, DIVISOR)
```

With that, my solution clocked in at just under 2 seconds. Not a bad improvement!

## Part 2

If you've got all 49 stars up to this point, then all that's left is to press the button! Congrats! :tada:

Otherwise, [check the previous answers](https://github.com/xavdid/advent-of-code/tree/main/solutions/2020) and solve old puzzles until you're ready.

## One Last Thing

If you've gotten this far, I just want to say that I really appreciate you playing along with me. I've learned a lot writing these, and I hope you learned something reading them.

If you've got suggestions about the writing style, puzzle approach, or just want to say hi, please [get in touch](https://xavd.id/contact). I'd love to hear from you! Some days it feels like I'm writing into the void.

Anyway, until next year!
