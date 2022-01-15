# prompt: https://adventofcode.com/2021/day/23

import re
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from heapq import heappop, heappush
from math import inf  # pylint: disable=no-name-in-module
from operator import add, sub
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

from ...base import GridPoint, TextSolution, answer

Amphipod = Union[Literal["A"], Literal["B"], Literal["C"], Literal["D"]]

COST: Dict[Amphipod, int] = {"A": 1, "B": 10, "C": 100, "D": 1000}
HOME_HORIZ: Dict[Amphipod, int] = {"A": 2, "B": 4, "C": 6, "D": 8}
HOMES = {2, 4, 6, 8}


@dataclass
class Location:
    horiz: int
    vert: int = 0
    value: Optional[Amphipod] = None

    @property
    def is_home(self) -> bool:
        """
        The location is an amph and is in its home column (either position)
        """
        if not self.value:
            return False
        return self.vert > 0 and self.horiz == HOME_HORIZ[self.value]


def cost_between_points(a: Location, b: Location) -> int:
    # assert bool(a.value) ^ bool(b.value)  # exactly one point has a value
    step_cost = COST[cast(Amphipod, a.value or b.value)]
    return (a.vert + b.vert + abs(a.horiz - b.horiz)) * step_cost


@dataclass
class State:
    populated: Dict[GridPoint, Amphipod]
    max_hallway_depth: int

    def loc_at(self, horiz: int, vert: int) -> Location:
        return Location(horiz, vert, self.populated.get((horiz, vert)))

    @property
    def did_win(self) -> bool:
        return all(Location(h, v, a).is_home for (h, v), a in self.populated.items())

    def __eq__(self, o: "State") -> bool:
        return self.populated == o.populated

    def _new_state(self, loc: Location, to: GridPoint) -> Tuple[int, "State"]:
        dest = Location(*to)
        return (
            cost_between_points(loc, dest),
            self.new_state_with_swap(loc, to),
        )

    def _check_horizontals(
        self, loc: Location, op: Callable[[int, int], int]
    ) -> Tuple[bool, List[Tuple[int, "State"]]]:
        """
        returns a 2-tuple of:
            *  whether or not the bath to home is unblocked (but nothing about the home itself)
            * the next possible states
        """
        results: List[Tuple[int, "State"]] = []
        horiz = loc.horiz
        home = HOME_HORIZ[cast(Amphipod, loc.value)]
        home_unblocked: bool = False
        while 1 <= horiz <= 9:
            horiz = op(horiz, 1)

            if horiz == home:
                home_unblocked = True
                continue

            if horiz in HOMES:
                # already found home, this isn't it
                continue

            if (horiz, 0) in self.populated:
                break
            results.append(self._new_state(loc, (horiz, 0)))

        return home_unblocked, results

    def _check_vertical(
        self, loc: Location, targ_horiz: int
    ) -> Optional[Tuple[int, "State"]]:
        # there is a clear path from loc to the opening of home
        # to enter home:
        # * all current residents must also be home
        # * there must be an empty spot

        targ_vert = None
        for vert_possibility in range(self.max_hallway_depth, 0, -1):
            if (targ_horiz, vert_possibility) in self.populated:
                if self.loc_at(targ_horiz, vert_possibility).is_home:
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

        # otherwise, it's valid to move the spot in the open to their hallway
        return self._new_state(loc, (targ_horiz, targ_vert))

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

    def next_states(self) -> List[Tuple[int, "State"]]:
        results: List[Tuple[int, "State"]] = []

        for (horiz, vert), amph in self.populated.items():
            if not self.can_move(horiz, vert):
                continue

            loc = self.loc_at(horiz, vert)
            can_reach_home: Optional[bool] = None

            if loc.is_home and all(
                self.loc_at(horiz, i).is_home
                for i in range(vert + 1, self.max_hallway_depth + 1)
            ):
                # me and everyone below me are home, am all good
                continue

            # if they're in a house (and thus have vert), they can only move to a hallway spot,
            # so check each direction until we hit a wall
            # this only runs if they're in a house that's not theirs
            if vert:
                for direction in [sub, add]:
                    found_home, new_states = self._check_horizontals(loc, direction)
                    can_reach_home = can_reach_home or found_home
                    # print(f"just {found_home=}, now {can_reach_home=}")
                    results += new_states
                    # print(f"  added {len(new_states)} new states from horiz")

            # they're already in the hallway, so their only valid move is to go home
            # to go home, they have to be:
            # * unblocked to get there
            # * if there is someone in the home, it has to also be a resident

            targ_horiz = HOME_HORIZ[amph]

            if can_reach_home is None:
                can_reach_home = self._is_horiz_clear_to_home(horiz, targ_horiz)

            if not can_reach_home:
                continue

            if home_state := self._check_vertical(loc, targ_horiz):
                results.append(home_state)

        return results

    def can_move(self, horiz: int, vert: int) -> bool:
        """
        Returns `False` if the amph is under another, `True` otherwise
        """
        if vert < 2:
            return True

        return all(self.loc_at(horiz, i).value is None for i in range(1, vert))

    def new_state_with_swap(self, old: Location, new: GridPoint) -> "State":
        # print(f"swapping {old} to {new}")
        new_pop = self.populated.copy()
        del new_pop[(old.horiz, old.vert)]
        new_pop[new] = self.populated[(old.horiz, old.vert)]
        return State(new_pop, self.max_hallway_depth)

    @cached_property
    def frozen(self) -> str:
        """
        Used to serialize this state into a set
        """
        return "|".join(f"{k}:{v}" for k, v in sorted(self.populated.items()))

    def __lt__(self, o):
        # needed so States can be in sortable tuples; we don't actually care about order
        return False


class Solution(TextSolution):
    _year = 2021
    _day = 23

    def _parse_input(self, extra: bool) -> Dict[GridPoint, Amphipod]:
        start_order: List[Amphipod] = re.findall(r"[ABCD]", self.input)
        locations = {}
        i = 0
        for vert in [1, 4 if extra else 2]:
            for horiz in [2, 4, 6, 8]:
                locations[(horiz, vert)] = start_order[i]
                i += 1
        if extra:
            # D#C#B#A #
            # D#B#A#C #
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

    def _dijkstra(self, max_hallway_depth: int) -> int:
        locations = self._parse_input(max_hallway_depth != 2)

        start = State(locations, max_hallway_depth)
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

    @answer(12240)
    def part_1(self) -> int:
        return self._dijkstra(2)

    @answer(44618)
    def part_2(self) -> int:
        return self._dijkstra(4)
