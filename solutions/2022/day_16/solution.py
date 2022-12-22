# prompt: https://adventofcode.com/2022/day/16
# adapted from:
# https://www.reddit.com/r/adventofcode/comments/zn6k1l/2022_day_16_solutions/j0gqhgs/

import heapq
from dataclasses import dataclass
from typing import Iterable

from ...base import StrSplitSolution, answer


@dataclass(frozen=True)
class Valve:
    name: str
    rate: int

    @classmethod
    def from_str(cls, raw_valve: str) -> tuple["Valve", list[str]]:
        parts = raw_valve.split(" ", maxsplit=9)
        return Valve(parts[1], int(parts[4][:-1].split("=")[-1])), parts[-1].split(", ")

    # so that the dataclass is technically sortable
    # (a requirement to be used in a priority queue)
    def __lt__(self, _):
        return False


NeighborMap = dict[Valve, list[Valve]]


class Solution(StrSplitSolution):
    _year = 2022
    _day = 16
    # Valve object to a map of other Valves and their distances
    graph: dict[Valve, dict[Valve, int]] = {}

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

    def parse_valves(self) -> Valve:
        """
        parses input and creates the following:

        - `self.graph`, a mapping of Valve -> {Valve -> distance to valve}
        - returns the starting valve object (AA)
        """
        # name to Valve object
        valves: dict[str, Valve] = {}

        raw_neighbors: dict[str, list[str]] = {}
        for line in self.input:
            valve, str_paths = Valve.from_str(line)
            valves[valve.name] = valve
            raw_neighbors[valve.name] = str_paths

        # map of valve -> materialized neighbor valves
        neighbors: NeighborMap = {
            valves[raw_valve]: [valves[n] for n in neighbor_names]
            for raw_valve, neighbor_names in raw_neighbors.items()
        }

        # always start at AA
        starting_valve = valves["AA"]

        # next, get distance from each node to every other
        self.graph = {
            valve: self.calculate_distances(neighbors, valve)
            for valve in neighbors
            if valve is starting_valve or valve.rate
        }

        return starting_valve

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

    def score_sequence(self, sequence: list[Valve], time: int) -> int:
        total = 0
        current = Valve("AA", 0)

        for next_valve in sequence:
            time -= self.graph[current][next_valve] + 1
            total += time * next_valve.rate
            current = next_valve

        return total

    @answer((1751, 2207))
    def solve(self) -> tuple[int, int]:
        starting_valve = self.parse_valves()
        valves_to_check = {k for k in self.graph if k is not starting_valve}

        max_steam_alone = max(
            self.score_sequence(sequence, 30)
            for sequence in self.every_sequence(
                current_valve=starting_valve,
                valves_to_check=valves_to_check,
                working_sequence=[],
                time=30,
            )
        )

        sequences: list[tuple[int, set[Valve]]] = sorted(
            (
                (self.score_sequence(sequence, 26), set(sequence))
                for sequence in self.every_sequence(
                    starting_valve, valves_to_check, [], 26
                )
            ),
            reverse=True,
        )

        score = 0
        for index, (score_a, sequence_a) in enumerate(sequences):
            # we're sorting by descending score, so if we hit one that won't beat
            # the current record when doubled, we'll never find a winner
            if score_a * 2 < score:
                break
            for score_b, sequence_b in sequences[index + 1 :]:
                # only consider sets of sequences that have no overlapping moves
                if not sequence_a & sequence_b:
                    score = max(score, score_a + score_b)

        return max_steam_alone, score
