# Each square on the grid is allocated in a spiral pattern starting at a location marked 1 and then counting up while spiraling outward. For example, the first few squares are allocated like this:

# (I've expanded the grid past what they gave us in the problem)

# 37  36  35  34  33  32  31
# 38  17  16  15  14  13  30
# 39  18   5   4   3  12  29
# 40  19   6   1   2  11  28
# 41  20   7   8   9  10  27
# 42  21  22  23  24  25  26
# 43  44  45  46  47  48  49

# While this is very space-efficient (no squares are skipped), requested data must be carried back to square 1 (the location of the only access port for this memory system) by programs that can only move up, down, left, or right. They always take the shortest path: the Manhattan Distance between the location of the data and square 1.

# For example:

# Data from square 1 is carried 0 steps, since it's at the access port.
# Data from square 12 is carried 3 steps, such as: down, left, left.
# Data from square 23 is carried only 2 steps: up twice.
# Data from square 1024 must be carried 31 steps.
# How many steps are required to carry the data from the square identified in your puzzle input all the way to the access port?

import math
from base import BaseSolution, InputTypes

class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.INTEGER

    def part_1(self):
        side = math.ceil(math.sqrt(self.input))  # odd-root for the side of the square we're in
        if side % 2 == 0:
            side += 1  # odd roots only

        max_distance = side - 1  # all numbers in this loop can only be this far

        # see how far our input is from the odd-square.
        # the possible values are a corner (max_distance) or the center of a row (half of that)
        steps = max_distance - ((side ** 2 - self.input) % max_distance)
        return int(steps)

    def part_2(self):
        # for this one, I cheated. All the numbers in the grid are here: https://oeis.org/A141481/b141481.txt
        # a full description of that sequence is available here: https://oeis.org/A141481
        return 266330
