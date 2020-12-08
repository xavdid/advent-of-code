# Day 7 (2020)

`Handy Haversacks` ([Prompt](https://adventofcode.com/2020/day/7))

## Part 1

All right, we're really getting into it now.

The question we ultimately need to answer for part 1 is:

> given a bag color, can it (or any of the bags it can hold) hold "shiny gold"?

First, we have to model this data. For part 1 we don't need to worry about the bag quantities, so we can ignore them.

Luckily, each line follows a partially predictable pattern:

The first part of the line is regular enough that we can pull it out:

```py
for line in self.input:
    this.mapping = {}
    # dull bronze bags contain 1 mirrored beige bag, 5 muted violet bags, 1 wavy lime bag.

    # this_bag holds these_bags
    this_bag, held_bags = s.split(' bags contain ')

    if 'no other bags' in held_bags:

        pass

    # ['dull bronze', '1 mirrored beige bag, 5 muted violet bags, 1 wavy lime bag.']

    held_bags = held_bags.split(', ')

    # ['1 mirrored beige bag', '5 muted violet bags', '1 wavy lime bag.']

    these_bags = []
    # just grab the adjective and color
    for bag in held_bags:
        bag_parts = bag.split(' ')
        these_bags.append(' '.join(bag_parts[1:3]))

    # ['mirrored beige', 'muted violet', 'wavy lime']

    this.mapping[this_bag] = these_bags
```

Now that we've got the parts split out, we need to store it. A string that maps to a list of string sounds a lot like a `Dict[str, List[str]]` to me! Let's store that as `self.mapping` (if your solution is in a class, like mine. Otherwise, declare `mapping = {}` at the very top of the file).

Now that we've got our `dict`, we need to check what each bag holds all the way down until we get to bags that don't hold anything (such as `faded blue` in the example).

Whenever you call a function repeatedly until you reach a "base case" is textbook [recursion](https://www.google.com/search?q=recursion). This can be an intimidating subject, but as long as you follow a couple of simple rules, you'll be in great shape!

### Rule 1: always start with your base case

In this function, we want to stop recursing if we definitively know whether or not the current bag can hold the gold bag:

```py
def can_hold_gold(self, bag) -> bool:
    if self.mapping[bag] == []:
        return False # definitely no
    if 'shiny gold' in self.mapping[bag]:
        return True # definitely yes
```

Assuming there's not a loop in the bags (red holds blue, which holds red), we'll eventually reach one of these two paths and our function will stop recursing. Awesome.

### Rule 2: return a calculation involving the function

Now the heady part. Given a bag that we don't have a definitive answer on, how do we calculate it?

We need to check if any bag that our bag holds can in turn hold `shiny gold`. So, we should return `True` if any bag in `self.mapping[bag]` returns true. Easy enough in code:

```py
...
return any([self.can_hold_gold(color) for color in self.mapping[bag]])
```

With those two sections, we can call `can_hold_gold` and count the number of times it returns `True`:

```py
return [self.can_hold_gold(bag) for bag in self.mapping].count(True)
```

All together, my solution ran in 0.363 seconds. Not too shabby!

But, we can do better with the magic of ✨Dynamic Programming✨. If that doesn't tickle your fancy, feel free to jump ahead to [Part 2](#part-2). Otherwise, read on.

Let's take a closer look at the first two lines of the example:

> light red bags contain 1 bright white bag, 2 muted yellow bags.
> dark orange bags contain 3 bright white bags, 4 muted yellow bags.

After calculating whether `bright yellow` can hold `shiny gold` in the first line (it can), we get to the second line and... start calculating whether `bright yellow` can hold `shiny gold`! In the little example this isn't a big deal, but in actual puzzle input, this could be very costly.

We can take advantage of the fact that a bag being able to hold `shiny gold` never changes. So once we know the answer, we can cache it in the mapping to speed up future checks of the same bag:

```py
def can_hold_gold(self, bag) -> bool:
    if isinstance(self.mapping[bag], bool):
        return self.mapping[bag]

    if not self.mapping[bag]:
        res = False
    elif "shiny gold" in self.mapping[bag]:
        res = True
    else:
        res = any([self.can_hold_gold(color) for color in self.mapping[bag]])

    # cache results for later
    self.mapping[bag] = res
    return res
```

The first time a function is called for a bag, it does the full calculation for every bag in its tree. The next time any of those bags are checked (as part of any other bag), the response will be instant.

Now my soultion runs in 0.016 seconds, a 22.7x improvement.

Breaking complex problems into small problems and caching the results is a technique called [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming#Computer_programming). It can lead to huge gains in the speed of recursive algorithms. A valuable tool to have in your toolbelt!

## Part 2
