---
year: 2021
day: 6
title: "Lanternfish"
slug: "2021/day/6"
pub_date: "2021-12-06"
---

## Part 1

I'm calling it now - this smells of a classic AoC problem where part 1 is brute-forcable and part 2 will _seem_ like it works the same way, but you do too many days and it turns out your code is way too slow.

But, until then, we can sort of just step through the instructions. We've got a list of numbers. We iterate through that list to make a new one following a couple of rules:

- if the number is `0`, replace it with `6` and add an `8` to the end
- otherwise, replace it with `number - 1`

And honestly, it's that easy:

```py
result = self.input
for _ in range(80):
    new_result = []
    num_births = 0
    for fish in result:
        if fish == 0:
            new_result.append(6)
            num_births += 1
        else:
            new_result.append(fish - 1)
    result = new_result + num_births * [8]

return len(result)
```

We go through our `result` and populate the `new_result`; then we swap them and do it all over again! The only odd thing here is the last line of the loop: `new_result + num_births * [8]`. This relies on Python's ability to multiply (most) iterables:

```py
[3] * 3
# => [3, 3, 3]
'cool' * 3
# => 'coolcoolcool'
```

It can also add lists:

```py
[1] + [2]
# => [1, 2]
```

Put those together and you get:

```py
new_result = [1, 2, 3]
num_births = 3

result = new_result + num_births * [8]
# => [1, 2, 3, 8, 8, 8]
```

:sparkles: The more you know!

## Part 2

Boom. My part 1 finished instantly and part 2 hung long enough that I gave up. We'll have to think of another, faster way to store our lanternfish counts.

The key here is that all laternfish that share a number have the same result. So rather than calculate each fish's update individually, we can just keep a _count_ of the number of fish of each age and add them all together. This is a good example of _algorithmic complexity_ (an important Computer Science concept I [touched briefly on](/writeups/2021/day/4/) in day 4). Our part 1 approach got slower as the days went on, since our list of fish kept getting longer. Our new approach will take the same amount of computation every day, since we're only ever storing (up to) 8 numbers. That's known as "constant time complexity", which is a great "score" for an algorithm.

We'll rely here on Python's `collections.defaultdict`. While a regular `dict` throws an error if you access a missing key, `defaultdict` uses a specified default instead:

```py
from collections import defaultdict

reg = {}
d = defaultdict(int) # missing keys are 0

reg['a'] += 1
# => KeyError: 'a'

# Instead, we need to write:
if 'a' in reg:
    reg['a'] += 1
else:
    reg['a'] = 1

# or, as a one-liner:
# reg['a'] = reg.get('a', int()) + 1

# with a defaultdict, it "just works":
d['a'] += 1
```

We can also use `collections.Counter`, which is Python's implementation of the [multiset data structure](https://en.wikipedia.org/wiki/Multiset). In this case, it has the same utility as using `collections.defaultdict` with a factory method parameter of `int`, but `Counter` has some nice utility methods when we want to reason about the counts of individual items:

```py
from collections import Counter

c = Counter()

c['a'] += 1
c['b'] += 2

for item, count in c.most_common():
    print(f'The value "{item}" has cardinality {count} in our counter.')
```

Using either a `defaultdict` or a `Counter`, we can confidently add numbers to keys in the dict without knowing if they're there or not. So, here's our solution for both parts:

```py
from collections import defaultdict

part_1 = 0

result = defaultdict(int)

# build initial state
for i in self.input:
    result[i] += 1

for day in range(256):
    # store our part_1 answer early
    if day == 80:
        part_1 = sum(result.values())

    new_result = defaultdict(int)
    for fish, num in result.items():
        if fish == 0:
            # add instead of set because there could already be some 6's
            new_result[6] += num
            # the only thing that can make 8's is 0, so we can just set.
            # but it's a little safer to always add
            new_result[8] += num
        else:
            new_result[fish - 1] += num
    result = new_result

return part_1, sum(result.values())
```

It should look pretty similar to part 1, but our operations use the `dict` instead of the `list`. Otherwise, smooth sailing!

> The following solutions were contributed by [Andrew Szeto](https://github.com/jabagawee)

## Alternate solution 1: Yet another data structure (deque) from the collections module

In our `defaultdict` based solution above, note that we never exceed nine keys in the dict (and those nine keys are always the integers 0 through 8). We generated new dicts after every simulated day by moving values down from a key `n` to the key `n-1`, we moved the key `0` to the key `8`, and then we did some extra work to add the value from the old key `0` to the new key `6`. This entire operation sounds exactly like the `rotate` method on the `collections.deque` class, so let's give that a shot too.

```py
from collections import deque

fish_per_count = deque([self.input.count(i) for i in range(9)], maxlen=9)
for i in range(1, 256 + 1):
    # all the fish due for reproduction are about to also reset their
    # counters to 7, which will be immediately decremented to 6
    fish_per_count[7] += fish_per_count[0]
    fish_per_count.rotate(-1)
    if i == 80:
        part_1 = sum(fish_per_count)

return part_1, sum(fish_per_count)
```

A lot of the bookkeeping and management of state are abstracted away when we recognize that the ticking down of every fish's reproductive counter and the looping at 0 can be represented by the rotation of indices in a list. This solution takes advantage of the fact that list indexing and dict indexing look almost identical if the following assumptions are true:

- keys are integers, and
- keys that are non-existent in the dict effectively have a value of 0.

## Alternate solution 2: Dynamic programming

Instead of procedurally simulating the process of lanternfish reproduction ourselves, we can also recruit the computer's help in doing so via [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming). By breaking down our problem into successively smaller subproblems and explicitly solving the simplest subproblem, we can rely on the computer to build the solution back up from the broken-down parts. For any given fish a certain number of days away from reproducing, we can define the total number of fish that will arise from that fish after a certain number of days like so:

```py
def num_fish(reproduction_counter, days):
    # in the simplest case, a fish on a certain day only counts for one fish.
    # it may reproduce tomorrow, but we are counting it today.
    if days == 0:
        return 1
    # in the special case, a fish will reset its `reproduction_counter` back to 6.
    # it will also generate a new fish with a `reproduction_counter` of 8.
    if reproduction_counter == 0:
        return num_fish(6, days - 1) + num_fish(8, days - 1)
    # in all other cases, this fish will produce the same number of family members
    # as a fish one day older than itself that will be counted one day earlier.
    return num_fish(reproduction_counter - 1, days - 1)
```

Given that the return value of this function can only be `1` or the sum of two more calls to itself, this approach has similar space and time complexity as our part 1 solution; if the solution to the problem is N, there will be O(N) calls to this method. In fact, it made worse by the fact that every fish that is counted at `days == 0` could have up to 8 stack frames above itself, though that is a constant multiple and generally not as concerning as the numbers grow. We can solve this by removing duplicated work, ie caching our intermediate results. In the Python standard library, `functools.lru_cache` serves as an easy-to-use cache implementation. The LRU in the name tells us that if the cache gets full, it evicts the _least recently used_ entries from the cache. In our case, we know that the function should only be called with `reproduction_counter` $\in [0..8]$ and `days` $\in [0..128]$, so we can add our cache decorator like so:

```py
from functools import lru_cache

@lru_cache(maxsize=9*129)
def num_fish(reproduction_counter, days):
    ...

part_1 = sum(num_fish(original_fish, 80) for original_fish in self.input)
part_2 = sum(num_fish(original_fish, 128) for original_fish in self.input)
```

Even though it may look like we are duplicating work by calculating up to day 80 twice, the caching decorator saves our intermediate results and lets us write code that is less concerned with implementation details and more concerned with readability and correctness.
