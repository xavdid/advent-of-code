# prompt: https://adventofcode.com/2017/day/8

from ...base import BaseSolution, InputTypes
from collections import defaultdict
from operator import gt, lt, ge, le, eq, ne, add, sub


class Solution(BaseSolution):
    year = 2017
    input_type = InputTypes.ARRAY

    def solve(self):
        ops = {
            ">": gt,
            "<": lt,
            ">=": ge,
            "<=": le,
            "==": eq,
            "!=": ne,
            "inc": add,
            "dec": sub,
        }
        res = defaultdict(int)

        biggest = 0

        for row in self.input:
            [var, var_op, op_val, _, cond_var, cond_op, cond_val] = row.split(" ")
            if ops[cond_op](res[cond_var], int(cond_val)):
                next_val = ops[var_op](res[var], int(op_val))
                res[var] = next_val
                biggest = max(biggest, next_val)

        return (max(res.values()), biggest)
