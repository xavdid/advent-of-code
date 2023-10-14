---
year: 2020
day: 13
title: "Shuttle Search"
slug: "2020/day/13"
pub_date: "2020-12-15"
---

## Part 1

I'm not sure yet what those `x`s in the input will be for, but they're easy enough to filter out. Let's parse some input!

```py
min_leave_time = int(self.input[0])
bus_ids = [int(x) for x in self.input[1].split(",") if x != "x"]
```

For each `bus_id`, we need to find the first one that occurs after our `min_leave_time`. In the example, we can leave at `939` and the correct bus is `59`. If we compute `939 / 59`, we get `15.91`. So the first bus departure is that, rounded up times the `bus_id`: `16 * 59`, which is `944`. Hey, that's the answer for our example!

So for each bus, we need to get its earliest departure time. Then we follow the rest of the instructions for the answer:

```py
departure_time, best_bus = sorted(
    [(ceil(min_leave_time / bus_id) * bus_id, bus_id) for bus_id in bus_ids]
)[0]

return (departure_time - min_leave_time) * best_bus
```

It's a little concise, but clear. For the example, the sorted list is `[(944, 59), (945, 7), (949, 13), (950, 19), (961, 31)]`. The first one is the one we want, so we can cut straight to the first element. All that's left is some arithmetic.

## Part 2

For this part, I wanted to start with a way to validate an answer. For a given loop iteration (a timestamp where the first bus can depart), we should be able to quickly calculate whether this timestamp is correct.

First, we have to tweak our input parsing a little to store both the bus id and the number of steps offset from root:

```py
buses = [
    (offset, int(bus_id))
    for offset, bus_id in enumerate(self.input[1].split(","))
    if bus_id != "x"
]

root_bus_id = buses[0][1]
```

For `17,x,13,19`, we get `[(0, 17), (2, 13), (3, 19)]`. Now, we loop over each bus and see if it could have left at the base timestamp + the offset:

```py
def valid_for_timestamp(loop):
base_ts = loop * root_bus_id
for offset, bus_id in buses[1:]:
    if (base_ts + offset) % bus_id != 0:
        return False

return True
```

We can skip the first bus because we know it can leave already (assuming we only call this function on multiples of the root bus). Let's do just that:

```py
loop = 1

while True:
    if valid_for_timestamp(loop):
        return loop * buses[0][1]

    loop += 1
```

And that's our whole solution! It returns the right answer for each test case just about instantly. Let's just plug in our puzzle input and... huh. It's taking a long time. Like, a _really_ long time. Too long, in fact.

This line in the prompt should have clued us in:

> However, with so many bus IDs in your list, surely the actual earliest timestamp will be larger than 100000000000000!

I tried starting my loop at `ceil(100000000000000 / root_bus_id)`, but it turns out we're still not fast enough. We'll have to refine our approach.

At this point, I was pretty stuck. I'm more interested in learning than figuring it all out on my own, so I took to the [Reddit solution thread](https://old.reddit.com/r/adventofcode/comments/kc4njx/2020_day_13_solutions/) for inspiration. I stumbled on [this great one](https://old.reddit.com/r/adventofcode/comments/kc4njx/2020_day_13_solutions/gfncyoc/) by `/u/noblematt20`. They give [a great explanation](https://old.reddit.com/r/adventofcode/comments/kc4njx/2020_day_13_solutions/gfsc2gg/) in the thread, but I'll break it down here as well.

A bus is valid in this part if `(timestamp + offset) % bus_id == 0`. We start by finding the first time our first bus leaves again. In the above example, that's timestamp `17`. It's also the first bus, so it's offset is zero. Filling in the equation, we have `(17 + 0) % 17 == 0`, which is going to be true for any first bus.

Next, we'll add some number (call it `step`) where `(timestamp + offset + step) % bus_id == 0`. If `timestamp + offset` is a multiple of `bus_id` and `timestamp + offset + step`, then we know that `step` _must_ be a multiple of `bus_id`. So instead of stepping by 1, we can instead step by our `bus_id`!

This holds true for 1st bus -> 2nd bus, 2nd -> 3rd, and so on. Starting at timestamp `17` (our first bus) we can jump by 17 until we find a `timestamp` that satisfies both:

- `(timestamp + 0) % 17 == 0`
- `(timestamp + 2) % 13 == 0`

We'll try 34, 51, 68, 85, **102**. There it is!

Now the fancy part: we know that the next step will be divisible by both 17 and 13. Why? Because we could get there from either timestamp 17 or 102, so both of these need to be true:

- `(17 + 0 + (17 * SOMETHING)) % bus_id == 0`
- `(102 + 2 + (13 * SOMETHING)) % bus_id == 0`

The smallest `SOMETHING` is 17 _ 13 _ 1, or **221**. If that doesn't work, we can try 221 _ 2, _ 3, etc. until we reach the timestamp that satisfies bus 19 with an offset of 3: 102 + (221 \* 15), which is **3417**. That's the answer for our short example (and eventually, our puzzle input). Let's code it up.

Python has a function that'll be perfect for us here: `itertools.count`. It takes a `start` and a `step` and returns a `generator` that gives us the next item in the sequence (but only when we ask for it, making `generators` _very_ memory efficient). So we walk through each bus and scan until we find the timestamp that solves all previous buses:

```py
step = 1
timestamp = 0  # start at the beginning
for offset, bus_id in buses:
    for ts in count(timestamp, step):
        if (ts + offset) % bus_id == 0:  # look familiar?
            timestamp = ts
            break
        step *= bus_id  # step by the LCM of all previous bus_ids
return timestamp
```

That'll do it! Before we go, one more nugget of wisdom: _you can build generators with conditions_. We know that `count(0, 1)` is a `generator`. But did you now that `(c for c in count(0, 1) if c % 2 == 0)` also returns a generator object? We can check it by using the global `next` function to get the next item:

```py
>>> gen = (c for c in count(0, 1) if c % 2 == 0)
>>> next(gen)
0
>>> next(gen)
2
>>> next(gen)
4
>>> next(gen)
6
```

With that knowledge in hand, we can simply our solution to the following:

```py
step = 1
timestamp = 0
for offset, bus_id in buses:
    timestamp = next(
        ts for ts in count(timestamp, step) if (ts + offset) % bus_id == 0
    )
    step *= bus_id
return timestam
```

Python handles finding that next number for us, so all we have to do is ask for it the right way.

---

It's worth noting that this puzzle is apparently an application of something called the [Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem). If you were aware of that ahead of time, you would have gotten part 2 much more quickly.
