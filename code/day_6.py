# prompt: https://adventofcode.com/2017/day/6

from base import BaseSolution, InputTypes

class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.TSV

    def part_1(self):
        return self.solve()[0]

    def part_2(self):
        return self.solve()[1]

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
        arr = self.input[0]  # don't mutate input
        seen = [arr[:]]

        while True:  # python could use a do-while
            arr = self.redistribute(arr)
            if arr in seen:
                break
            else:
                seen.append(arr[:])

        return (len(seen), len(seen) - seen.index(arr))
