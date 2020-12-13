# Day 13 (2020)

`Shuttle Search` ([Prompt](https://adventofcode.com/2020/day/13))

## Part 1

I'm not sure yet what those `x`s in the input will be for, but they're easy enough to filter out. Let's parse some input!

```py
min_leave_time = int(self.input[0])
bus_ids = [int(x) for x in self.input[1].split(",") if x != "x"]
```

For each `bus_id`, we need to find the first one that occurs after our `min_leave_time`. In the example, we can leave at `939` and the correct bus is `59`. If we compute `939 / 59`, we get `15.91`. So the first bus departue is that, rounded up times the `bus_id`: `16 * 59`, which is `944`. Hey, that's the answer for our example!

So for each bus, we need to get its earliest departure time. Then we follow the rest of the instrunctions for the answer:

```py
departure_time, best_bus = sorted(
    [(ceil(min_leave_time / bus_id) * bus_id, bus_id) for bus_id in bus_ids]
)[0]

return (departure_time - min_leave_time) * best_bus
```

It's a little concise, but clear. For the example, the sorted list is `[(944, 59), (945, 7), (949, 13), (950, 19), (961, 31)]`. The first one is the one we want, so we can cut straight to the first element. All that's left is some arithmetic.

## Part 2
