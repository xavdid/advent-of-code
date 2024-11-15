---
year: 2023
day: 25
slug: 2023/day/25
title: "Snowverload"
pub_date: "2024-11-14"
---

## Part 1

All right, last one! Looking for min-cut solutions should point you towards the [wikipedia article](https://en.wikipedia.org/wiki/Minimum_cut) and the [Stoer–Wagner algorithm](https://en.wikipedia.org/wiki/Stoer%E2%80%93Wagner_algorithm). Another approach would be to graph the whole thing, since you can probably see it visually. But, neither of those seemed especially fun or interesting. Ultimately, we need to separate all of our nodes into two groups that have exactly 3 connections. Problem is, it's hard to figure out which node belongs in which cluster.

I'm a little out of gas on these and, as you can tell my the publish date for this writeup, am running out of time before next (this?) year starts. So, I went, for the final time, to the [solution thread](https://old.reddit.com/r/adventofcode/comments/18qbsxs/2023_day_25_solutions/). Some approaches described finding the shortest path between each node and finding the "hottest" paths, but I've done a lot of shortest-path work this year and wasn't in the mood for another.

Luckily, I found a [quick and clever](https://old.reddit.com/r/adventofcode/comments/18qbsxs/2023_day_25_solutions/ketzp94/) approach by `/u/4HbQ`. Let's run through it.

The key is realizing that when we're done clustering nodes, each group will have exactly 3 nodes with neighbors in the other group. For the nodes in the rest of the group, 100% of neighbors will be "local". If we rank nodes based on how many cross-group neighbors they have, the more likely it is that they belong in the other group. Let's code that up!

First, parsing grid. We'll make a dict of `node -> set[node]`, ensuring that relationships are noted in both directions:

```py
from collections import defaultdict

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        graph: dict[str, set[str]] = defaultdict(set)
        for line in self.input:
            root, nodes = line.split(": ")
            for node in nodes.split():
                graph[root].add(node)
                graph[node].add(root)
```

Straightforward so far. Next, we'll make two sets and a way to count non-local neighbors:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        right: set[str] = set()
        left = set(graph) - right

        def num_right_neighbors(n: str):
            return len(graph[n] & right)
```

Next, we'll loop until there are exactly `3` connections between `left` and `right` (which means are groups are correctly clustered). In each loop, we'll find which node has the most connections to the other group and move it over (assuming it probably belongs over there):

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        ...

        while sum(map(num_right_neighbors, left)) != 3:
            node = max(left, key=num_right_neighbors)
            left.remove(node)
            right.add(node)

        return len(left) * len(right)
```

Once the loop exits, we can multiply the size of each group and return it! Simple and elegant, right? Here's the funny thing though: This works (and got me my answer & 49th star), but it doesn't _always_ work.

On the very first loop, `num_right_neighbors` returns `0` for every node, so `max` returns the first thing it iterated over. Given we're iterating over a set, which node gets sent over first is basically random. If we happen to send a node that's one of our final 6, we'll end up sending all the nodes and running out of `left` causing an error. I get this behavior ~ 1 in 20 runs:

```sh
% for run in {1..20}; do
 ./advent
done
```

Luckily it's an error and not just sneakily returning a wrong answer, but still. I think solutions should work 100% of the time, every time. So, what to do?

My first approach was to put the whole thing in a function, catch the raised error, and retry until it works. But I liked a little bit before when I said "which node gets sent over first is basically random". It's actually deterministic, but changes each time you run `python`. So within a given invocation of my `advent` program, a function that picked a bad node first will continue to do so. I could run the program 3 times and hope 1 completes, but that's not really what I'm going for.

So instead, we'll use a function, but pick a starting node randomly:

```py
from random import choice as random_choice


class Solution(StrSplitSolution):
    def sort_groups(self, graph: dict[str, set[str]]) -> int:
        ejected = random_choice(list(graph.keys()))

        right: set[str] = {ejected}
        left = set(graph) - right

        while sum(map(num_right_neighbors, left)) != 3:
            if not left:
                # sometimes we get unlucky by ejecting a node too close to the cut point
                # in that case, just run again!
                return self.sort_groups(graph)

            ... # rest of original solution

    def part_1(self) -> int:
        graph: dict[str, set[str]] = defaultdict(set)
        ...

        # moved remaining code into above function
        return self.sort_groups(graph)
```

It's a little bit silly, but if we fail, we can just recurse and try again. Strictly speaking, it's possible that this is an infinite loop and we're _extremely_ unlucky. But in practice, it rarely fails more than twice in a row, so I feel good about this solution. In practice, I now get an answer on 100% of my runs, which is good enough for me.

## Part 2

That's it! We've completed this journey at long last.

As always, thanks for reading. See you all again... in a few weeks! 🙈
