# Day 6 (2021)

`Lanternfish` ([prompt](https://adventofcode.com/2021/day/6))

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

:sparkle: The more you know!

## Part 2

Boom. My part 1 finished instantly and part 2 hung long enough that I gave up. We'll have to think of another, faster way to store our lanternfish counts.

The key here is that all laternfish that share a number have the same result. So rather than calculate each fish's update individually, we can just keep a _count_ of the number of fish of each age and add them all together. This is a good example of _algorithmic complexity_ (an important Computer Science concept I [touched briefly on](https://github.com/xavdid/advent-of-code/tree/main/solutions/2021/day_4) in day 4). Our part 1 approach got slower as the days went on, since our list of fish kept getting longer. Our new approach will take the same amount of computation every day, since we're only ever storing (up to) 8 numbers. That's known as "constant time complexity", which is a great "score" for an algorithm.

We'll rely here on Python's `collections.defaultdict`. While a regular `dict` throws an error if you access a missing key, `defualtdict` uses a specified default instead:

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

# with a defaultdict, it "just works":
d['a'] += 1
```

Using a `defaultdict`, we can confidently add numbers to keys in the dict without knowing if they're there or not. So, here's our solution for both parts:

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
