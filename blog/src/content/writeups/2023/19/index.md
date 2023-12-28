---
year: 2023
day: 19
slug: 2023/day/19
title: "TKTK"
# concepts: [regex]
# pub_date: "TBD"
---

## Part 1

This is the kind of puzzle I enjoy. It involves following the instructions closely, dynamic programming and some regex.

At a high level, we need to write a function that can run through each of our `Part`s (that hold the the `xmas` numbers) and apply workflows until we resolve either an `A` or `R`. To do that, we need to parse the `Part`s and, much trickier, parse workflows. We'll start with the easy one.

Parts are always in the same order and well formed, so we can use a regex to find every pair of `letter=number`s. Our output is a `dict` (which will make lookups easy later). This is straightforward:

```py
import re

Part = dict[str, int]

def parse_part(line: str) -> Part:
    return {k: int(v) for k, v in re.findall(r"(.)=(\d+)", line)}

# parse_part("{x=787,m=2655,a=1222,s=2876}")
#   -> {'x': 787, 'm': 2655, 'a': 1222, 's': 2876}
```

A `dict` comprehension makes easy work of our first task and gives us the first piece of the puzzle. Now for the good stuff.

For each workflow (starting with `in`) we need to run basically this pseudocode:

```py
def run_workflow(part: Part, workflow: ...):
    for filter_func in workflow.filters:
        if next_workflow := filter_func(part):
            return next_workflow

        return workflow.default
```

We'll have a dict of `key => workflow` do the lookups, but the exact nature of that `run_workflow` remains to be determined. Let's break it into component pieces.

For each line in the input, we need to extract its key, the filters, and the default. A regex makes short work of this:

```py
def parse_workflow(raw_workflow: str):
    if not (match := re.search(r"(.*){(.*),(.*)}", raw_workflow)):
        raise ValueError(f"unable to parse workflow: {raw_workflow}")

    key, filters, default = match.groups()
    # ('px', 'a<2006:qkq,m>2090:A', 'rfg')
```

That gives us our key and result. Next, we need to parse the middle part into callable functions. Each string has a pretty rigid structure (letter, operation, value, `:`, label), so it's easy enough to generate to actual Python code:

```py
from operator import gt, lt

Filter = Callable[[Part], Optional[str]]

def parse_filter(m: str) -> Filter:
    category = m[0]
    op = lt if m[1] == "<" else gt
    value_str, result = m[2:].split(":")

    return lambda part: result if op(part[category], int(value_str)) else None
```

Our function returns a function! The outer one takes a string (the raw filter) and returns a specially-made function that that itself takes a `Part`. If the specific category in the part compares favorably to the value, return the result (otherwise `None`). We use `operator.gt/lt`, the functions that back the actual `>` and `<` operations, to handle the math.

This give us everything we need to turn a raw workflow string into a single function that takes a `Part` and returns `str`. There's a few layers of generated functions, but they each to a single thing. Here's everything together (replacing our pseudocode from before):

```py
def build_workflow(raw_filters: str, default: str) -> Callable[[Part], str]:
    def _run_filters(part: Part) -> str:
        for raw_filter in raw_filters.split(","):
            if next_workflow := parse_filter(raw_filter)(part):
                return next_workflow

        return default

    return _run_filters


def parse_workflow(raw_workflow: str) -> tuple[str, Callable[[Part], str]]:
    if not (match := re.search(r"(.*){(.*),(.*)}", raw_workflow)):
        raise ValueError(f"unable to parse workflow: {raw_workflow}")

    key, filters, default = match.groups()

    return key, build_workflow(filters, default)
```

We can now finally start our actual solution:

```py
...

class Solution(TextSolution):
    separator = "\n\n"

    def part_1(self) -> int:
        workflows_block, parts_block = self.input

        workflows = dict(
            parse_workflow(workflow_line)
            for workflow_line in workflows_block.splitlines()
        )
```

We're using the `dict([(key, value), ...])` form of the `dict` constructor, which lets us easily turn all our workflows into useful functions. Now we can circle back to actually scoring our `Part`s.

Given that we're working with a tree structure, recursion is a good place to start. Our base case is a check for the `key` being `R` or `A`. Otherwise, we'll recurse with the result of running that workflow. We'll call our recursive function on each `Part` and sum the result:

```py ins={12-50}
...

class Solution(TextSolution):
    def part_1(self) -> int:
        workflows_block, parts_block = self.input

        workflows = dict(
            parse_workflow(workflow_line)
            for workflow_line in workflows_block.splitlines()
        )

        def score_part(part: Part, workflow_key: str) -> int:
            if workflow_key == "A":
                return sum(part.values())
            if workflow_key == "R":
                return 0

            return score_part(part, workflows[workflow_key](part))

        return sum(
            score_part(parse_part(raw_part), "in")
            for raw_part in parts_block.splitlines()
        )
```

It's more code than most days (and _certainly_ more dynamic), but it's not too bad when it's all set and done. On to part 2!

## Part 2
