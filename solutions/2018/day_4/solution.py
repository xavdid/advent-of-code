# prompt: https://adventofcode.com/2018/day/4

from ...base import BaseSolution, InputTypes
from collections import defaultdict
from itertools import chain
from statistics import mode
from operator import itemgetter


class Solution(BaseSolution):
    _year = 2018
    _number = 4

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def guard_score(self, t):
        """
        takes a tuple of (guard_id, sleepiest_minute, num_times_slept_in_that_minute)
        """
        return int(t[0]) * t[1]

    def parse_reports(self):
        guards = defaultdict(list)
        g = None
        date = None
        start = None
        for line in sorted(self.input):
            parts = line.split(" ")
            if line.endswith("shift"):
                g = parts[3][1:]
            if line.endswith("asleep"):
                date = parts[0][-5:]
                start = int(parts[1][-3:-1])
            if line.endswith("up"):
                end = int(parts[1][-3:-1])
                guards[g].append((date, range(start, end)))

        return guards

    def solve(self):
        guards = self.parse_reports()

        # [(id, total_minutes_slept)]
        guards_by_minutes_slept = sorted(
            [
                (guard, sum([len(s[1]) for s in shifts]))
                for guard, shifts in guards.items()
            ],
            key=itemgetter(1),
        )

        sleepiest_guard_id = guards_by_minutes_slept[-1][0]

        # [(id, sleepiest_minute, num_times_slept_that_minute)]
        most_reliable_minutes = []
        for guard, _ in guards_by_minutes_slept:
            # flat list of each minute this guard slept
            minutes_asleep = list(chain(*[s[1] for s in guards[guard]]))

            # how many times they slept on each minute
            min_by_num_slept = {i: minutes_asleep.count(i) for i in minutes_asleep}
            sleepiest_minute = max(min_by_num_slept.items(), key=itemgetter(1))

            # stores the minute during which the slept most often
            most_reliable_minutes.append((guard, *sleepiest_minute))

        # part 1
        sleepiest_guard_report = next(
            x for x in most_reliable_minutes if x[0] == sleepiest_guard_id
        )

        # part 2
        reliable_guard_report = sorted(most_reliable_minutes, key=itemgetter(2))[-1]

        return (
            self.guard_score(sleepiest_guard_report),
            self.guard_score(reliable_guard_report),
        )
