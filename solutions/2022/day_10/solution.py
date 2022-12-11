# prompt: https://adventofcode.com/2022/day/10


from typing import Tuple

from ...base import StrSplitSolution, answer

REPORTING_CYCLES = {20, 60, 100, 140, 180, 220}


class Solution(StrSplitSolution):
    _year = 2022
    _day = 10

    @answer((14420, "RGLRBZAU"))
    def solve(self) -> Tuple[int, str]:
        x = 1
        signal_strength = 0
        instruction_pointer = 0
        in_addx = False
        pixels = []
        for cycle in range(1, 241):
            # start cycle!

            instruction = self.input[instruction_pointer].split()
            addx = 0

            if instruction == ["noop"]:
                pass
            elif instruction[0] == "addx":
                if in_addx:
                    in_addx = False
                    addx = int(instruction[1])
                else:
                    in_addx = True

            if cycle in REPORTING_CYCLES:
                signal_strength += cycle * x

            # draw pixel
            if x - 1 <= (cycle - 1) % 40 <= x + 1:
                pixels.append("#")
            else:
                pixels.append(".")

            # end cycle!

            if not in_addx:
                x += addx
                instruction_pointer += 1

        print()
        # print each chunk of 40 pixels on a line
        print(
            "\n".join(
                "".join(l) for l in [pixels[i : i + 40] for i in range(0, 241, 40)]
            )
        )

        # Capital letters should print out in the terminal
        return signal_strength, "RGLRBZAU"
