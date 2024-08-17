# prompt: https://adventofcode.com/2017/day/16

from collections import deque

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    _year = 2017
    _day = 16

    @property
    def separator(self):
        return "\n"

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def part_1(self):
        return self._solve(1)

    def part_2(self):
        return self._solve(1_000_000_000)

    def _solve(self, num_dances):
        def swap(s, i, j):
            l = list(s)
            t = l[i]
            l[i] = l[j]
            l[j] = t
            return "".join(l)

        programs = "".join([chr(i) for i in range(97, 97 + 16)])
        seen = []

        for n in range(num_dances):
            # using a dict with the result pre-calculated worked, but was way too slow
            # if programs in seen:
            #     programs = seen[programs]
            #     continue

            # instead, once we're in a loop, we don't have to keep doing it; we know the outcome
            # what we don't know is how long the loop is, but we can know where in the sequence we'll be after 1bil tries
            if programs in seen:
                return seen[num_dances % n]
            seen.append(programs)

            for i in self.input:
                if i[0] == "s":
                    d = deque(programs)
                    d.rotate(int(i[1:]))
                    programs = "".join(d)
                elif i[0] == "x":
                    [i, j] = [int(i) for i in i[1:].split("/")]  # noqa: PLW2901
                    programs = swap(programs, i, j)
                elif i[0] == "p":
                    [prog_1, prog_2] = i[1:].split("/")
                    programs = swap(
                        programs, programs.index(prog_1), programs.index(prog_2)
                    )
                else:
                    raise BaseException("who knows")

        return "".join(programs)
