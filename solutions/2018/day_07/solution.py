# prompt: https://adventofcode.com/2018/day/7

from ...base import BaseSolution, InputTypes
from collections import defaultdict

# changes from example to actual puzzle
NUM_WORKERS = 5
DURATION = 60


class Solution(BaseSolution):
    _year = 2018
    _day = 7

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def num_seconds(self, letter):
        return DURATION + 1 * (ord(letter) - 64)

    def build_map(self):
        # map Node -> pre-reqs
        self.all_nodes = set()
        self.instructions = defaultdict(set)
        self.pre_reqs = defaultdict(set)

        potential_starting_points = set()
        for line in self.input:
            a = line[5]
            b = line[36]
            self.instructions[a].add(b)
            self.pre_reqs[b].add(a)
            self.all_nodes.update({a, b})

            # have to find the point with no pre-reqs
            # can't just remove here, since order matters
            potential_starting_points.add(a)

        # could maintain both a list and a set if we're too slow?
        self.completed = []
        self.queue = potential_starting_points - set.union(
            *map(set, self.instructions.values())
        )

    def part_1(self):
        self.build_map()

        offset = 0
        while self.all_nodes - set(self.completed):
            cur = sorted(self.queue)[offset]
            if not self.pre_reqs[cur] - set(self.completed):  # all prereqs are met
                self.completed.append(cur)
                self.queue.discard(cur)
                self.queue.update(self.instructions[cur])
                offset = 0
            else:
                offset += 1

        return "".join(self.completed)

    def part_2(self):
        self.build_map()

        offset = 0
        t = 0
        # map<finish_at, letter>
        jobs = {}
        while self.all_nodes - set(self.completed):
            # complete jobs finishing now
            if t in jobs:
                self.completed.append(jobs.pop(t))

            # worksers pick up all availabble options until queue is empty or workers are busy
            for cur in sorted(self.queue):
                if len(jobs) == NUM_WORKERS:
                    break

                if not self.pre_reqs[cur] - set(self.completed):  # all prereqs are met
                    jobs[t + self.num_seconds(cur)] = cur
                    self.queue.discard(cur)
                    self.queue.update(self.instructions[cur])
                    offset = 0
            t += 1

        return t - 1

    def solve(self):
        pass
