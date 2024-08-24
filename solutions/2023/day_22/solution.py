# prompt: https://adventofcode.com/2023/day/22


from dataclasses import dataclass

from ...base import StrSplitSolution, answer

type Cube = tuple[int, int, int]


@dataclass
class Brick:
    id_: int
    cubes: set[Cube]
    lowest_z: int

    @staticmethod
    def parse(id_: int, s: str) -> "Brick":
        start, end = [ss.split(",") for ss in s.split("~")]

        dims = [
            int(l) if l == r else range(int(l), int(r) + 1) for l, r in zip(start, end)
        ]

        match dims:
            case int(x), int(y), range() as r:
                cubes = {(x, y, z) for z in r}
            case int(x), range() as r, int(z):
                cubes = {(x, y, z) for y in r}
            case range() as r, int(y), int(z):
                cubes = {(x, y, z) for x in r}
            case int(x), int(y), int(z):
                cubes = {(x, y, z)}
            case _:
                raise ValueError(f"invalid shape: {s}")

        lowest_z = dims[2] if isinstance(dims[2], int) else dims[2].start

        return Brick(id_, cubes, lowest_z)

    def intersects(self, other: "Brick") -> bool:
        return bool(self.cubes & other.cubes)

    def fall(self) -> "Brick":
        # refuse to fall if on the ground
        if self.on_ground:
            return self

        return Brick(
            self.id_,
            {(x, y, z - 1) for x, y, z in self.cubes},
            self.lowest_z - 1,
        )

    @property
    def on_ground(self) -> bool:
        return self.lowest_z == 1

    def __lt__(self, other: "Brick") -> bool:
        return self.lowest_z < other.lowest_z


class Solution(StrSplitSolution):
    _year = 2023
    _day = 22

    @answer((421, 39247))
    def solve(self) -> tuple[int, int]:
        bricks = sorted(Brick.parse(idx, l) for idx, l in enumerate(self.input))

        settled_bricks: list[Brick] = []
        settled_cubes: set[Cube] = set()

        for brick in bricks:
            cur_pos = brick
            while not (
                cur_pos.on_ground or (next_pos := cur_pos.fall()).cubes & settled_cubes
            ):
                cur_pos = next_pos

            settled_bricks.append(cur_pos)
            settled_cubes |= cur_pos.cubes

        supported_by: dict[int, set[int]] = {}
        for settled_brick in settled_bricks:
            if settled_brick.on_ground:
                continue

            below = settled_brick.fall()
            supported_by[settled_brick.id_] = {
                other.id_
                for other in settled_bricks
                if settled_brick.id_ != other.id_ and below.intersects(other)
            }

        num_bricks = len(self.input)
        num_load_bearing = len(
            set().union(*(s for s in supported_by.values() if len(s) == 1))
        )
        num_safe_to_remove = num_bricks - num_load_bearing

        chain_reaction_total = 0
        for settled_brick in range(num_bricks):
            removed = {settled_brick}

            while True:
                would_fall = {k for k, v in supported_by.items() if v <= removed}
                # sub 1 to account for the staring brick which won't be in `would_fall`
                if len(would_fall) == len(removed) - 1:
                    chain_reaction_total += len(would_fall)
                    break

                # find bricks that are supported by _anything_ we've pulled on next loop
                removed |= would_fall

        return num_safe_to_remove, chain_reaction_total
