---
year: 2021
day: 12
title: "Passage Pathing"
slug: "2021/day/12"
pub_date: "2021-12-12"
---

## Part 1

I'll admit, this one had me a bit stumped to start. Whenever I don't know how to begin, I step through the smallest example and solve each step by hand. To help visualize, I parsed the input and made a little data structure:

```py
from collections import defaultdict

connections: Dict[str, List[str]] = defaultdict(list)
for line in self.input:
    l, r = line.split("-")
    if l != "end" and r != "start":
        connections[l].append(r)
    if l != "start" and r != "end":
        connections[r].append(l)

# => defaultdict(<class 'list'>,
#             {'A': ['c', 'b', 'end'],
#              'b': ['A', 'd', 'end'],
#              'c': ['A'],
#              'd': ['b'],
#              'start': ['A', 'b']})
```

Then I thought through how I'd get from that structure to the output. Imagine each path is a list of moves. Your initial list is a single path where the only move is `start`. Then you duplicate it with each valid move. `[['start']]` becomes `[['start', 'A'], ['start', 'b']]`. That in turn expands to:

- `start,A,c`
- `start,A,b`
- `start,A,end`
- `start,b,A`
- `start,b,d`
- `start,b,end`

So for each connection to the last element in my list, I add that to the list! This seems promising. The paths that include `end` should be taken out of rotation - those have found the end. For the rest, I should keep checking if they have valid moves. The prompt already told me that `d` is never visited, so we'll need a mechanism to toss that path out. I think at this point we can get some actual code down:

```py
# tuple so that we don't have to call `.copy()` a lot
Path = Tuple[str, ...]

in_progress_paths: List[Path] = [("start",)]
finished_paths: List[Path] = []
next_steps: List[Path] = []

# can start with range(...) loop instead of `while` so it'll stop if my loop conditions aren't right
while in_progress_paths:
    for path in in_progress_paths:
        for dest in connections[path[-1]]:
            if dest == "end":
                finished_paths.append(path + (dest,))
            if dest.isupper() or dest not in path:
                next_steps.append(path + (dest,))

    in_progress_paths = next_steps
    next_steps = []

return len(finished_paths)
```

This keeps adding paths as long as they are "valid". That is, they:

- jump to `end`, always valid
- jump to an upper case cave, always valid
- if not upper case (must be lower), so it must not be in our path

If one of those is true, it goes in our working paths (or finished one). Otherwise, it gets left behind. At the end, however many paths have been completed (and they're each guaranteed to be unique, so no worries there) is our answer!

## Part 2

At first I misread this as _all_ little caves could be visited twice. That would have been an easy one! We could tweak a single line (the check for `dest not in path`); we'd be no our way in no time. Instead, _a_ little cave can be visited exactly twice. So, our path needs to track if it's visited a little twice already. Sounds like it's time to move our humble `tuple` into a little class that can encapsulate some of that logic for us:

```py
@dataclass
class Path:
    steps: Tuple[str, ...]
    has_repeated_little: bool = False

    def extend_path(self, step: str) -> "Path":
        new_steps = self.steps + (step,)
        return Path(
            new_steps,
            self.has_repeated_little or (step.islower() and step in self.steps),
        )

    def can_add_step(self, step: str) -> bool:
        if step.isupper():
            return True

        if self.has_repeated_little:
            return step not in self.steps

        return True
```

It's got our tuple of strings, plus it knows whether or not it's already repeated a little cave or not. The `can_add_step` takes care of all that logic and `extend_path` handles our duplication and knowing whether or not we've just added a repeated cave.

We can incorporate both parts into a combined `_solve` method they can each call:

```py
def _solve(self, can_repeat_little_cave: bool) -> int:
    # input parsing and initialization from before
    ...

    while in_progress_paths:
        for path in in_progress_paths:
            for dest in connections[path.steps[-1]]:
                if dest == "end":
                    finished_paths.append(path.extend_path(dest))
                    continue

                # part 2
                if can_repeat_little_cave:
                    if path.can_add_step(dest):
                        next_steps.append(path.extend_path(dest))
                    continue

                # part 1
                if dest.isupper() or dest not in path.steps:
                    next_steps.append(path.extend_path(dest))

        in_progress_paths = next_steps
        next_steps = []

    return len(finished_paths)
```

Because the logic is so similar, we really only need to branch on the duplicate small cave handling.

I think this is my slowest solution part os far- part 2 takes just .75s on my M1 Pro (though still no fans). I think it's the first day there's a noticeable delay when the solver runs.

`./advent --profile` doesn't have a smoking gun, either. We're doing a lot of object initialization and copying of tuples, but I'm pretty sure we need at least some of that to keep each path fresh in memory. It's to be expected, I think, as we get later in the month. Hopefully it doesn't become a pattern!

I briefly tried using `set`s to keep down on the amount of data we were storing, but turns out copying those was more expensive than the tuples, so it all got slower! That's how it goes sometime.
