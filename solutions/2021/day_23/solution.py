# prompt: https://adventofcode.com/2021/day/23


from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from heapq import heappop, heappush
from math import inf
from pprint import pprint, pformat
from typing import DefaultDict, Dict, List, Optional, Set, Tuple, Union, cast, Literal
from operator import add, sub
import re


from ...base import TextSolution, answer, GridPoint

# from typing import Tuple

Amphipod = Union[Literal["A"], Literal["B"], Literal["C"], Literal["D"]]

COST: Dict[Amphipod, int] = {"A": 1, "B": 10, "C": 100, "D": 1000}
HOME_HORIZ: Dict[Amphipod, int] = {"A": 2, "B": 4, "C": 6, "D": 8}
HALLWAYS = {2, 4, 6, 8}


@dataclass
class Location:
    horiz: int
    vert: int = 0
    value: Optional[Amphipod] = None

    def __post_init__(self):
        if self.vert:
            assert self.horiz in HALLWAYS, f"{self} is invalid"

        if self.horiz in HALLWAYS:
            assert self.vert, f"{self} is invalid"

    @property
    def index(self) -> int:
        return self.horiz + self.vert

    @property
    def is_home(self) -> bool:
        if not self.value:
            return False
        return self.vert > 0 and self.horiz == HOME_HORIZ[self.value]

    @property
    def is_locked(self) -> bool:
        return self.vert == 2 and self.is_home

    def is_valid_for(self, a: Amphipod) -> bool:
        if self.value:
            return False
        if self.vert == 0:
            return True
        return self.horiz == HOME_HORIZ[a]


def cost_between_points(a: Location, b: Location) -> int:
    assert bool(a.value) ^ bool(b.value)  # exactly one point has a value
    step_cost = COST[cast(Amphipod, a.value or b.value)]

    return (a.vert + b.vert + abs(a.horiz - b.horiz)) * step_cost

    return abs(a.index - b.index) * step_cost


SlimLocation = Tuple[int, int, Amphipod]


@dataclass
class State:
    populated: Dict[GridPoint, Amphipod]

    def loc_at(self, horiz: int, vert: int = 0) -> Location:
        if (horiz, vert) in self.populated:
            return Location(horiz, vert, self.populated[(horiz, vert)])
        if not 0 <= horiz <= 10:
            raise ValueError(f"{horiz=} out of bounds")
        if vert and not vert in {1, 2}:
            raise ValueError(f"{vert=} out of bounds")
        if not vert and horiz in {2, 4, 6, 8}:
            raise ValueError(f"{horiz=},{vert=} invalid")

        return Location(horiz, vert)

    def pretty(self):
        return pformat(self.populated)

    @property
    def did_win(self) -> bool:
        return all(Location(h, v, a).is_home for (h, v), a in self.populated.items())

    def __eq__(self, o: "State") -> bool:
        return self.populated == o.populated

    def next_states(self) -> List[Tuple[int, "State"]]:
        results: List[Tuple[int, "State"]] = []

        for (horiz, vert), amph in self.populated.items():
            # print(f"Checking {amph} at {horiz, vert}")
            if not self.can_move(horiz, vert):
                continue

            loc = self.loc_at(horiz, vert)

            if loc.is_home:
                if vert == 1:
                    if self.loc_at(horiz, 2).is_home:
                        # this column is done
                        continue
                    # below is blocked, must move
                else:
                    # am down and home, can stay
                    continue

            # they can only move to a hallway spot, so check each direction until we hit a wall
            # this only runs if they're in a hallway that's not theirs
            if vert:
                while horiz >= 1:
                    horiz -= 1
                    if horiz in HALLWAYS and HOME_HORIZ[amph] != horiz:
                        continue
                    if HOME_HORIZ[amph] == horiz:
                        if (horiz, 2) not in self.populated:
                            results.append(
                                (
                                    cost_between_points(loc, Location(horiz, 2)),
                                    self.new_state_with_swap(
                                        (loc.horiz, loc.vert), (horiz, 2)
                                    ),
                                )
                            )

                        elif (horiz, 1) not in self.populated and self.loc_at(
                            horiz, 2
                        ).is_locked:
                            results.append(
                                (
                                    cost_between_points(loc, Location(horiz, 1)),
                                    self.new_state_with_swap(
                                        (loc.horiz, loc.vert), (horiz, 1)
                                    ),
                                )
                            )
                        continue
                    if (horiz, 0) in self.populated:
                        break
                    results.append(
                        (
                            cost_between_points(loc, Location(horiz, 0)),
                            self.new_state_with_swap((loc.horiz, loc.vert), (horiz, 0)),
                        )
                    )

                horiz = loc.horiz
                while horiz <= 9:
                    horiz += 1
                    if horiz in HALLWAYS and HOME_HORIZ[amph] != horiz:
                        continue
                    if HOME_HORIZ[amph] == horiz:
                        if (horiz, 2) not in self.populated:
                            results.append(
                                (
                                    cost_between_points(loc, Location(horiz, 2)),
                                    self.new_state_with_swap(
                                        (loc.horiz, loc.vert), (horiz, 2)
                                    ),
                                )
                            )
                        elif (horiz, 1) not in self.populated and self.loc_at(
                            horiz, 2
                        ).is_locked:
                            results.append(
                                (
                                    cost_between_points(loc, Location(horiz, 1)),
                                    self.new_state_with_swap(
                                        (loc.horiz, loc.vert), (horiz, 1)
                                    ),
                                )
                            )
                        continue
                    if (horiz, 0) in self.populated:
                        break
                    results.append(
                        (
                            cost_between_points(loc, Location(horiz, 0)),
                            self.new_state_with_swap((loc.horiz, loc.vert), (horiz, 0)),
                        )
                    )
            else:
                # they're already in the hallway, so their only valid move is to go home
                # to go home, they have to be:
                # * unblocked to get there
                # * if there is someone in the home, it has to be locked in
                targ_horiz = HOME_HORIZ[amph]
                if (targ_horiz, 2) in self.populated and not self.loc_at(
                    targ_horiz, 2
                ).is_locked:
                    # can't enter a non-empty hallway that a non-resident is in
                    continue
                if (targ_horiz, 1) in self.populated:
                    # someone is blocking the entrance
                    continue

                op = add if targ_horiz > horiz else sub
                is_blocked = False
                while horiz != targ_horiz:
                    horiz = op(horiz, 1)
                    if (horiz, 0) in self.populated:
                        is_blocked = True
                        break

                if is_blocked:
                    continue

                # otherwise, it's valid to move the spot in the open to their hallway
                targ_vert = 1 if (targ_horiz, 2) in self.populated else 2
                results.append(
                    (
                        cost_between_points(loc, Location(targ_horiz, targ_vert)),
                        self.new_state_with_swap(
                            (loc.horiz, loc.vert), (targ_horiz, targ_vert)
                        ),
                    )
                )

        return results

    def can_move(self, horiz: int, vert: int) -> bool:
        """
        Returns `False` if the amph is under another, `True` otherwise
        """
        if vert == 2:
            return not self.loc_at(horiz, 1).value
        return True

    def new_state_with_swap(self, old: GridPoint, new: GridPoint) -> "State":
        # print(f"swapping {old} to {new}")
        new_pop = self.populated.copy()
        del new_pop[old]
        new_pop[new] = self.populated[old]
        return State(new_pop)

    @cached_property
    def frozen(self) -> str:
        """
        Used to serialize this state into a set
        """
        return "|".join(f"{k}:{v}" for k, v in sorted(self.populated.items()))

    def __lt__(self, o):
        return False


class Solution(TextSolution):
    _year = 2021
    _day = 23

    # @answer(1234)
    def part_1(self) -> int:
        start_order: List[Amphipod] = re.findall(r"[ABCD]", self.input)
        locations = {}
        i = 0
        for vert in [1, 2]:
            for horiz in [2, 4, 6, 8]:
                locations[(horiz, vert)] = start_order[i]
                i += 1

        # assert len(locations) == 8
        start = State(locations)
        # self.pp(world)
        # assert not world.did_win
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
                # self.pp(next_state)
                assert (
                    next_move_cost
                ), f"moving to {next_state} was free, shouldn't have been"
                if next_state.frozen in visited:
                    continue

                total_cost = cost + next_move_cost

                if total_cost < distances[next_state.frozen]:
                    distances[next_state.frozen] = total_cost
                    heappush(queue, (total_cost, next_state))

            # self.pp(queue)
            # break

        raise RuntimeError("No solution found")

        # self.pp(list(enumerate(next_states)))
        # for pick in [15, 3, 6, 5, 4, 4, 3, 0, 0, 0]:
        #     print("-----------")
        #     world = next_states[pick][1]
        #     next_states = world.next_states()
        #     self.pp(list(enumerate(next_states)))

        # assert world.did_win

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> Tuple[int, int]:
    #     pass
