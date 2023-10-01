# prompt: https://adventofcode.com/2017/day/6

import csv

from ...base import StrSplitSolution


class Solution(StrSplitSolution):
    _year = 2017
    _day = 6

    def _parse_tsv(self):
        reader = csv.reader(self.input, delimiter="\t")
        return [[int(i) for i in row] for row in reader]

    def redistribute(self, arr):
        biggest = max(arr)
        i = arr.index(biggest)
        arr[i] = 0
        i += 1
        while biggest > 0:
            arr[i % len(arr)] += 1
            i += 1
            biggest -= 1

        return arr

    def solve(self):
        arr = self._parse_tsv()[0]  # don't mutate input
        seen = [arr[:]]

        while True:  # python could use a do-while
            arr = self.redistribute(arr)
            if arr in seen:
                break
            else:
                seen.append(arr[:])

        return (len(seen), len(seen) - seen.index(arr))
