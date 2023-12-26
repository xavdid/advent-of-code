---
year: 2021
day: 23
title: "Amphipod"
slug: "2021/day/23"
pub_date: "2022-01-22"
---

## Part 1

This has been the toughest day for me so far. I usually do both parts in a couple of hours, max. I worked on this one for literal days. I got there! But boy, did it take some time.

Generically, it's the same problem as [day 15](/writeups/2021/day/15/)- we have to figure out the most efficient bath between a starting state and and an ending state. We will be able to calculate the cost between two states. So, we'll be able to use Dijkstra's algorithm again to find the most efficient series of intermediate states to get to the desired ending.

To that end, I copied my entire algorithm from day 15 and put it in a `self._dijkstra` method. Its only parameter is `max_room_size`, which will be important for part 2; don't worry about it for now.

The part of this that gave me the most trouble was how to model the data. It's _sort of_ a grid, but you can't move freely. There are "houses" (vertical parts) and the "hallway" (horizontal area). An amphipod is "home" if it's in the correct house. I first tried to organize it with nested lists, like so:

```py
# the state in the example
[
    None,
    None,
    [None, "B", "A"],
    None,
    [None, "C", "D"],
    None,
    ...
]
```

Each step is either empty or has a letter; each room is a sub array. But, I found this a little hard to visualize and manipulate, so I went for a more traditional grid. Each point is a `tuple` of `(horiz, vert)`. Here's the initial example again:

```
(0,0) (1,0) (2,0) (3,0) (4,0) (5,0) ... (9,0) (10,0)
            (2,1)       (4,1)
            (2,2)       (4,2)
```

It's a "grid", but there's a fixed number of valid points. For instance, `(1,1)` is a wall and can't have an amphipod there, so we ignore it. This lets us store our state in a `Dict[Point, str]`. Let's make our basic state class and helper types:

```py
from dataclasses import dataclass
# we're not using these all yet, but we will!
from typing import (
    Callable,
    DefaultDict,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

Amphipod = Union[Literal["A"], Literal["B"], Literal["C"], Literal["D"]]
GridPoint = Tuple[int, int]

@dataclass
class State:
    populated: Dict[GridPoint, Amphipod]
    max_room_size: int = 2
```

Now that we have somewhere to put them, we'll need to parse our input:

```py
class Solution:
    ...
    def _parse_input(
    start_order: List[Amphipod] = re.findall(r"[ABCD]", self.input)
        locations = {}
        i = 0
        for vert in [1, 2]:
            for horiz in [2, 4, 6, 8]:
                locations[(horiz, vert)] = start_order[i]
                i += 1
        return locations
```

That works because the regex finds letters left-to-right, top-to-bottom. We can assign them locations the same way.

Ok! So put those together and we have a state which knows exactly where all of the 8 amphipods are. The first thing we'll need to be able to calculate is whether or not that state has "won" (so we know when to exit). A state has won if all of its amphipods are in their home columns. So, we'll need a function that tells us that, too. They're not too complicated:

```py
# which column each amph belongs to
HOME_HORIZ: Dict[Amphipod, int] = {"A": 2, "B": 4, "C": 6, "D": 8}

class State:
    ...

    def loc_is_home(self, loc: GridPoint) -> bool:
        """
        Is the amphipod at the given location home?
        """
        if loc not in self.populated:
            return False

        return loc[1] > 0 and loc[0] == HOME_HORIZ[self.populated[loc]]

    @property
    def did_win(self) -> bool:
        return all(self.loc_is_home(p) for p in self.populated.keys())
```

Now, given a state, we know if it's won. We've confirmed our initial state _hasn't_ won (bummer, that would save a lot of time here). Now we need to be able to get a new state from an old state. The new state is mostly identical to the old one, but its `populated` `dict` will have exactly one key different:

```py
class State:
    ...

    def new_state_with_swap(self, old: GridPoint, new: GridPoint) -> "State":
        new_pop = self.populated.copy()
        del new_pop[old]
        new_pop[new] = self.populated[old]
        return State(new_pop, self.max_room_size)
```

Turn it around and that's a brand new `State`! In practice, we'll be coupling a new state with how much it cost to transition between them (that cost is very important to our algorithm). Given those two points, we can calculate their distance as the horizontal distance plus each of their vertical distances (which covers cases where we have to go up, side, and then down):

```py
COST: Dict[Amphipod, int] = {"A": 1, "B": 10, "C": 100, "D": 1000}

class State:
    ...

    def cost_between_points(self, a: GridPoint, b: GridPoint) -> int:
        # exactly one of these points will have an amphipod; you can verify that by adding
        # an `assert self.populated.get(a) ^ self.populated.get(b)`
        # which uses Python's xor operator to verify our requirement
        step_cost = COST[cast(Amphipod, self.populated.get(a) or self.populated.get(b))]
        return (a[1] + b[1] + abs(a[0] - b[0])) * step_cost
```

There's a bit of extra typing cruft (the `cast`) in there, but the math is on the last line and is straightforward. We can wrap these two methods into a single function that returns the `2-tuple` we'll eventually be sorting in Dijkstra's:

```py
class State:
    ...

    def _new_state(self, loc: GridPoint, to: GridPoint) -> Tuple[int, "State"]:
        return (
            self.cost_between_points(loc, to),
            self.new_state_with_swap(loc, to),
        )
```

This all looks good, but there's a catch- nothing we've written so far verifies the _validity_ of the moves. Our prompt explains those rules, and there are many cases where we're unable to move an amphipod between two points (e.g. it's path is blocked). Let's think through the rules of how an amphipod can move. Then, given a state, we'll be able to generate every possible next state. There are a few rules of motion to consider:

1. If an amphipod is in a house it can:
   1. move into the hallway
   2. move home
2. If an amphipod is in the hallway, it can _only_ move home
   1. To move home, all amphipods in that house must already be home
   2. To move home, there must be a clear path there
3. If an amphipod is in a house and is not at the top, it can't move
4. An amphipod will only make 1 or 2 moves during the game:
   1. start -> hall -> home, OR
   2. start -> home
5. If an amphipod is home and everything below it is home, it won't move

With those rules in hand, we can start iterating on possible next states! From the starting state, there are exactly 28 possible moves:

```
#############
#...........#
###B#C#B#D###
  #A#D#C#A#
  #########
```

Each of the 4 amphipods at the top of their houses (`B`, `C`, `B`, and `D`) can move to any of the valid hallway spots. Each of the ones on the bottom (`A`, `D`, `C`, and `A`) can't move. The next function we need to write looks at each amphipod, determines if it can move, and if so, generates the next state (and its cost). Let's get to it:

```py
class State:
    ...

    def can_move(self, horiz: int, vert: int) -> bool:
        """
        Returns `False` if the amph is under another, `True` otherwise
        """
        if vert < 2:
            return True

        return all(self.populated.get((horiz, i)) is None for i in range(1, vert))

    def next_states(self) -> List[Tuple[int, "State"]]:
        results: List[Tuple[int, State]] = []

        for loc, amph in self.populated.items():
            horiz, vert = loc
            if not self.can_move(horiz, vert):
                continue

            if self.loc_is_home(loc) and all(
                self.loc_is_home((horiz, i))
                for i in range(vert + 1, self.max_room_size + 1)
            ):
                # me and everyone below me are home, am all good
                continue
```

We consider each amphipod. If it can't move (because it's under another), then we can bail early. Next, we check if it needs to move at all (maybe it's already found home). If neither of those conditions match, then it's at least _possible_ it can move. Now we build a list of valid states for that amphipod.

The first case we consider is if it's in a house (which is either not it's home, or it's blocking someone who isn't home). We know it's in a house because `vert > 0`.

```py
from operator import add, sub

HOMES = {2, 4, 6, 8}

class State:
    ...

    def _check_horizontals(
        self, loc: GridPoint, direction: Callable[[int, int], int]
    ) -> Tuple[bool, List[Tuple[int, "State"]]]:
        """
        returns a 2-tuple of:
            *  whether or not the bath to home is unblocked (but nothing about the home itself)
            * the next possible states
        """
        results: List[Tuple[int, "State"]] = []
        horiz = loc[0]
        home_unblocked: bool = False
        while 1 <= horiz <= 9:
            horiz = direction(horiz, 1)

            if horiz == HOME_HORIZ[self.populated[loc]]:
                home_unblocked = True
                continue

            if horiz in HOMES:
                # already found home, this isn't it
                continue

            if (horiz, 0) in self.populated:
                break
            results.append(self._new_state(loc, (horiz, 0)))

        return home_unblocked, results

    def next_states(...):
        ...

        for loc, amph in self.populated.items():
            ...

            # if it's None, then we didn't check the hallway at all
            can_reach_home: Optional[bool] = None

            # so we only store the next states if we didn't go straight home
            amph_results: List[State] = []

            # if they're in a house (and thus have vert), they can only move to a hallway spot,
            # so check each direction until we hit a wall
            # this only runs if they're in a house that's not theirs
            if vert:
                for direction in [sub, add]:
                    found_home, new_states = self._check_horizontals(loc, direction)
                    can_reach_home = can_reach_home or found_home
                    amph_results += new_states
```

Let's break this down. We know we can move into the hallway, but we're not sure how far. So we call `_check_horizontals` to walk in a direction. If we're on top of a house, we keep going (can't block an entrance). If that house is ours, we note the fact that we're not blocked from getting there (this is relevant later). For each valid spot we find, we store it as a possible state. Once we're blocked or we reach the end of the hallway, we return all the new states we found. We can reuse the same function for both directions by passing the `add` and `sub` functions from the `operators` package (which are the functions that power `+` and `-`).

Back in the main loop, we check horizontally in both directions and note whether or not we could have reached home's entrance unblocked (something we'll need a little later). We will have found _some_ number of new states. In our original example, this will be 7.

Next, we look at locations _without_ vert, which are amphipods that are already in the hallway. Their only valid move is to go home. That's only possible if the way is unblocked _and_ there are no non-residents in the target house. We may have already found whether or not we're unblocked. If not, we can check it now.

```py
class State:
    ...

    def _is_horiz_clear_to_home(self, horiz: int, targ_horiz: int) -> bool:
        # haven't checked, try it
        op = add if targ_horiz > horiz else sub
        can_reach_home = True
        while horiz != targ_horiz:
            horiz = op(horiz, 1)
            if (horiz, 0) in self.populated:
                can_reach_home = False
                break
        return can_reach_home

    def next_states():
        ...

        for loc, amph in self.populated.items():
            ...

            # they're already in the hallway, so their only valid move is to go home
            # to go home, they have to be:
            # * unblocked to get there
            # * if there are other amphs there, they must all be residents

            targ_horiz = HOME_HORIZ[amph]

            if can_reach_home is None:
                can_reach_home = self._is_horiz_clear_to_home(horiz, targ_horiz)

            if not can_reach_home:
                results += amph_results
                continue
```

If we can't reach home, we can save what we found so far and bail. The more interesting case is if we _can_. We have a couple more checks to do, before we know that it can actually land at home (not just reach it):

```py
class State:
    ...

    def _check_vertical(
        self, loc: GridPoint, targ_horiz: int
    ) -> Optional[Tuple[int, "State"]]:
        # there is a clear path from loc to the opening of home
        # to enter home:
        # * all current residents must also be home
        # * there must be an empty spot

        targ_vert = None
        for vert_possibility in range(self.max_room_size, 0, -1):
            p = (targ_horiz, vert_possibility)
            if p in self.populated:
                if self.loc_is_home(p):
                    # can't go here, but we're not busted yet
                    continue
                # non-neighbor here!
                break

            # found an empty spot!
            targ_vert = vert_possibility
            break

        if targ_vert is None:
            # couldn't find a spot
            return None

        # otherwise, we have found home
        return self._new_state(loc, (targ_horiz, targ_vert))

    def next_states():
        ...

            if home_state := self._check_vertical(loc, targ_horiz):
                    results.append(home_state)
            else:
                results += amph_results

        return results
```

This covers the rules we discussed. It checks each spot in the vertical from the bottom up (starting at whatever `self.max_room_size` is; `2` initially). There are a couple of cases that `_check_vertical` handles- they're commented. If there's a spot and it's not otherwise breaking rules, we can go there!

Back in the main loop, there's some new syntax: `:=`. Affectionately called the "walrus operator", it's a combination of an `if` and an assignment. It's equivalent to:

```py
home_state = self._check_vertical(loc, targ_horiz)
if home_state:
    results.append(home_state)
else:
    results += amph_results
```

It's a nice little piece of syntactic sugar. You can read more about it in [the PEP that introduced it](https://www.python.org/dev/peps/pep-0572/).

There's a nice little optimization there- if we can successfully go home, we can discard the rest of the `amph_results`- the best move is always to go home, so we only need to bring that state along with it if it's an option. Either way, we return whatever we have.

Congratulations on making it this far! We've done the lion's share of the work- there's just a couple of things left. Let's revisit our Dijkstra's implementation. Here's what I copied from [day 15](/writeups/2021/day/15/) with a couple of updates for today:

```py
def _dijkstra(self, max_room_size: int) -> int:
    locations = self._parse_input()

    start = State(locations, max_room_size)
    queue: List[Tuple[int, State]] = [(0, start)]
    visited = set()
    distances: DefaultDict[str, float] = defaultdict(lambda: inf, {start.frozen: 0})

    while queue:
        cost, current = heappop(queue)

        if current in visited:
            continue

        if current.did_win:
            return cost

        visited.add(current)

        for next_move_cost, next_state in current.next_states():
            if next_state in visited:
                continue

            total_cost = cost + next_move_cost

            if total_cost < distances[next_state]:
                distances[next_state] = total_cost
                heappush(queue, (total_cost, next_state))

    raise RuntimeError("No solution found")
```

If we run this as is, we get an odd error:

```
    ...
    if current in visited:
TypeError: unhashable type: 'State'
```

It all has to do with what kinds of items are allowed to be elements in sets. We've talked before about how Python sets are fast. They do this by taking the hash of an object- a unique string that's determined by the object's properties. The same object always has the same hash. Python knows very quickly if a given hash exists in a set (there's more to it, but it's a topic for another time).

For this approach to work, the items in the set have to be _immutable_, or unchangeable. Some Python data types are immutable by design: strings, numbers, etc. Containers, on the other hand, are mutable: `dict`, `list`, `set`. You can add and remove items to/from them, so they can change over time. As a result, you can't put a mutable object into a place where only immutable objects are accepted: sets and dict keys. Here are some examples:

```py
s = set()
s.add(1) # ok
s.add('a') # ok
s.add([0]) # unhashable type: 'list'

d = {}
d[1] = 1
d['a'] = 'a'
d[set()] = None # unhashable type: 'set'
```

This is the error we're seeing! We're trying to check if `current` (an instance of our `State` `dataclass`) is in a set. Do that, it needs to be hashable. Dataclasses can be hashable, but all of their properties must _also_ be hashable. Since we're storing a `dict`, that won't work. Instead, we'll have to devise a way to represent our `State` in a hashable way, a process known as _serialization_. There are a few ways to do this, but the simplest is as a string. We have to be careful to ensure that our `populated` dict has consistent serialized output. That requires sorting our keys, so that the same dict always has the same output, an important feature here. Here's how that looks:

```py
from functools import cached_property

class State:
    ...

    @cached_property
    def frozen(self) -> str:
        """
        Used to serialize this state into a set
        """
        return "|".join(f"{k}:{v}" for k, v in sorted(self.populated.items()))
```

Perfect! This let's us represent our state as a hashable string. We used `cached_property` because we'll be using this a lot and we don't want to have to re-calculate it multiple times. Here's the updated Dijkstra:

```py
def _dijkstra(self, max_room_size: int) -> int:
    locations = self._parse_input()

    start = State(locations, max_room_size)
    queue: List[Tuple[int, State]] = [(0, start)]
    visited: Set[str] = set()
    distances: DefaultDict[str, float] = defaultdict(lambda: inf, {start.frozen: 0})

    while queue:
        cost, current = heappop(queue)

        if current.frozen in visited:
            continue

        if current.did_win:
            return cost

        visited.add(current.frozen)

        for next_move_cost, next_state in current.next_states():
            if next_state.frozen in visited:
                continue

            total_cost = cost + next_move_cost

            if total_cost < distances[next_state.frozen]:
                distances[next_state.frozen] = total_cost
                heappush(queue, (total_cost, next_state))

    raise RuntimeError("No solution found")
```

That should be everything! Give it a run and...

```
...
    heappush(queue, (total_cost, next_state))
TypeError: '<' not supported between instances of 'State' and 'State'
```

Ah! One last thing. A priority queue sorts its items, but it doesn't know how to sort `State` instances. That makes sense - they don't really have a defined order. All that remains is to tell Python as much:

```py
class State:
    ...

    def __lt__(self, other):
        # needed so States can be in sortable tuples; we don't actually care about order
        return False
```

The `__lt__` builtin is how you tell Python that an instance (`self`) is less than another object. And again, we don't care about the actual result, just that Python can call this method and get an "answer".

Finally, we're all set. We have an answer!

## Part 2

I cheated a bit on my writeup today- my part 1 answer includes everything we needed for part 2. I figured that was easier than introducing all my code that assumed there were only room sizes of `2`. So, we can use our adjustable room sizes to change how we parse input:

```py
def _parse_input(self, extra: bool) -> Dict[GridPoint, Amphipod]:
    start_order: List[Amphipod] = re.findall(r"[ABCD]", self.input)
    locations = {}
    i = 0
    # the amphs we read from input are farther down if we're in "extra" mode
    for vert in [1, 4 if extra else 2]:
        for horiz in [2, 4, 6, 8]:
            locations[(horiz, vert)] = start_order[i]
            i += 1
    if extra:
        # D#C#B#A #
        # D#B#A#C #
        # we can just hardcode these
        locations.update(
            {
                (2, 2): "D",
                (2, 3): "D",
                (4, 2): "C",
                (4, 3): "B",
                (6, 2): "B",
                (6, 3): "A",
                (8, 2): "A",
                (8, 3): "C",
            }
        )
    return locations

def _dijkstra(self, max_room_size: int) -> int:
    locations = self._parse_input(max_room_size != 2)
    ...
```

Thanks to our prep, our two parts become calls to that function:

```py
def part_1(self) -> int:
    return self._dijkstra(2)

def part_2(self) -> int:
    return self._dijkstra(4)
```

Both parts run for me in under 5 seconds, which seems like a reasonable place to leave it. Great job sticking through with this one! I was frustrated with it for a while, but it definitely grew on me.
