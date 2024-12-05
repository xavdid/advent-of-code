---
year: 2024
day: 5
slug: "2024/day/5"
title: "Print Queue"
# concepts: []
pub_date: "2024-12-05"
---

## Part 1

My first inclination on this is to parse out the rules as pairs of ints and the updates as lists of ints. An update is said to pass a rule when it's got both of the rule elements. We can filter updates and sum them.

Because we have to parse out the two separate blocks, we'll treat the input as a big string and separate it by `\n\n`. For each of those, we'll do some basic parsing:

```py
def parse_int_list(l: list[str]) -> list[int]:
    return [int(i) for i in l]

class Solution(TextSolution):
    def part_1(self) -> int:
        raw_rules, raw_updates = self.input.split("\n\n")

        rules: list[list[int]] = [
            parse_int_list(raw_rule.split("|")) for raw_rule in raw_rules.splitlines()
        ]

        updates: list[list[int]] = [
            parse_int_list(raw_update.split(","))
            for raw_update in raw_updates.splitlines()
        ]
```

Next, we need a function to validate if an update passes a rule. If it's missing either of the rule's elements it should be ignored, otherwise we'll make sure the first element comes before the second:

```py
def adheres_to_rule(rule: list[int], update: list[int]) -> bool:
    assert len(rule) == 2
    l, r = rule
    if l in update and r in update:
        return update.index(l) < update.index(r)

    # if we don't have both rule items, we ignore it
    return True
```

That lets us filter for updates that pass every rule and pull out their middle element (which is the floor of their length / 2). Python's integer division (`//`) handles rounding down for us:

```py
...

class Solution(TextSolution):
    def part_1(self) -> int:
        ...

        return sum(
            update[len(update) // 2] # get middle element
            for update in updates
            if all(adheres_to_rule(r, update) for r in rules) # for updates that pass all rules
        )
```

## Part 2

Now we need to produce the correct ordering of the pages in an update based on all of the relevant rules. It was important that for an update, every page showed up in at least 1 rule. I did a quick check to verify that:

```py
from itertools import chain

for update in updates:
    relevant_rules = [r for r in rules if r[0] in update and r[1] in update]
    all_nums = set(chain(*relevant_rules))
    assert all_nums == set(update)
```

So we know that if we have all the rules for the update, we can reconstruct the update from scratch rather than modifying the update itself (which would also probably work, we just don't _have_ to).

Thus, the game has changed. The task now is to produce an unambiguous ordering from a list of dependencies. This immediately smelled like ordering of dependent tasks, which is something I have [strong](https://xavd.id/blog/post/my-perfect-task-app/#dependent-tasks) [feelings](https://github.com/xavdid/dependent-tasks) about. This sort is called a [Topological sort](https://en.wikipedia.org/wiki/Topological_sorting) and is useful for a wide variety of CS use cases, like resolving required dependency versions in a package manager.

To perform this sort, we have to transform our rules into a directed acyclic graph (aka `DAG`). Some graphs (like the grids used in previous days) have undirected edges between nodes:

```
A ---- B
|      |
|      |
|      |
|      |
C ---- D
```

While edges in a DAG all have specific directions:

```
      B
      |
      |
      V
A --> C --> D
```

To sort a DAG, the algorithm starts by finding nodes that aren't depended on. For that calculation to work, it's important that there are no loops in the graph (that's the "acyclic" part of the DAG). For instance, this graph has no valid starting node, since it's a loop:

```
A ---> B
^      |
|      |
|      |
|      V
C <--- D
```

As long as we have both of those qualities in our graph, it's a DAG! And wouldn't you know it, our list of rules fits that perfectly.

The most common algorithm for topological sorting is [Kahn's algorithm](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm), which is described in pseudocode on Wikipedia. We could implement. Or...

Remember when I said this algorithm gets used in a lot of programming concepts? It turns out that it's important enough to be included in Python's built-in [graphlib](https://docs.python.org/3/library/graphlib.html)! In fact, it's the only thing there. Let's try it!

We'll be tweaking our part 1 code to separately handle both valid and invalid sorts:

```py rem={11-15} ins={3,4,16-21}
...

def middle_element(l: list[int]) -> int:
    return l[len(l) // 2]

class Solution(TextSolution):
    def part_1(self) -> int:
    def solve(self) -> tuple[int, int]:
        ...

        return sum(
            update[len(update) // 2] # get middle element
            for update in updates
            if all(adheres_to_rule(r, update) for r in rules) # for updates that pass all rules
        )
        part_1, part_2 = 0, 0
        for update in updates:
            if all(adheres_to_rule(r, update) for r in rules):
                part_1 += middle_element(update)
            else:
                ... # TODO
```

So now we have an `update` and know that it's not sorted correctly. `graphlib.TopologicalSorter` has an `add` method to define nodes, so we can loop through the relevant rules and add them to our graph before sorting it:

```py
from graphlib import TopologicalSorter
...

class Solution(TextSolution):
    def solve(self) -> tuple[int, int]:
        ...
        for update in updates:
            if all(adheres_to_rule(r, update) for r in rules):
                ...
            else:
                sorter = TopologicalSorter()
                for l, r in rules:
                    if l in update and r in update:
                        # only add if both rule elements are in this update
                        sorter.add(l, r)

                sorted_update = list(sorter.static_order())

                part_2 += middle_element(sorted_update)

        return part_1, part_2
```

`sorter.static_order()` gives us the sorted list of nodes, which we can pass to our same `middle_element` calculation from before.

Some days, the Python stdlib really feels like cheating. Other days, it's just the value of picking the right tool for the job. 😁
