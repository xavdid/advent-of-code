---
year: 2021
day: 16
title: "Packet Decoder"
slug: "2021/day/16"
pub_date: "2021-12-22"
---

## Part 1

Hoo boy- lots of reading here. The good news is that it's ultimately much simpler than it looks. Doesn't make it _easy_- there's a lot of opportunity for error and debugging can be tricky. But, we can break the problem down.

First things first: we need a function to turn a hex string (like `D2FE28`) into their component (padded) bits. Neither part of that ask (`hex -> int` or `int -> bin`) is particularly onerous:

```py
int('3', 16)
# => 3
int('d', 16)
# => 13

# ---

bin(3)
# => '0b11'
bin(13)
# => '0b1101'
```

One snag. Python's binary strings start with `0b` and aren't padded out to 4 bits. Above, `3` is `11`, not `0011` like we need it to be. There's a number of ways to fix this; we'll use maybe the neatest.

Python has a whole [mini-language for formatting strings](https://docs.python.org/3.10/library/string.html#formatspec)! You can dig into that (very formal) specification if you'd like, but the gist is that within `f'...'` or `'...'.format(...)`, you can use certain characters in a specific order to perform many common formatting tasks. In our case, we call it like so:

```py
x = 3
f'{int(x, 16):0>4b}'
# => '0011'
```

Bingo! This tells Python to format the string with the character `0` to the left (`>`) up to `4` places; also format the int as `b`inary. It's an opaque way to get exactly what we want! So we can wrap that in a list comprehension and we've got some helper functions:

```py
def bin_to_int(b: str) -> int:
    """
    '1101' -> 13
    """
    return int(b, 2)


def hex_to_bits(h: str) -> str:
    """
    'D2FE28' -> '110100101111111000101000'

    For each hex letter, returns a padded 4-bit binary string
    """
    return "".join([f"{int(x, 16):0>4b}" for x in h])
```

Sweet! Now we can start taking apart the prompt itself. Our input is a hex string that we need to parse into a nested series of packets. Each packet has some info at the front, and then one of 3 cases:

1. a binary number
2. 1+ sub-packets of a fixed length
3. a fixed number of sub-packets (of any length)

Let's put together a `Packet` class to store this info:

```py
class Packet:
    def __init__(self, raw_packet: str) -> None:
        self.length = 0  # the number of bits in this packet
        self.value = 0  # only used for literals, for now
        self.sub_packets: List["Packet"] = []
        self.raw_packet = raw_packet
```

Next, we need to be able to read a fixed number of bits off the front of the packet. Case 2 above needs to know exactly how long a sub-packet was, so let's wrap that whole operation in a method:

```py
class Packet:
    ...

    def pop_bits(self, num_bits: int) -> str:
        result = self.raw_packet[:num_bits] # grab the bits
        self.raw_packet = self.raw_packet[num_bits:] # advance the raw_packet
        self.length += num_bits # increment the running count
        return result
```

Now, back in `__init__`, we can read some info:

```py
class Packet:
    def __init__(self, raw_packet: str) -> None:
        ...

        self.version = bin_to_int(self.pop_bits(3))
        self.type = bin_to_int(self.pop_bits(3))
```

Everything is starting to come together! Next, our actual parsing. We'll start with the easy one, the literal. If `self.type` is `4`, then we want this branch. We'll grab 5 bits at a time. If the first one is a `0` we `break`, otherwise we keep going. Each time, we add the rest of the bits to a running list that we'll parse as a number when we're done. Here's how that looks:

```py
class Packet:
    def __init__(self, raw_packet: str) -> None:
        ...

        if self.is_literal:
            value_bits = []
            while True:
                last_marker, *segment = self.pop_bits(5)
                value_bits += segment
                if last_marker == "0":
                    break

            self.value = bin_to_int("".join(value_bits))

    @property
    def is_literal(self) -> bool:
        return self.type == 4
```

The only tricky thing here is the spread operator on `*segment`. This is a concise way to grab the first element and then the "`*rest`". At this point, you should be able to run the initial example. Give that a shot:

```py
# not part of actual solution!
p = Packet(hex_to_bits('D2FE28'))
print(p.value)
# => 2021
```

Next, the subpackets. If you haven't guessed, we'll be using recursion here. Each `Packet`, when created can contain subpackets (which, in turn, can have further subpackets until hopefully our input terminates). Here's how we'll do that:

```py
class Packet:
    ...

    def parse_subpacket(self) -> int:
        sub_packet = Packet(self.raw_packet)
        self.sub_packets.append(sub_packet)
        self.pop_bits(sub_packet.length)
        return sub_packet.length
```

That first line is what does the recursing; the rest is just housekeeping. We store the new packet at our root one, then advance our `raw_packet` by however long the subpacket was. This is important in all cases, since we want to continue parsing _after_ the end of the subpacket. Now we can pick back up on our 3 cases:

```py
class Packet:
    def __init__(self, raw_packet: str) -> None:
        ...

        if self.is_literal:
            ...
        elif self.pop_bits(1) == "0":
            bits_read = 0
            num_bits_to_read = bin_to_int(self.pop_bits(15))

            while bits_read < num_bits_to_read:
                bits_read += self.parse_subpacket()
        else:
            num_sub_packets = bin_to_int(self.pop_bits(11))
            for _ in range(num_sub_packets):
                self.parse_subpacket()
```

And that should do it! All the examples should parse correctly. The last thing is a function to sum up the versions and to call it:

```py
class Packet:
    ...
    def summed_versions(self):
        return self.version + sum([p.summed_versions() for p in self.sub_packets])

return Packet(hex_to_bits(self.input)).summed_versions()
```

---

Before we move on, let me pull back the curtain a second. My first draft of working code for this part was [very messy](https://github.com/xavdid/advent-of-code/commit/59d4b8d065b92c3f84ef4df484437162abcaf3eb#diff-5cd538158d2e0f222c9f00a308ac88d0af3576bbe920283f0af2ab4425ca896d). I've cleaned it up a lot for this post (and simplified the most error-prone blocks), but thought it might be helpful to see. When you've got a complex puzzle, get _something_ working and then clean it up later!

## Part 2

As we might have guessed, it's now time to actually put those `type`s to use. Our code doesn't have to change much- we'll mostly be adding a new method. Once all of our parsing is done on a given packet (regardless of where it was in the tree), we'll be able to calculate its value. Let's tweak `__init__` a little bit:

```py
class Packet:
    def __init__(self, raw_packet: str) -> None:
        ...

        if self.is_literal:
            ...
            self.value = bin_to_int("".join(value_bits)) # not new
        else:
            # moved all this under an else block
            if self.pop_bits(1) == "0":
                ...
            else:
                ...

            self.value = self.calculate_operator_value() # need to define this

    def calculate_operator_value(self) -> int:
        # TODO
        ...

        return 0
```

This is the part of building an interpreter (because that's what we're doing!) where the rubber meets the road. Now we translate compiled "machine code" into actual values that can be operated on. We'll use built-in Python functions to add/multiply/etc the `.value` of nested subpackets. Here's a first pass:

```py
from functools import reduce
from operator import mul

class Packet:
    ...

    def calculate_operator_value(self) -> int:
        subpacket_values = [p.value for p in self.sub_packets]

        op = self.type
        if op == 0:
            return sum(subpacket_values)
        if op == 1:
            # there's no `product` function, but this is how it would be defined if there was
            return reduce(mul, subpacket_values, 1)
        if op == 2:
            return min(subpacket_values)
        if op == 3:
            return max(subpacket_values)

        assert len(self.sub_packets) == 2
        l, r = self.sub_packets

        if op == 5:
            return int(l.value > r.value)
        if op == 6:
            return int(l.value < r.value)
        if op == 7:
            return int(l.value == r.value)

        raise NotImplementedError(f'Unknown operator: "{op}"')
```

Looks pretty ok! It certainly works, and we have our answer. We can clean it up though. Ultimately, this function has two parts

1. If it's `type` 0-3, call a function that takes 1+ items and returns a result
2. Otherwise it's `type` 5-7 and we call a function that takes exactly 2 numbers and returns a boolean

What if we declared all those functions separately and then called whichever one was appropriate. Here's how that looks:

```py
from functools import reduce
from operator import eq, gt, lt, mul
from typing import Callable, Dict, Iterable, List, Tuple

def product(seq: Iterable[int]) -> int:
    return reduce(mul, seq, 1)


OPERATOR_FUNCS: Dict[int, Callable[[Iterable[int]], int]] = {
    0: sum,
    1: product,
    2: min,
    3: max,
}

OPERATOR_COMPARISONS: Dict[int, Callable[[int, int], bool]] = {
    5: gt,
    6: lt,
    7: eq,
}
```

This approach uses the `operator` package (sounds relevant, right?), which holds the functions that power normal math operations. `1 < 2` is the same as `lt(1, 2)`. Being able to reference those operations explicitly allows us to build code where we don't know which function we're calling ahead of time. Now our calculation can be shrunk way down:

```py
class Packet:
    ...

    def calculate_operator_value(self) -> int:
        op = self.type

        if op in OPERATOR_FUNCS:
            return OPERATOR_FUNCS[op](p.value for p in self.sub_packets)

        assert len(self.sub_packets) == 2
        # throw a custom error if the assertion fails
        assert op in OPERATOR_COMPARISONS, f'Unknown operator: "{op}"'

        l, r = self.sub_packets
        return int(OPERATOR_COMPARISONS[op](l.value, r.value))
```

Boom! Much cleaner, but still easy to reason about.

One last bit of fun trivia before we go- the `int()` call on the last line isn't actually needed. In Python, `bool` is a subclass of `int`, so bools can be used in place of ints. For instance, `True + True` is `2`. But, it's a little more correct looking to return an actual `int`, so I did a final conversion.

If you enjoyed this sort of puzzle (interpreting opaque strings into actual programs), I recommend going through Advent of Code 2019, starting on [Day 2](https://adventofcode.com/2019/day/2). About half of the puzzles from that year involve creating an increasingly more complex version of today's puzzle. There's also [Writing an Interpreter in Go](https://interpreterbook.com/) if you want to explore some of the nuts and bolts.
