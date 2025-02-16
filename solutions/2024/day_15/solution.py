# prompt: https://adventofcode.com/2024/day/15


from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, add_points, parse_grid

OFFSETS = {
    "<": (0, -1),
    ">": (0, 1),
    "^": (-1, 0),
    "v": (1, 0),
    "[": (0, 1),
    "]": (0, -1),
}

SWAPS = {
    "[": "]",
    "]": "[",
}


class Solution(StrSplitSolution):
    _year = 2024
    _day = 15
    separator = "\n\n"

    @answer(1457740)
    def part_1(self) -> int:
        grid = parse_grid(self.input[0].splitlines(), ignore_chars="#")
        moves = self.input[1].replace("\n", "")

        loc = next(k for k, v in grid.items() if v == "@")

        for move in moves:
            offset = OFFSETS[move]
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            if grid[next_loc] == "O":
                next_block = next_loc
                while grid.get(next_block) == "O":
                    next_block = add_points(next_block, offset)

                if grid.get(next_block) == ".":
                    grid[next_block] = "O"
                else:
                    continue

            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc

        return sum(100 * row + col for (row, col), c in grid.items() if c == "O")

    @answer(1467145)
    def part_2(self) -> int:
        raw_wide_grid = [
            s.replace(".", "..")
            .replace("#", "##")
            .replace("@", "@.")
            .replace("O", "[]")
            for s in self.input[0].splitlines()
        ]
        grid = parse_grid(raw_wide_grid, ignore_chars="#")

        # num_rows = len(raw_wide_grid)
        # num_cols = len(raw_wide_grid[0])
        # def print_grid():
        #     print("\n   ", end="")
        #     for cc in range(num_cols):
        #         print(f"{str(cc)[0] if cc >= 10 else '0'}", end="")
        #     print()
        #     print("   ", end="")
        #     for cc in range(num_cols):
        #         print(f"{str(cc)[-1]}", end="")
        #     print()
        #     for r in range(num_rows):
        #         print(f"{r:02} ", end="")
        #         for c in range(num_cols):
        #             print(grid.get((r, c), "#"), end="")
        #         print()
        #     print()

        # print_grid()

        loc = next(k for k, v in grid.items() if v == "@")
        moves = self.input[1].replace("\n", "")

        for move in moves:
            # for i in range(8):
            # move = moves[i]
            # sleep(0.25)
            # os.system("clear")
            # print(f"{move} from {loc}")
            # print_grid()
            offset = OFFSETS[move]
            if (next_loc := add_points(loc, offset)) not in grid:
                continue

            if grid[next_loc] in "[]":
                if move in "v^":
                    rows: list[list[GridPoint]] = [
                        [next_loc, add_points(next_loc, OFFSETS[grid[next_loc]])]
                    ]
                    can_move = True
                    while True:
                        next_row = {add_points(offset, p) for p in rows[-1]}
                        next_row |= {
                            add_points(p, OFFSETS[grid[p]])
                            for p in next_row
                            if grid.get(p, "x") in "[]"
                        }

                        if any(p not in grid for p in next_row):
                            can_move = False
                            break

                        if next_boxes := [p for p in next_row if grid[p] in "[]"]:
                            # loop!
                            rows.append(next_boxes)
                        else:
                            break

                    if not can_move:
                        continue

                    for row in reversed(rows):
                        for p in row:
                            dest = add_points(p, offset)
                            grid[dest] = grid[p]
                            grid[p] = "."

                else:
                    target_loc = next_loc
                    blocks = [target_loc]
                    while grid.get(target_loc, "x") in "[]":
                        target_loc = add_points(target_loc, offset)
                        blocks.append(target_loc)

                    if grid.get(target_loc) == ".":
                        grid[target_loc] = SWAPS[grid[blocks[0]]]
                        for b in blocks[:-1]:
                            grid[b] = SWAPS[grid[b]]
                    else:
                        continue

            grid[next_loc] = "@"
            grid[loc] = "."
            loc = next_loc

        return sum(100 * row + col for (row, col), c in grid.items() if c == "[")
