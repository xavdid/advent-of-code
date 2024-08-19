# prompt: https://adventofcode.com/2023/day/22

from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from ...base import StrSplitSolution, answer

# class Brick(NamedTuple):
#     id_: int
#     x: int | range
#     y: int | range
#     z: int | range

#     @staticmethod
#     def parse(s: str, id_: int) -> "Brick":
#         start, end = [ss.split(",") for ss in s.split("~")]
#         args: list[int | range] = [id_]
#         for l, r in zip(start, end):
#             if l == r:
#                 args.append(int(l))
#             else:
#                 assert int(l) < int(r)
#                 args.append(range(int(l), int(r) + 1))

#         return Brick(*args)

#     def fall(self) -> tuple["Brick", bool]:
#         """
#         Tries to fall. Returns the result of that operation and whether there was a change
#         """
#         if self.lowest_z == 1:
#             return self, False

#         if isinstance(self.z, range):
#             return Brick(
#                 self.id_, self.x, self.y, range(self.z.start - 1, self.z.stop - 1)
#             ), True

#         return Brick(self.id_, self.x, self.y, self.z - 1), True

#     def rise(self) -> "Brick":
#         """
#         Rises!
#         """

#         if isinstance(self.z, range):
#             return Brick(
#                 self.id_, self.x, self.y, range(self.z.start + 1, self.z.stop + 1)
#             )

#         return Brick(self.id_, self.x, self.y, self.z + 1)

#     @property
#     def lowest_z(self) -> int:
#         if isinstance(self.z, range):
#             return self.z.start
#         return self.z

#     def intersects(self, other: "Brick") -> bool:
#         num_overlap = 0
#         for dim in "x", "y", "z":
#             match getattr(self, dim), getattr(other, dim):
#                 case int(l), int(r) if l == r:
#                     # print(f"    A({self.id_} <-> {other.id_}): {l}, {r}")
#                     num_overlap += 1
#                 case int(l), range() as r if l in r:
#                     # print(f"    B({self.id_} <-> {other.id_}): {l}, {r}")
#                     num_overlap += 1
#                 case range() as l, int(r) if r in l:
#                     # print(f"    C({self.id_} <-> {other.id_}): {l}, {r}")
#                     num_overlap += 1
#                 case (
#                     range() as l,
#                     range() as r,
#                 ) if l.stop >= r.start and r.stop >= l.start:
#                     # https://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html
#                     # print(f"    D({self.id_} <-> {other.id_}): {l}, {r}")
#                     num_overlap += 1

#         return num_overlap >= 3


@dataclass(frozen=True)
class BrickV2:
    id_: int
    x: int | range
    y: int | range
    z: int | range

    @cached_property
    def lowest_z(self) -> int:
        if isinstance(self.z, range):
            return self.z.start
        return self.z

    @cached_property
    def points(self) -> frozenset[tuple[int, int, int]]:
        match self.x, self.y, self.z:
            case int(x), int(y), range() as r:
                return frozenset((x, y, z) for z in r)
            case int(x), range() as r, int(z):
                return frozenset((x, y, z) for y in r)
            case range() as r, int(y), int(z):
                return frozenset((x, y, z) for x in r)
            case int(x), int(y), int(z):
                return frozenset([(x, y, z)])
            case _:
                raise RuntimeError(f"invalid shape: {self}")

    def intersects(self, other: "BrickV2") -> bool:
        return bool(self.points & other.points)

    @staticmethod
    def parse(s: str, id_: int) -> "BrickV2":
        start, end = [ss.split(",") for ss in s.split("~")]
        args: dict[str, int | range] = {"id_": id_}
        for dim, l, r in zip("xyz", start, end):
            if l == r:
                args[dim] = int(l)
            else:
                assert int(l) < int(r)
                args[dim] = range(int(l), int(r) + 1)

        return BrickV2(**args)  # type: ignore

    def fall(self) -> tuple["BrickV2", bool]:
        """
        Tries to fall. Returns the result of that operation and whether there was a change
        """
        if self.lowest_z == 1:
            return self, False

        if isinstance(self.z, range):
            return BrickV2(
                self.id_, self.x, self.y, range(self.z.start - 1, self.z.stop - 1)
            ), True

        return BrickV2(self.id_, self.x, self.y, self.z - 1), True

    def rise(self) -> "BrickV2":
        """
        Tries to fall. Returns the result of that operation and whether there was a change
        """

        if isinstance(self.z, range):
            return BrickV2(
                self.id_, self.x, self.y, range(self.z.start + 1, self.z.stop + 1)
            )

        return BrickV2(self.id_, self.x, self.y, self.z + 1)


class Solution(StrSplitSolution):
    _year = 2023
    _day = 22

    @answer(421)
    # 426 is too high
    def part_1(self) -> int:
        self.debug("starting")
        bricks = sorted(
            (BrickV2.parse(l, idx) for idx, l in enumerate(self.input)),
            key=lambda b: b.lowest_z,
        )
        self.debug("parsed bricks")

        self.debug(bricks)

        settled_bricks: list[BrickV2] = []
        total_bricks = len(bricks)
        self.debug(f"dropping {total_bricks} bricks")
        for i, b in enumerate(bricks):
            self.debug(f"  dropping {i+1:04}/{total_bricks}")
            cur_pos = b
            while True:
                # self.debug(f"  at {cur_pos.lowest_z}")
                next_pos, could_fall = cur_pos.fall()
                if (not could_fall) or any(
                    next_pos.intersects(other)
                    for other in settled_bricks
                    if other.id_ != next_pos.id_ and other.lowest_z < cur_pos.lowest_z
                ):
                    # self.debug("    settled")
                    settled_bricks.append(cur_pos)
                    break

                # self.debug(f"    falling {cur_pos.lowest_z} -> {next_pos.lowest_z}")
                cur_pos = next_pos

        # self.debug(settled_bricks)

        supporters: dict[int, list[int]] = {}

        self.debug("building tree")
        for b in settled_bricks:
            above = b.rise()

            supporters[b.id_] = [
                o.id_ for o in settled_bricks if b.id_ != o.id_ and above.intersects(o)
            ]
            # self.debug(f"{b.id_} has {num_touching} touching")
            # if num_touching != 1:
            #     result += 1

        self.debug(supporters)

        inverted = defaultdict(list)

        self.debug("inverting tree")
        for supporter, supported_bricks in supporters.items():
            for supported in supported_bricks:
                inverted[supported].append(supporter)

        self.debug(inverted)

        self.debug("counting bricks")
        seen_alone = set(supporters.keys())

        for z in inverted.values():
            if len(z) == 1:
                seen_alone.discard(z[0])

        # self.debug(seen_alone)
        return len(seen_alone)

        # return sum(

        #     for b in settled_bricks
        #     if not any(b.intersects(o) for o in settled_bricks if b.id_ != o.id_)
        # )

        # find all bricks at the lowest z and fall them all until they stop moving. Then set a new lowest and fall them; decreasing the floor as you fall past your re-set low point

    # @answer(1234)
    def part_2(self) -> int:
        pass

    # @answer((1234, 4567))
    # def solve(self) -> tuple[int, int]:
    #     pass
