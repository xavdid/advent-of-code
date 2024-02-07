# prompt: https://adventofcode.com/2023/day/20

from collections import Counter, deque
from dataclasses import dataclass

from ...base import StrSplitSolution, answer

# from, high pulse?, to
Pulse = tuple[str, bool, str]


@dataclass
class BaseModule:
    name: str
    targets: list[str]

    def build_pulses(self, is_high_pulse: bool) -> list[Pulse]:
        return [(self.name, is_high_pulse, t) for t in self.targets]

    def send(self, source: str, is_high_pulse: bool) -> list[Pulse]:
        raise NotImplementedError()

    def register_sources(self, sources: list[str]):
        raise NotImplementedError()


class FlipFlopModule(BaseModule):
    state = False

    def send(self, _: str, is_high_pulse: bool) -> list[Pulse]:
        # high pulses are ignored
        if is_high_pulse:
            return []

        # otherwise, invert and send new state pulse to all targets
        self.state = not self.state

        return self.build_pulses(self.state)


class ConjunctionModule(BaseModule):
    _sources: dict[str, bool] = {}

    def send(self, source: str, is_high_pulse: bool) -> list[Pulse]:
        self._sources[source] = is_high_pulse

        # if all high, send low
        # else, high
        to_send = not all(self._sources.values())

        return self.build_pulses(to_send)

    def register_sources(self, sources: list[str]):
        if self._sources:
            raise ValueError("already registered sources!")
        self._sources = {s: False for s in sources}


class Computer:
    modules: dict[str, BaseModule] = {}

    def __init__(self, lines: list[str]) -> None:
        # first pass: identify conjunction modules and initialize an empty array of what points at them
        conj_modules = {
            line.split(" ")[0][1:]: [] for line in lines if line.startswith("&")
        }

        # second pass: generate and store BaseModule classes
        for line in lines:
            raw_source, raw_target = line.split(" -> ")
            source = raw_source[1:]
            targets = raw_target.split(", ")

            for t in targets:
                if t in conj_modules:
                    conj_modules[t].append(source)

            if raw_source == "broadcaster":
                self.initial_targets = targets
            if raw_source.startswith("%"):
                self.modules[source] = FlipFlopModule(source, targets)
            if raw_source.startswith("&"):
                self.modules[source] = ConjunctionModule(source, targets)

        for k, v in conj_modules.items():
            self.modules[k].register_sources(v)

    def push_button(self) -> Counter:
        queue: deque[Pulse] = deque(
            ("broadcaster", False, t) for t in self.initial_targets
        )

        # False starts at 1 for button -> broadcaster
        pulse_counts = Counter({False: 1})

        while queue:
            source, pulse, target = queue.popleft()
            pulse_counts[pulse] += 1

            # ignore writing to `rx` or `output`
            if target not in self.modules:
                continue

            queue += self.modules[target].send(source, pulse)

        return pulse_counts

    def run(self):
        totals = sum((self.push_button() for _ in range(1000)), Counter())

        return totals[False] * totals[True]


class Solution(StrSplitSolution):
    _year = 2023
    _day = 20

    @answer(763500168)
    def part_1(self) -> int:
        return Computer(self.input).run()

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
