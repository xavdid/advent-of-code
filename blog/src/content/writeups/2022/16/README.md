---
year: 2022
day: 16
title: "Proboscidea Volcanium"
slug: "2022/day/16"
pub_date: "2022-12-22"
---

## Part 1

I'm gonna be honest, this one kicked my butt. I got to a place where I had (manually) built the shortest path between every pair of valves[^1], but my basic greedy algorithm wasn't getting the right answer.

Ultimately, I threw in the towel. Because the point of AoC (for me) is to learn, I went through the [solution thread](https://old.reddit.com/r/adventofcode/comments/zn6k1l/2022_day_16_solutions/j0gqhgs/) until I found an explanation that clicked with me. I came across [this one](https://old.reddit.com/r/adventofcode/comments/zn6k1l/2022_day_16_solutions/j0gqhgs/), from `/u/Ill_Swimming4942`.

I'll walk through it like normal so you too can finish the day with sufficient understanding of the puzzle. Bear in mind that I did _not_ solve this myself (but I do now understand a working solution).

---

Because the solution space is so (relatively) small, we're able to brute force it. What if we map out every possible series of moves that can be accomplished in 30 ~steps~ minutes and then score the pressure released on each? Sounds so crazy, it just might work.

First up, input parsing! We'll be loading lines of raw input into a `Valve` class:

```py
from dataclasses import dataclass


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int

    @classmethod
    def from_str(cls, raw_valve: str) -> tuple["Valve", list[str]]:
        # use maxsplit so all of the neighbors stay together
        parts = raw_valve.split(" ", maxsplit=9)
        return Valve(parts[1], int(parts[4][:-1].split("=")[-1])), parts[-1].split(", ")

    # __lt__ is defined so that the dataclass is technically sortable
    # (a requirement to be used in a priority queue)
    def __lt__(self, _):
        return False
```

Now, we call that:

```py
...

class Solution(StrSplitSolution):
    def parse_valves(self) -> Valve:
        # name to Valve object
        valves: dict[str, Valve] = {}

        raw_neighbors: dict[str, list[str]] = {}
        for line in self.input:
            valve, str_paths = Valve.from_str(line)
            valves[valve.name] = valve
            raw_neighbors[valve.name] = str_paths
```

This leaves us with `valves` populated, a mapping from the name to the actual `Valve` object. We'll be using those dataclass instances for a lot, so it's important that we're using those rather than strings.

Next, we build a mapping of a `Valve` to its immediate neighbors:

```py
...

NeighborMap = dict[Valve, list[Valve]]

class Solution(StrSplitSolution):
    def parse_valves(self) -> Valve:
        ...

        # map of valve -> materialized neighbor valves
        neighbors: NeighborMap = {
            valves[raw_valve]: [valves[n] for n in neighbor_names]
            for raw_valve, neighbor_names in raw_neighbors.items()
        }
```

Now we're done with our strings, everything is `Valve` objects from here out. Next, we'll build a list of distances between every pair of points:

```py
...

class Solution(StrSplitSolution):
    ...

    def calculate_distances(
        self, neighbors: NeighborMap, start: Valve
    ) -> dict[Valve, int]:
        """
        Does a BFS walking away from the starting point
        to determine the best shortest path from target to each other point
        """
        queue: list[tuple[int, Valve]] = [(0, start)]
        best_distances: dict[Valve, int] = {start: 0}
        while queue:
            cost, current = heapq.heappop(queue)
            for neighbor in neighbors[current]:
                if (
                    neighbor not in best_distances
                    or cost + 1 < best_distances[neighbor]
                ):
                    new_best = cost + 1
                    best_distances[neighbor] = new_best
                    heapq.heappush(queue, (new_best, neighbor))

        # filter out valves we'll never stop at (since they have no rate)
        return {
            valve: distance for valve, distance in best_distances.items() if valve.rate
        }
```

We're doing the breadth-first version of Dijkstra's algorithm (in contrast to the depth-first one [I covered in day 12](/writeups/2022/day/12/)). Starting with `start`, we find the distance to all other points in the grid and then filter out the ones we'll never stop at. What's left is a `dict` of only `Valve`s with rates. Here's `AA` from the sample input:

```py
{
    Valve(name='AA', rate=0): {
        Valve(name='DD', rate=20): 1,
        Valve(name='BB', rate=13): 1,
        Valve(name='CC', rate=2): 2,
        Valve(name='EE', rate=3): 2,
        Valve(name='JJ', rate=21): 2,
        Valve(name='HH', rate=22): 5
    },
    ...
}
```

This will let us do lookups between any 2 pairs of `Valve` objects. We'll call that on every valve that has a rate (or is our starter):

```py
...

class Solution(StrSplitSolution):
    ...

    def parse_valves(self) -> Valve:
        ...

        # always start at AA
        starting_valve = valves["AA"]

        # next, get distance from each node to every other
        self.graph = {
            valve: self.calculate_distances(neighbors, valve)
            for valve in neighbors
            if valve is starting_valve or valve.rate
        }

        return starting_valve
```

Because we're comparing if two objects are the exact same ones in memory, we can get away with an `is` comparison (rather than the more common `==`, which tests equivalency, not "this is literally the same item in memory").

Next up, we need a way to generate every possible sequence of valves you can walk to and activate in the 30 minute window. To build this, we'll use recursion to check every place we can go from our starting point, then all the places we can go from there, and so on until there's nowhere else to check:

```py
...

class Solution(StrSplitSolution):
    ...

    def every_sequence(
        self,
        current_valve: Valve,
        valves_to_check: set[Valve],
        working_sequence: list[Valve],
        time: int,
    ) -> Iterable[list[Valve]]:
        for next_valve in valves_to_check:
            cost = self.graph[current_valve][next_valve] + 1
            if cost < time:
                yield from self.every_sequence(
                    current_valve=next_valve,
                    # these lines copy the iterables, which plays nicely with recursion
                    valves_to_check=valves_to_check - {next_valve},
                    working_sequence=working_sequence + [next_valve],
                    time=time - cost,
                )
        yield working_sequence
```

This uses `yield from`, which is a fancy way of doing `for item in x(): yield item` over and over. It also handles some error handling for us, if we ever wrote any errors. You can check out [a lengthy presentation about this pattern here](https://www.dabeaz.com/coroutines/), if you're so inclined.

Anyway, to help visualize this recursion, here's the arguments for reach function call to generate a single sequence:

<details>
<summary>Recursive Call Arguments (click to expand)</summary>

```py
{'time': 30,
 'working_sequence': [],
 'current': Valve(name='AA', rate=0),
 'to_check': {Valve(name='JJ', rate=21),
                Valve(name='EE', rate=3),
                Valve(name='HH', rate=22),
                Valve(name='DD', rate=20),
                Valve(name='CC', rate=2),
                Valve(name='BB', rate=13)}}

{'time': 27,
 'working_sequence': [Valve(name='JJ', rate=21)],
 'current': Valve(name='JJ', rate=21),
 'to_check': {Valve(name='EE', rate=3),
                Valve(name='HH', rate=22),
                Valve(name='DD', rate=20),
                Valve(name='CC', rate=2),
                Valve(name='BB', rate=13)}}

{'time': 22,
 'working_sequence': [Valve(name='JJ', rate=21), Valve(name='EE', rate=3)],
 'current': Valve(name='EE', rate=3),
 'to_check': {Valve(name='DD', rate=20),
                Valve(name='HH', rate=22),
                Valve(name='BB', rate=13),
                Valve(name='CC', rate=2)}}

{'time': 20,
 'working_sequence': [Valve(name='JJ', rate=21),
                        Valve(name='EE', rate=3),
                        Valve(name='DD', rate=20)],
 'current': Valve(name='DD', rate=20),
 'to_check': {Valve(name='HH', rate=22),
                Valve(name='BB', rate=13),
                Valve(name='CC', rate=2)}}

{'time': 15,
 'working_sequence': [Valve(name='JJ', rate=21),
                        Valve(name='EE', rate=3),
                        Valve(name='DD', rate=20),
                        Valve(name='HH', rate=22)],
 'current': Valve(name='HH', rate=22),
 'to_check': {Valve(name='BB', rate=13), Valve(name='CC', rate=2)}}

{'time': 8,
 'working_sequence': [Valve(name='JJ', rate=21),
                        Valve(name='EE', rate=3),
                        Valve(name='DD', rate=20),
                        Valve(name='HH', rate=22),
                        Valve(name='BB', rate=13)],
 'current': Valve(name='BB', rate=13),
 'to_check': {Valve(name='CC', rate=2)}}

{'time': 6,
 'working_sequence': [Valve(name='JJ', rate=21),
                        Valve(name='EE', rate=3),
                        Valve(name='DD', rate=20),
                        Valve(name='HH', rate=22),
                        Valve(name='BB', rate=13),
                        Valve(name='CC', rate=2)],
 'current': Valve(name='CC', rate=2),
 'to_check': set()}
```

</details>

We stop adding to the sequence as soon as `cost` exceeds our allotted `time` limit of `30`. Also note that we're not concerned with the amount of steam released here - we're grabbing every possible sequence, regardless of score. We also use some clever Python tricks here, namely the fact that containers are passed by reference (so recursive children can modify them), but copied during `+` and `-` operations. Pretty slick, right?

Now that we have a concept of sequences (a series of stops at valves), we can score it. This is actually fairly straightforward - we step through the sequence, multiplying the rate by the amount of time left:

```py
...

class Solution(StrSplitSolution):
    ...

    def score_sequence(self, sequence: list[Valve], time: int) -> int:
        total = 0
        current = Valve("AA", 0)

        for next_valve in sequence:
            # cost to move, + 1 to turn on the valve
            time -= self.graph[current][next_valve] + 1
            total += time * next_valve.rate
            current = next_valve

        return total
```

With all that in place, we can finally get the answer for part 1:

```py
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        starting_valve = self.parse_valves()
        valves_to_check = {k for k in self.graph if k is not starting_valve}

        return max(
            self.score_sequence(sequence, 30)
            for sequence in self.every_sequence(
                current_valve=starting_valve,
                valves_to_check=valves_to_check,
                working_sequence=[],
                time=30,
            )
        )
```

## Part 2

While part 1 asked us to compute the optimal 30-step path, part 2 asks us for the optimal pair of 26-step paths. As a pair, these paths must not contain any of the same steps (there'd be no reason for both us and the elephant to turn the same valve).

The first order of business is calling `every_sequence` again, but with `time=26`. And, instead of just returning the score, we'll also return a `set` of the points involved:

```py
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        # part 1 code
        ...
        part_1 = max(...)

        sequences: list[tuple[int, set[Valve]]] = sorted(
            (
                (self.score_sequence(sequence, 26), set(sequence))
                for sequence in self.every_sequence(
                    starting_valve, valves_to_check, [], 26
                )
            ),
            reverse=True,
        )
```

It's the same `every_sequence` call as above, but without the explicit kwargs. It's more consise, but less readable (IMO) if you don't know exactly what each kwarg is supposed to be. We also sorted our result by the score of the sequence, so we'll try the most valuable sequences first when iterating.

Next, we have to find our winning pair of paths. We'll start by iterating over the sequences:

```py
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        ...

        score = 0
        for index, (score_a, sequence_a) in enumerate(sequences):
            # we're sorting by descending score, so if we hit one that won't beat
            # the current record when doubled, we'll never find a winner
            if score_a * 2 < score:
                break

            ... # TODO

        return max_steam_alone, score
```

Because we're starting at the highest score and descending, we know that if 2x `score_a` wouldn't win, it's not getting any better from here. Lastly, iterate the remaining list and see if those sequences have no overlap. If they don't, then we store their score (if it's the biggest yet):

```py
...

class Solution(StrSplitSolution):
    ...

    def solve(self) -> tuple[int, int]:
        ...

        score = 0
        for index, (score_a, sequence_a) in enumerate(sequences):
            ...

            for score_b, sequence_b in sequences[index + 1 :]:
                # only consider sets of sequences that have no overlapping moves
                if not sequence_a & sequence_b:
                    score = max(score, score_a + score_b)

        return max_steam_alone, score
```

We could have used `itertools.combinations` instead of the nested loops (which would give us the same pattern), but it incurs extra memory use and takes a little longer by materializing the entire input tuple (while we're iterating over a sequence, which is _very_ efficient).

And with that, we're done! Here's hoping the difficulty peaked early this year.

[^1]: There are 55 values if you remove duplicates (`AA -> BB` is the same as `BB -> AA` on an undirected graph). There are 1,830 of them for the puzzle input.
