# Day 16 (2021)

`Packet Decoder` ([prompt](https://adventofcode.com/2021/day/16))

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
        self.value = 0  # only used for literals
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

### Tests

- basic literal `D2FE28`
- operator w/ num_packets `EE00D40C823060`
- operator w/ packet length `38006F45291200`
- nested `8A004A801A8002F478`

```

```
