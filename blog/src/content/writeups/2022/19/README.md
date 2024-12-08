---
year: 2022
day: 19
title: "Not Enough Minerals"
slug: "2022/day/19"
pub_date: "2023-07-31"
---

## Part 1

We're optimizing a series of steps, so today might seem like another [Dijkstra's](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) day. Unfortunately just reaching _a_ solution doesn't guarantee it's the best one. To ensure that, we have to simulate out all of the possible paths. Or, at least enough to be sure we have the best answer. That sounds like a job for a [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)!

One minute at a time, we'll look at every state in the queue and add every possible next step to the queue. Each state can create up to 5 new states:

- buy no robots, just mine
- buy one of the 4 available robot types

As you can imagine, our queue is going to grow out of control pretty spectacularly. That's a later us problem though. Luckily, this process is finite. Once every state has taken 24 steps, we can count how many geodes in the inventory and figure out what the best one was.

A state is comprised of current inventory and the number of robots we've built. Each of those is an object with 4 ints: `ore`, `clay`, `obsidian`, and `geode`. As luck would have it, that's the shape of the blueprints, too. A 2-cost clay robot could be `(0, 2, 0, 0)` and a geode robot's price can be expressed as `(3, 0, 12, 0)`.

Unfortunately, tuples of ints lke that aren't easy to do math with. We can add them, but all we get is concatenation. We can compare them, but Python returns as soon as any element is unequal (which won't work for prices):

```py
# mine 1 ore
(3, 0, 0, 0) + (1, 0, 0, 0) # (3, 0, 0, 0, 1, 0, 0, 0)

# can afford clay robot?
(4, 0, 0, 0) >= (3, 0, 12, 0) # True, but shouldn't be based on how prices work

# buy a robot
(4, 0, 13, 0) - (3, 0, 12, 0) # TypeError: unsupported operand type(s) for -: 'tuple' and 'tuple'
```

Instead, we need something that acts like a tuple, but is better fit for math operations Enter, the `MathTuple`:

```py
from operator import add, ge, gt, le, lt, sub
from typing import Callable, NamedTuple

class MathTuple(NamedTuple):
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0

    def _combine(self, f: Callable[[int, int], int], other: "MathTuple"):
        return MathTuple(*(f(a, b) for a, b in zip(self, other)))

    def __add__(self, other: "MathTuple") -> "MathTuple":
        return self._combine(add, other)

    def __sub__(self, other: "MathTuple") -> "MathTuple":
        return self._combine(sub, other)

    def _comparator(self, f: Callable[[int, int], int], other: "MathTuple") -> bool:
        return all(f(a, b) for a, b in zip(self, other))

    def __lt__(self, other: "MathTuple") -> bool:
        return self._comparator(lt, other)

    def __le__(self, other: "MathTuple") -> bool:
        return self._comparator(le, other)

    def __gt__(self, other: "MathTuple") -> bool:
        return self._comparator(gt, other)

    def __ge__(self, other: "MathTuple") -> bool:
        return self._comparator(ge, other)
```

Suddenly, all our examples work:

```py
# mine 1 ore
MathTuple(0, 0, 0, 0) + MathTuple(1, 0, 0, 0) # MathTuple(4, 0, 0, 0)

# can afford clay robot?
MathTuple(4, 0, 0, 0) >= MathTuple(3, 0, 12, 0) # False

# buy a robot
MathTuple(4, 0, 13, 0) - MathTuple(3, 0, 12, 0) # MathTuple(1, 0, 1, 0)
```

We're subclassing `NamedTuple`, which is itself a subclass of `tuple`. I went with `NamedTuple` over my [perennial favorite](https://xavd.id/blog/post/python-dataclasses-from-scratch/) the dataclass because being able to iterate over the properties predictably is important. Dataclasses can be made to do that, but it's slow and more code than it's worth. Tuples are simple and very interoperable.

We also have to override some of the [comparison methods](https://docs.python.org/3/reference/datamodel.html#object.__lt__) and a couple of the [number-related methods](https://docs.python.org/3/reference/datamodel.html#object.__add__). These are the underlying functions that Python calls on two objects when they're passed to operators like `+`, `>=`, or `-`.

Now we can parse the input. This one's much simpler than it looks. Each line has exactly 6 numbers and they always correspond to the same thing:

1. ore cost of ore
2. ore cost of clay
3. ore cost of obsidian
4. clay cost of obsidian
5. ore cost of geode
6. obsidian cost of geode

We can write a regex to find us the 6 numbers in a line and turn them into ints:

```py
import re

...

Blueprint = dict[str, MathTuple]

blueprints: list[Blueprint] = []
for line in self.input:
    costs = list(map(int, re.findall(r"(\d+) ", line)))
    blueprints.append(
        {
            "ore": MathTuple(ore=costs[0]),
            "clay": MathTuple(ore=costs[1]),
            "obsidian": MathTuple(ore=costs[2], clay=costs[3]),
            "geode": MathTuple(ore=costs[4], obsidian=costs[5]),
        }
    )

```

Next, we need a class to track our inventory:

```py
...

class Inventory(NamedTuple):
    current: MathTuple = MathTuple()
```

It may look odd to have a 1-element tuple, but we'll be adding some methods and (_spoilers_) an extra element later. Just bear with me.

Now the meat and potatoes: our breadth-first search. Here's the skeleton:

```py
from typing import Iterable

...

State = tuple[Inventory, MathTuple]

def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    queue: Iterable[State] = [(Inventory(), MathTuple(ore=1))] # (resources, robots)

    for time in range(num_minutes):
        next_queue: list[State] = []

        for inventory, robots in queue:
            # TODO: add all possible cases to the next_queue

        queue = next_queue

    return max(inv.current.geode for inv, _ in queue)
```

Eagle eyed readers will note that I've preemptively made `num_minutes` dynamic, despite part 1 not ever changing that value. Let's call it a hunch about what part 2 will entail.[^1] Otherwise, it's a pretty standard BFS- consider every state at a certain timestamp, enqueue the next step, then do those all at once. This is the opposite of the depth-first approach (where we consider a branch until we find the destination (or know that we can't)). Like I said before, these queues will get [wide](https://i.kym-cdn.com/entries/icons/original/000/025/003/benswoll.jpg).

Let's dig into that loop. We need to address our two major cases

1. mining, then buying nothing
2. buying a robot (we can afford), mining, then adding that robot to the pile

Now that we need to add (mine) and subtract (buy) from our inventory, it's a good time to add those helper methods to `Inventory` and one to `MathTuple` itself:

```py
...

class MathTuple(NamedTuple):
    ...

    def increment(self, material: str) -> "MathTuple":
        return self._replace(**{material: getattr(self, material) + 1})

...

class Inventory(NamedTuple):
    ...

    def mine(self, robots: MathTuple) -> "Inventory":
        return Inventory(self.current + robots)

    def buy(self, price: MathTuple) -> "Inventory":
        return Inventory(self.current - price)

...

def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    ...

    for time in range(num_minutes):
        ...

        for inventory, robots in queue:
            mined_inventory = inventory.mine(robots)

            # wait and mine
            next_queue.append((mined_inventory, robots))

            # try to build each robot type and add a state for any we can afford
            for resource, price in prices.items():
                if inventory.current >= price:
                    next_queue.append(
                        (mined_inventory.buy(price), robots.increment(resource))
                    )

            ...
```

It's a fair bit of code, but I find it very readable. Note the careful order of operations- our "wait" state mines right away, but our "build" cases base their purchasing decisions on the pre-mining inventory (but use the post-mining inventory for the next state).

Our data structures are all based on tuples, meaning they're immutable. Thus, they're never edited - "modifications" mean creating a new object based on the values of old one. Because our methods all return new `Inventory` objects, our methods can be chained to each other (applying one chain at a time). That's why `inventory.mine(robots).buy(price)` works! I find this sort of code very easy to reason about.

Pay close attention to the `MathTuple.increment` method. We get to use the handy [namedtuple.\_replace](https://docs.python.org/3.11/library/collections.html#collections.somenamedtuple._replace), but have to pass the kwarg dynamically (which we wouldn't do if we knew the name ahead of time, like `self._replace(ore=self.ore + 1)`). Using `**` with a `dict` in conjunction with `getattr`(which lets us look up a property via a string name) make short work of it though.

Anyway, let's give it a whirl on the test input, that should be pretty fast...

Talk about some famous last words. I added some logging to see what was taking so long:[^2]

```py
def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    ...

    for time in range(num_minutes):
        print(f"Starting round {time:02}, queue is length {len(queue):,}")
```

Gives us:

```
Starting round 00, queue is length 1
Starting round 01, queue is length 1
Starting round 02, queue is length 1
Starting round 03, queue is length 2
Starting round 04, queue is length 3
Starting round 05, queue is length 7
Starting round 06, queue is length 12
Starting round 07, queue is length 29
Starting round 08, queue is length 57
Starting round 09, queue is length 143
Starting round 10, queue is length 320
Starting round 11, queue is length 846
Starting round 12, queue is length 2,205
Starting round 13, queue is length 6,285
Starting round 14, queue is length 18,681
Starting round 15, queue is length 58,722
Starting round 16, queue is length 193,877
Starting round 17, queue is length 664,222
Starting round 18, queue is length 2,357,070
...
```

While the early rounds fly by, the rate at which our queue grows in the later rounds quickly becomes untenable; each state can potentially spawn 5 more. We'll have to apply a classic CS concept: ~~[branch & bound](https://en.wikipedia.org/wiki/Branch_and_bound)~~ [Beam Search](https://en.wikipedia.org/wiki/Beam_search) (_much thanks to `@DataWraith` on Tildes for kindly [correcting me](https://tildes.net/~comp.advent_of_code/1kj7/day_7_bridge_repair#comment-eaxs)_ on this naming!).

Instead of treating every single state as a potential winner, we can prune our queue by throwing out states that we don't think will go the distance. How exactly we do that is up to us but the idea that at the start of each round, we:

1. sort all states in the queue by some predictor of success
2. keep only the best N states and assume that anything worse than that number isn't a winner

This way, we'll only consider a fixed number each round and that number will stay small. But, our success now depends on being able to accurately prune bad branches.

Before continuing on, take a minute to think of any rules we can use to prune a bad state judge a potentially good one by. Here's one I tried:

Don't try to build robots in the final round. Those robots won't produce (since time is up), but they'll potentially x5 the number of states we have to look through at the very end.

Ok, have a quick think on it (and don't just say you did and keep reading, actually chew on it for a minute).

---

Ok, come up with anything good? I'll share what I used, but feel free to experiment on your own!

I had 3 big ideas:

1. the aforementioned "don't build in the last round"
2. use a `set` for `next_queue` so that we don't repeat work on duplicate states
3. judge states based on their total resources mined

We can knock the first two out:

```py
...

def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    ...

    for time in range(num_minutes):
        next_queue: set[State] = set()

        for inventory, robots in queue:
            ...

            # don't build on last round
            if time == num_minutes - 1:
                continue

            ...
```

Ordinarily it would be tricky to transition our `State`s to being totally immutable, but because we're using tuples for everything, we can drop them right into a `set` without complaint. We can see the advantages right away:

```
Starting round 00, queue is length 1
Starting round 01, queue is length 1
Starting round 02, queue is length 1
Starting round 03, queue is length 2
Starting round 04, queue is length 3
Starting round 05, queue is length 7
Starting round 06, queue is length 11
Starting round 07, queue is length 25
Starting round 08, queue is length 44
Starting round 09, queue is length 101
Starting round 10, queue is length 202
Starting round 11, queue is length 446
Starting round 12, queue is length 906
Starting round 13, queue is length 1,877
Starting round 14, queue is length 3,902
Starting round 15, queue is length 8,316
Starting round 16, queue is length 18,180
Starting round 17, queue is length 40,433
Starting round 18, queue is length 89,829
Starting round 19, queue is length 196,130
Starting round 20, queue is length 425,732
Starting round 21, queue is length 940,224
Starting round 22, queue is length 2,141,974
...
```

We broke 1 million queue items in round 18 last time but not until 22 with this approach. Improvement! Of course, I still wasn't patient enough to see it finish. Let's get bounding.

The core change is to sort and cut the queue when it exceeds a certain size:

```py
...

MAX_QUEUE_SIZE = 1000

def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    ...

    for time in range(num_minutes):
        ...

        if len(queue) > MAX_QUEUE_SIZE:
            queue = sorted(queue, key=lambda s: ..., reverse=True)[:MAX_QUEUE_SIZE]

        ...
```

All that remains is to sort our states. My approach was to track the total number of resources that have been mined and return those as a tuple (with the most expensive resources first). The thought being that whichever branches have produced the most advanced resources have a better chance of This will use traditional tuple ordering, sorting strictly by the first element and breaking ties (if needed) with the 2nd, 3rd, and so on.

Because we encapsulated all our adding and subtracting logic in `Inventory`, that's the only place we need to make changes:

```py
...

class Inventory(NamedTuple):
    current: MathTuple = MathTuple()
    total: MathTuple = MathTuple() # add a running total

    def mine(self, robots: MathTuple) -> "Inventory":
        # adjust by adding to the total
        return Inventory(self.current + robots, self.total + robots)

    def buy(self, price: MathTuple) -> "Inventory":
        # just pass along the total without edit (don't subtract from it)
        return Inventory(self.current - price, self.total)

    @property
    def key(self):
        """
        decides how an inventory is sorted.
        more promising solutions should be sorted higher
        """
        return (
            self.total.geode,
            self.total.obsidian,
            self.total.clay,
            self.total.ore,
        )

...

def find_max_geodes(prices: Blueprint, num_minutes: int) -> int:
    ...

    for time in range(num_minutes):
        ...

        if len(queue) > MAX_QUEUE_SIZE:
            # fill in key function
            queue = sorted(queue, key=lambda s: s[0].key, reverse=True)[:MAX_QUEUE_SIZE]

        ...
```

Finally, we return our answers:

```py
...

return sum(
    (idx + 1) * find_max_geodes(blueprint, num_minutes=24)
    for idx, blueprint in enumerate(blueprints)
)
```

After confirming my answer, I tried dropping the `MAX_QUEUE_SIZE` until I stopped getting the right answer. For my approach, `200` seemed like the sweet spot.

See how how you can go!

## Part 2

Ironically, based on our optimization work for part 1, this is a nothing-burger:

```py
return (
    find_max_geodes(blueprints[0], 32)
    * find_max_geodes(blueprints[1], 32)
    * find_max_geodes(blueprints[2], 32)
)
```

Because of our bounding, the longer rounds didn't meaningfully add to the queue length. We're only checking 3 blueprints instead of the input's full 30, so this is the _much_ faster half.

Lastly, I recommending checking out this [great Reddit thread](https://old.reddit.com/r/adventofcode/comments/zpy5rm/2022_day_19_what_are_your_insights_and/) of optimization approaches folks came up with. It's really cool seeing all the different approaches. Give it a read!

[^1]: Of course, I'm writing this after having completed both parts, so call it a _very good_ hunch. Really though, I added that arg in the first version of this code because I've done enough of these at this point to occasionally guess what's coming.
[^2]: This uses Python's little-known but very powerful [format string mini-language](https://docs.python.org/3/library/string.html#formatspec). Definitely worth being familiar with for very nice looking strings!
