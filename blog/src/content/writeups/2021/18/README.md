---
year: 2021
day: 18
title: "Snailfish"
slug: "2021/day/18"
pub_date: "2021-12-26"
---

## Part 1

I think this was the hardest day so far. I spun my wheels for a few hours exploring a solution I didn't end up being able to get working (or end up needing anyway). I'll walk through a bit of my though process here and how I got to my eventual solution.

After reading the prompt, the thing I was struggling the most with was how to store the data. The obvious answer is nested `tuple`s, just like they're presented in the input. But, the nesting means that we'll likely do operations using recursion. That would be well and good, but the fact that `explode` modifies _sibling_ items makes that really tough. It's hard to jump out of a function and find our way to a separate invocation. While thinking about it, I jotted down the following notes:

> - parse as strings? don't build nested tuples. can go left/right through the text and find other numbers. count paired brackets to get indentation level. do some replacements at index
> - come up with an indexing system for each regular number. depth and maybe overall position? make sure numbers can be absolutely ordered. could then maybe find the "left" of a given number.
> - actual nested tuples, but i'm not sure how the recursion would work. Each call of the function would know it's depth and would return the exploded result when looking at a pair- but i'm not sure how it could communicate changes to siblings

None of them jumped out as obvious answers, so I picked the option that seemed most reasonable- the second one. It avoids modifying raw strings and it avoids the recursion issues I was nervous about. So, I made myself a tiny class that I could modify. Mutability was a big advantage here, since I knew I'd be modifying these as I went. So, class rather that actual `tuple`:

```py
from dataclasses import dataclass

@dataclass
class Item:
    val: int
    depth: int


Pairs = List[Item]
```

I also wrote a function to turn a line from the puzzle input into a list of `Pair` objects:

```py
def num_to_pairs(n: str) -> Pairs:
    result = []
    depth = 0
    for c in n:
        if c == "[":
            depth += 1
        if c == "]":
            depth -= 1
        if c.isnumeric():
            result.append(Item(int(c), depth))
    return result
```

That part worked great. Now, here's where I went wrong. I assumed that to get the magnitude, I'd need re-create the pairs and nesting structure from the input. I wrote that dang function 3 separate hoping that I'd stumble on a solution. Eventually, I'd get stuck on because I wasn't able to decode a list of pairs all at the same level. The comma insertion and knowing when to add closing brackets was really messing me up. I got frustrated and took a step back. I ultimately needed that reconstruction to calculate the magnitude of a number- could I get that without fully decoding the pairs?

In a well-formed (balanced, etc) snail number, there must exist at least one pair that's only numbers. If we add both halves of it together, then it is now part of a pair that is only numbers (or it's half of one and there's a new "deepest"). If we keep adding pairs from the bottom up, we'll eventually have 2 items, which we'll combine into a single item, which is a number. This is no longer a valid snail number, but it _is_ the magnitude of the one we started with. Here's how that looks in code:

```py
def magnitude(pairs: Pairs) -> int:
    while len(pairs) > 1:
        max_depth = 0
        deepest_index = -1
        for i, p in enumerate(pairs):
            if p.depth > max_depth:
                deepest_index = i
                max_depth = p.depth

        deepest = pairs[deepest_index]

        left = 3 * pairs[deepest_index].val
        right = 2 * pairs[deepest_index + 1].val
        pairs[deepest_index] = Item(left + right, deepest.depth - 1)
        # the matching pair that we must know exists; it's been incorporated
        del pairs[deepest_index + 1]

    return pairs[0].val
```

Note that this modifies the input. That's usually frowned upon- it creates hard-to-find bugs where calling a function changes something you didn't expect to change. But, it means we don't have to copy/duplicate a bunch of class objects. So, in this specific case, we'll give it a pass.

Before we move on, we can fetch our max much more concisely:

```py
while len(pairs) > 1:
    ...

    deepest_index = max(range(len(pairs)), key=lambda i: pairs[i].depth)
    deepest = pairs[deepest_index]

    ...
```

`max`, like `filter` and others, takes a `key=` `kwarg`. This is useful for getting the max from an item with a non-obvious max, such as a custom class or a tuple. In this case, we're asking which index has the highest value, where that value is based on the `.depth` of the pair at that index. That's a trick I picked up from [this StackOverflow answer](https://stackoverflow.com/a/11825864/1825390) while trying to refine that code a bit.

Anyway, we don't actually need to reconstruct the input to get the result. So, we can freely `split` and `explode` on a list of `Pair`s. The rest ended up not being so bad.

First, exploding. If the `depth` of a `Item` is `5`, then:

- if we're past the first element, add this value to the previous element
- if there's an item to the right of the match in this pair (that is `i + 2` from this index), add the next value to that one
- then, delete the other item in this pair (`i + 1`)

Instead of doing `for p in pairs`, we'll do `while i < len(pairs)` so we can freely edit the list as we're moving through it. We return as soon as we make any changes, so this is pretty safe. Here's our `explode`:

```py
def explode(pairs: Pairs) -> bool:
    i = 0
    while i < len(pairs):
        p = pairs[i]
        if p.depth == 5:
            if i > 0:
                pairs[i - 1].val += p.val

            if i + 2 < len(pairs):
                pairs[i + 2].val += pairs[i + 1].val

            pairs[i] = Item(0, p.depth - 1)
            # delete next element
            del pairs[i + 1]
            return True
        i += 1

    return False
```

We do some bounds checking, but it's otherwise not so bad. The resulting `Item` is one level higher than our too-deep `Item`. `split` has a very similar setup:

```py
from math import ceil, floor

def split(pairs: Pairs) -> bool:
    i = 0
    while i < len(pairs):
        p = pairs[i]
        if p.val >= 10:
            val = p.val
            depth = p.depth

            p.val = floor(val / 2)
            p.depth += 1

            pairs.insert(i + 1, Item(ceil(val / 2), depth + 1))

            return True

        i += 1
    return False
```

Here, we move down a level (`depth + 1`) instead. `floor` and `ceil` let us round half of odd numbers correctly (`5.5` becomes `5` and `6` respectively). For both `explode` and `split`, we return `True` if we did _anything_ and `False` otherwise. That's important for our final step below.

Lastly is adding and reducing, which we can do as a single operation:

```py
def add_and_reduce(pairs: Pairs, to_add: Pairs) -> None:
    for p in to_add:
        pairs.append(p)
    for p in pairs:
        p.depth += 1

    # reduce!
    while True:
        if explode(pairs) or split(pairs):
            continue
        break
```

We use `.append` instead of `pairs += [...]` because we _want_ to modify the original list instead of re-assigning it. Then, we lower every item (since the whole pair is wrapped in a new layer). Last, we try to perform each of the `explode` and `split` operations. Remember the logic should be:

- explode the first available item
- if nothing explodes, split the first available item

If either of those happens, you start at the top of the list again. So, you could potentially explode multiple times before trying to split. Then, your first split causes more explosions and there's potentially a split-able item that sits for a while. Python's short circuiting behavior comes in clutch here. In an `X and Y` expression, if `X` is true, then `Y` doesn't get run at all. So, if `explode` happens, we skip `split` and start the loop again. If both functions return `False` (meaning they did nothing) then our number is all the way reduced and we can `break` out of the loop and exit.

With all that in place, we can actually solve our puzzle:

```py
pairs = num_to_pairs(self.input[0])
for line in self.input[1:]:
    add_and_reduce(pairs, num_to_pairs(line))
return magnitude(pairs)
```

## Part 2

This, like some previous days, is a speed check. If our code is fast enough, it's an easy day. If it's not, then we have some refactoring to do. Luckily, our solution is nice and fast, so the implementation is simple.

The only thing you may not be familiar with is `itertools.permutations`. It takes an iterable and gives us an iterator with every permutation of a given length for that input. The [docs](https://docs.python.org/3.10/library/itertools.html#itertools.permutations) explain it nicely:

> `permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC`

Because the prompt tells us that order matters, it's important that we use `permutations` instead of `combinations` (where order doesn't matter). The example looks perfect though! We'll get every possible pair of lines in both possible orders. Then, it's just calling our functions again:

```py
from itertools import permutations

max_res = 0
for a, b in permutations(self.input, 2):
    pairs = num_to_pairs(a)
    add_and_reduce(pairs, num_to_pairs(b))
    res = magnitude(pairs)
    max_res = max(max_res, res)

return max_res
```

If we had written our functions to return their results instead of modify input, we could instead write `max(magnitude(add_and_reduce(...))) for a, b in ...)`, but that won't quite work here. Not a big deal though, our code still works nicely. Let's call it a day.
