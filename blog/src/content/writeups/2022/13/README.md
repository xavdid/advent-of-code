---
year: 2022
day: 13
title: "Distress Signal"
slug: "2022/day/13"
pub_date: "2022-12-13"
---

## Part 1

Rather than start on the input parsing, I decided to [eat the frog](https://asana.com/resources/eat-the-frog) and write the `is_ordered`, which will hold most of the logic. There's nothing too technical - we're carefully following the instructions in the prompt.

It takes an `int`, a list of `int`, or a list of list of int, or... you get the idea. Python supports recursive types, so we can type it like so:

```py
Packet = int | list["Packet"]
```

Knowing that each of the two arguments to this function lets us add our first logic branch:

```py
...

# note - this bool | None syntax requires Python 3.10+
def is_ordered(left: Packet, right: Packet) -> bool | None:
    if isinstance(left, int) and isinstance(right, int):
        if left == right:
            return None
        return left < right
```

For our purposes, we'll use `None` for ties, meaning whatever is calling should continue to the next case, if available.

There are 3 other cases to consider with 2 arguments:

1. 2 lists
2. left `list`, right `int`
3. left `int`, right `list`

The logic on the first option is tricky, so we'll defer that. We can fill in the rest though:

```py
...

def is_ordered(left: Packet, right: Packet) -> bool | None:
    if isinstance(left, int) and isinstance(right, int):
        ...

    if isinstance(left, list) and isinstance(right, list):
        # TODO

    if isinstance(left, list):
        # list, int
        return is_ordered(left, [right])

    # int, list
    return is_ordered([left], right)
```

That covers our main branches. The last thing is to handle lists. We need to compare the first element of `left` with the first element of `right`, second element of each, etc. Sounds like a job for `zip`! But, like [day 5](/writeups/2022/day/5/), we need to use `functools.zip_longest` so that we know when one of the lists has ended. The potential to pass `None` as `left` or `right` requires an update to our branches:

```py
def is_ordered(left: Packet | None, right: Packet | None) -> bool | None:
    # right is smaller, not sorted
    if right is None:
        return False
    # left is smaller, sorted
    if left is None:
        return True

    ...

    if isinstance(left, list) and isinstance(right, list):
        for l, r in zip_longest(left, right):
            if (res := is_ordered(l, r)) is not None:
                return res
        return None

    ...
```

We look at each item and return a `bool` if we got one. If we didn't, we keep going, eventually returning `None` if the tie was never broken. And that'll do it!

Next, input parsing. AoC was kind enough to structure each line of input as valid Python, so we can use the `eval` family of functions to parse it as such. Normally, this is terribly unsafe; anything in the input gets executed in you program context. It could read secret variables, change program state, anything. Don't use the global `eval` function.

Instead, Python supplies the `ast.literal_eval` function. The [docs](https://docs.python.org/3.11/library/ast.html#ast.literal_eval) note that:

> Evaluate an expression node or a string containing only a Python literal or container display. The string or node provided may only consist of the following Python literal structures: strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None and Ellipsis. This can be used for evaluating strings containing Python values without the need to parse the values oneself.

Because it only recognizes basic Python primitives (lists, numbers, etc), it's saf-_er_ to use. Still probably worth scrutinizing your input closely, but you're less likely to let someone totally hack you this way (like [this meme suggests](https://i.redd.it/i8yweil4xl5a1.png)).[^1] So, we can run a line through `literal_eval` and get a Python-native version of the input! Combine that with totaling up the indexes if `is_ordered` is truthy, and we're done with part 1.

```py
class Solution(StrSplitSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        total = 0
        for index, block in enumerate(self.input):
            left, right = map(literal_eval, block.split("\n"))
            if is_ordered(left, right):
                total += index + 1

        return total
```

## Part 2

While part 1 verified that our basic algorithm was correct, part 2 has us actually using it. To start, we'll parse our input into a single flat list (plus the 2 additional `Packet`s):

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        divider_1: Packet = [[2]]
        divider_2: Packet = [[6]]
        flat_packets: list[Packet] = [divider_1, divider_2]
        for block in self.input:
            for packet in block.split("\n"):
                flat_packets.append(literal_eval(packet))

        # TODO: sort the list

        return (flat_packets.index(divider_1) + 1) * (flat_packets.index(divider_2) + 1)
```

As luck would have it, Python is great at sorting lists. All it needs is for us to tell it how to do so (something I touched on briefly yesterday). Now, we'll take a closer look at what exactly goes into the `key=` kwarg when sorting a list.

Ultimately, to sort a list, Python needs a sortable object. An object is sortable if it implements `__lt__`, allowing it to be compared to other similar objects. The function you use in `key` should return an object that is sortable. Sometimes, that's picking a specific `int` out of an object, but for our (potentially deeply nested) list, that's not so easy. We could write a class for `Packet` which implements this, but there's an easier way.

In older versions of Python, you used to write custom sorts using comparator functions. They took 2 elements (`a` and `b`) and would return:

- `-1` if `a` and `b` are correctly ordered (`a < b`)
- `0` if `a` and `b` are equal and don't need to be swapped (`a == b`)
- `1` if `a` and `b` are in the wrong order and _do_ need to be swapped (`b < a`)

Sound familiar? If we can turn calls to `is_ordered` into a sortable object, we can use it as our `key` function! And, best of all, Python provides this in `functools.cmp_to_key`. All we need is a little function that translates our `bool` outputs to `1` or `-1` (the lists in input are never equal). We can wrap it all in a little `lambda`:

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        ...

        flat_packets.sort(key=cmp_to_key(lambda l, r: -1 if is_ordered(l, r) else 1))

        return (flat_packets.index(divider_1) + 1) * (flat_packets.index(divider_2) + 1)
```

And that'll do it!

[^1]: Another option that I'm embarrassed to realize didn't occur to me is using to `json.loads`, since each line is valid JSON. I had eval on the mind though, since I _almost_ used it for [day 11](/writeups/2022/day/11/)'s equations.
