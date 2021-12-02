# prompt: https://adventofcode.com/2018/day/8

from ...base import BaseSolution, InputTypes

"""
NOTE! I DID NOT WRITE THE BELOW. Credit goes to /u/sciyoshi on reddit (source: https://www.reddit.com/r/adventofcode/comments/a47ubw/2018_day_8_solutions/ebc7ol0/)

I worked on this for longer than any I had done before and then got tired of it; my soulution was recursive, but I was tracking way more data than I needed and I kept getting lost. Today, AoC beat me but tomorrow I will do better.
"""


class Solution(BaseSolution):
    _year = 2018
    _day = 8

    @property
    def input_type(self):
        return InputTypes.INTSPLIT

    @property
    def separator(self):
        return " "

    def solve(self):
        def parse(data):
            children, metas = data[:2]
            data = data[2:]
            scores = []
            totals = 0

            for i in range(children):
                total, score, data = parse(data)
                totals += total
                scores.append(score)

            totals += sum(data[:metas])

            if children == 0:
                return (totals, sum(data[:metas]), data[metas:])
            else:
                return (
                    totals,
                    sum(
                        scores[k - 1]
                        for k in data[:metas]
                        if k > 0 and k <= len(scores)
                    ),
                    data[metas:],
                )

        total, value, remaining = parse(self.input)

        return (total, value)
