# prompt: https://adventofcode.com/2024/day/10


from ...base import StrSplitSolution, answer
from ...utils.graphs import GridPoint, IntGrid, neighbors, parse_grid


def score_trailhead(grid: IntGrid, trailhead: GridPoint, *, skip_visited: bool) -> int:
    score = 0
    visited: set[GridPoint] = set()

    queue: list[GridPoint] = [trailhead]

    while queue:
        cur = queue.pop()

        if skip_visited:
            if cur in visited:
                continue

            visited.add(cur)

        if (val := grid[cur]) == 9:
            score += 1
            continue

        queue.extend(
            n for n in neighbors(cur, num_directions=4) if grid.get(n) == val + 1
        )

    return score


class Solution(StrSplitSolution):
    _year = 2024
    _day = 10

    @answer((737, 1619))
    def solve(self) -> tuple[int, int]:
        grid = parse_grid(self.input, int_vals=True)

        return tuple(  # type: ignore
            sum(
                score_trailhead(grid, trailhead, skip_visited=skip_visited)
                for trailhead, v in grid.items()
                if v == 0
            )
            for skip_visited in (True, False)
        )
