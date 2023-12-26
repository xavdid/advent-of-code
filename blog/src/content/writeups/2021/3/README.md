---
year: 2021
day: 3
title: "Binary Diagnostic"
slug: "2021/day/3"
pub_date: "2021-12-03"
---

## Part 1

Though the binary math may look intimidating, we can actually avoid it entirely. At least in part 1, it's just a [red herring](https://en.wikipedia.org/wiki/Red_herring). Instead of binary numbers, think of them as strings where each character can only have a single value.

This would be easy enough to with an list of lists, each representing a "column" in the arranged input (the first character of each line). We could iterate through the input and then iterate through each line, adding the value to its matching list. Then we'd need to iterate each list and count the values. It would be a fair amount of code, but it _would_ work!

Luckily, we know a couple of Python tricks that will _drastically_ simplify this one.

There are two major things to tackle:

1. How to "rotate" the input
2. How to count the lists

Let's do them in order.

When I say "rotate", instead of a 3-length list where each element has length 5:

```py
[
    "00100",
    "11110",
    "10110",
]
```

We want a 5 item list where each element has length 3:

```py
[
    ("0", "1", "1"),
    ("0", "1", "0"),
    ("1", "1", "1"),
    ("0", "1", "1"),
    ("0", "0", "0"),
]
```

It might look hard, but we already know the function for this. It's `zip`, as mentioned in the bonus part of the [day 1 solution](/writeups/2021/day/1/#part-2). It takes many lists and gives you lists of the 1st element from each, the 2nd element from each, etc. But, all we have now are a single list of strings. We want to call `zip('00100', '11110', '10110')`, but we can't type that out ahead of time- it has to be dynamically called using our input.

Enter Python's "spread operator", the humble asterisk `*`. It tells Python that instead of passing this list to a function as a single list, transform it into individual arguments:

```py
l = [1,2,3]

def func(a, b, c):
    print(a, b, c)

func(l)
# => func() missing 2 required positional arguments: 'b' and 'c'

func(*l)
# => "1 2 3"
```

The spread operator lets us call `zip(*self.input)` and get the exact structure we need! :tada:

Next is counting. It's easy to do by hand, but Python's ever-helpful `collections` package includes a `Counter` class. Pass it an iterable (anything that can be iterated over) and it'll count how many times each element appears:

```py
from collections import Counter

Counter(("0", "1", "1"))
# => Counter({'1': 2, '0': 1})
```

Even better, it comes with a `most_common` method, which will sort the output:

```py
Counter(("0", "1", "1")).most_common()
# => [('1', 2), ('0', 1)]
```

So `some_counter.most_common()[0][0]` gives us the string which appears the most time.

Wrap that all up and we've got our gamma value:

```py
from collections import Counter

gamma = "".join(
   [
       Counter(place_values).most_common()[0][0]
       for place_values in zip(*self.input)
   ]
)
# => 10110
```

Because each line can only have 2 possible values, you know that for each most common character, the "opposite" one is the least common. So, we invert that string:

```py
epsilon = []
for c in gamma:
    if c == '1':
        epsilon.append('0')
    else:
        epsilon.append('1')
epsilon = ''.join(epsilon)

# or, shrunk down:

epsilon = "".join(["0" if c == "1" else "1" for c in gamma])
```

It's good not to pack _too_ much functionality into a single line, but in this case, I find it readable enough.

> savvy readers will notice that I broke my guideline from [literally yesterday](/writeups/2021/day/2/) where I cautioned against having an `else` at the end of a block to catch defaults. In this case, binary is _really does_ only have the two options, so it's safe enough.

All that's left is to convert our answers from a string to a binary number, and multiply them:

```py
return int(gamma, 2) * int(epsilon, 2)
```

The `2` here tells Python to parse the input as a "base 2", or "binary" number. Other types of numbers work too, such as `8`, `16`, and our default counting system of `10`.

## Part 2

Part 2 is definitely an exercise in reading comprehension. It's similar to part 1, but we're filtering the list as we go, so we can't _just_ `zip` our whole `self.input`. Instead, we'll have to get a count of the bits in a given position for all remaining numbers. Easy enough:

```py
place_to_check = 0
values = self.input
counts = Counter([i[place_to_check] for i in values])
```

That works for our first loop, but we'll have to make it more dynamic as we shrink that list down. We'll circle back to that though- let's finish our algorithm first. We need to build a `result` that has the bits that our answer should start with. We get that value from `counts` depending on which of the two is higher:

```py
...
result = ""
if counts["1"] > counts["0"]:
    result += "1"
elif counts["0"] > counts["1"]:
    result += "0"
else:
    result += "1"
```

Then, we re-filter our values to keep only those that start with the right sequence:

```py
values = [n for n in values if n.startswith(result)]`
```

Python's `.startswith` makes this easy, as does being able to include an `if` statement in a list comprehension.

Our current approach works great for the first loop, but we need to plug wire everything else together. We can wrap the above in a `while` loop, which keeps going until we've got exactly 1 value left. We can also ditch manually tracking `place_to_check`, since it'll be the same as `len(result)`. So, all together:

```py
values = self.input
result = ""

while len(values) > 1:
   place_to_check = len(result)
   counts = Counter([i[place_to_check] for i in values])
   if counts["1"] > counts["0"]:
       result += "1"
   elif counts["0"] > counts["1"]:
       result += "0"
   else:
       result += "1"

   values = [n for n in values if n.startswith(result)]
```

When the loop exits, we'll have a `values` list with exactly one item, which is the `02` result. The process for `C02` is similar, but what goes into `result` changes - it takes the less popular option and `0` in case of ties. So, let's put our algorithm in a function and make it configurable:

```py
from typing import Literal, Union
one_or_zero = Union[Literal["0"], Literal["1"]]

class Solution(StrSplitSolution):
    ...

    def filter_list(
        self,
        val_if_1_higher: one_or_zero,
        val_if_0_higher: one_or_zero,
        val_if_tied: one_or_zero,
    ) -> str:
        values = self.input
        result = ""

        while len(values) > 1:
            place_to_check = len(result)
            counts = Counter([i[place_to_check] for i in values])

            if counts["1"] > counts["0"]:
                result += val_if_1_higher
            elif counts["0"] > counts["1"]:
                result += val_if_0_higher
            else:
                result += val_if_tied

            values = [n for n in values if n.startswith(result)]

        return values[0]
```

Same basic idea, but we can manually specify what happens in each of the 3 cases. This makes our final puzzle solution:

```py
o2 = self.filter_list("1", "0", "1")
co2 = self.filter_list("0", "1", "0")
return int(o2, 2) * int(co2, 2)
```
