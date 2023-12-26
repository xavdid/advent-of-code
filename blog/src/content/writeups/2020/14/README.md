---
year: 2020
day: 14
title: "Docking Data"
slug: "2020/day/14"
pub_date: "2020-12-15"
---

## Part 1

I found this prompt very hard to parse, but the puzzle itself is straightforward. The prompt mentions a computer, but it's not the one we wrote on [day 8](/writeups/2020/day/8/). In fact for our purposes, it's a humble `dict`. We're going to be writing numeric values at string keys.

Lines of input come in two forms. Either:

- `mask = <LONG_STRING>`
- `mem[<NUMBER>] = <NUMBER_2>`

If we get a `mask` line, we store that value. If we get a `mem` line, we're writing values into the aforementioned storage. The basic setup is simple:

```py
mem = {}
mask = ""

for line in self.input:
    if line.startswith("mask"):
        mask = line.split(" = ")[1]
    else:
        ...
```

Let's zoom in on that `else` block. The first thing to do is parse out the values from that line. While we could do some surgical `split`ting, but a regex will be fewer lines. I won't go into all of regex here, but will callout a great Python-specific feature: **named capture groups**. While all regex engines can denote capture groups with `()`, Python lets you name them!

```py
import re
s = 'mem[42] = 100'

# without named groups
noname = re.match(r'mem\[(\d+)\] = (\d+)', s)
address, value = noname.groups() # => ('42', '100')

# with names
named = re.match(r"mem\[(?P<address>\d+)\] = (?P<value>\d+)", s)
named.group('address') # '42'
named.group('value') # '100'
```

It's not much on a regex this small, but it confers a lot of readability. Either way, we can extract out the `address` and `value` (as strings). Next, we've got to do some conversion.

First up is turning a number into a padded binary string. Sounds a little imposing, but Python's `bin`(ary) and `rjust` functions make short work of it:

```py
int_to_padded_binary = lambda i: bin(i)[2:].rjust(36, "0")
```

A couple of points of interest:

- it's a lambda function since it's a little one-liner. It could be a regular function too, but it being so simple lets us slim it down
- there are a _lot_ of ways to do do this and they're all equally correct
- the `bin` function returns the number with a leading `0b`. Normally this is fine, but if we further pad the result, we get things like `000000b1010`, which _isn't_ valid. So we drop the prefix with `[2:]`

With that in hand, we've got both our padded binary and our mask, so we're ready to tackle the example!

> value: 000000000000000000000000000000001011 (decimal 11)
> mask: XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
> result: 000000000000000000000000000001001001 (decimal 73)

It's exceedingly convenient that both strings are the same length; this allows us to take full advantage of Python's `zip` function. It takes two iterables and gives us pairs:

```py
list(zip('ABCD', '1234'))

# [('A', '1'), ('B', '2'), ('C', '3'), ('D', '4')]
```

We need to go through each matching character from the mask and value and sometimes replace the value character if the mask character isn't an `X`:

```py
def apply_mask_to_int(mask: str, i: int) -> str:
    res = []
    for mask_val, target_val in zip(mask, int_to_padded_binary(i)):
        if mask_val != 'X':
            res.append(mask_val)
        else:
            res.append(target_val)
    return ''.join(res)
```

Not so bad! We can make it a list comprehension without losing much clarity:

```py
def apply_mask_to_int(mask: str, i: int) -> str:
    return "".join(
        [
            mask_val if mask_val != "X" else target_val
            for mask_val, target_val in zip(mask, int_to_padded_binary(i))
        ]
    )
```

Now we call that from our `else` block above:

```py
data = re.match(r"mem\[(?P<address>\d+)\] = (?P<value>\d+)", line)

mem[data.group("address")] = int(
    apply_mask_to_int(mask, int(data.group("value"))),
    2
)
```

We call `int` twice:

- once to turn our regex-extracted `value` from a string to a number
- once to turn our padded binary back into a regular number. Note the call is a little different: `int(padded, 2)`, which tells the `int` function to convert from base-2 (aka binary)

To wrap up, we add up all the values stored in memory:

```py
return sum(mem.values())
```

## Part 2

Part 2 is mostly the same as part 1 - the big difference is that the bitmask is applied to the key instead of the value:

```py
mem = {}
mask = ""

for line in self.input:
    if line.startswith("mask"):
        mask = line.split(" = ")[1]
    else:
        data = re.match(r"mem\[(?P<raw_address>\d+)\] = (?P<value>\d+)", line)

        ...

return sum(mem.values())
```

Let's fill in that `...`! First, our mask application is slightly different. Now, we replace the value if anything but `0`. Easy enough:

```py
def apply_mask_to_int_v2(mask: str, i: int) -> str:
    return "".join(
        [
            target_val if mask_val == "0" else mask_val
            for mask_val, target_val in zip(mask, int_to_padded_binary(i))
        ]
    )
```

And we'll call it from that `else`:

```py
floating_mask = apply_mask_to_int_v2(
    mask, int(data.group("raw_address"))
)
```

Now the tricky part. We have to use this same mask repeatedly and replace the `X`s differently each time. If we look at their examples, we see a pattern:

> ...X1101X becomes:

> ...**0**1101**0** => 00
> ...**0**1101**1** => 01
> ...**1**1101**0** => 10
> ...**1**1101**1** => 11

Keen readers will clock that replacement as counting up in binary with leading zeroes! We replace `X` with padded binary representations of 0, then 1, 2, etc.

Because each `X` can have 2 values, a mask will write to `2 ^ num_x` addresses (2 `X`s is 4 addresses, 3 is 8, etc). The really sneaky thing is replacing the `X`s one at a time. Luckily, Python's `string.replace` function takes an argument to control the number of replacements. So if we iterate through the padded binary, we can replace one `X` at a time. This is doable with a small tweak to our padding function:

```py
int_to_padded_binary = lambda i, l=36: bin(i)[2:].rjust(l, "0")
```

Very similar to before, but the length of the padding is now configurable (and defaults to 36, so no code changes in part 1 are necessary). Now, the good stuff:

```py
def resolve_floaters(mask: str) -> int:
    num_x = mask.count("X")
    num_combos = 2 ** num_x

    for i in range(num_combos):
        res = mask
        # only want to pad for the Xs we have
        replacements = int_to_padded_binary(i, num_x)
        for digit in replacements:
            # each time we loop, another X disappears
            res = res.replace("X", digit, 1)
        # send back a regular number
        yield int(res, 2)
```

The `yield` keys you into the fact that we'll iterate over the results of this function, which we do in the `else` block:

```py
for address in resolve_floaters(floating_mask):
    mem[address] = int(data.group("value"))
```
