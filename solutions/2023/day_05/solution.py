# prompt: https://adventofcode.com/2023/day/5

from itertools import batched, chain

from ...base import TextSolution, answer

Transformation = tuple[range, int]


def parse_range(line: str) -> Transformation:
    dest_start, source_start, size = map(int, line.split())

    return range(source_start, source_start + size), dest_start - source_start


def parse_map(map_block: str) -> list[Transformation]:
    return sorted(
        [parse_range(l) for l in map_block.split("\n")[1:]], key=lambda r: r[0].start
    )


def mask_number(num: int, transformations: list[Transformation]) -> int:
    for mask, offset in transformations:
        if num in mask:
            return num + offset
    return num


def do_ranges_overlap(a: range, b: range) -> bool:
    return a.start < b.stop and b.start < a.stop


def shift_range(r: range, offset: int) -> range:
    return range(r.start + offset, r.stop + offset)


def apply_transformations(base: range, transforms: list[Transformation]) -> list[range]:
    for mask, offset in transforms:
        # 1 - no overlap; skip this mask
        if not do_ranges_overlap(base, mask):
            continue

        # 2 - base is inside mask, shift entire base
        if mask.start <= base.start and base.stop <= mask.stop:
            return [shift_range(base, offset)]

        # 3 - mask is a subset of base
        # return unshifted left, shifted middle, and recurse for the rest
        if base.start <= mask.start and mask.stop <= base.stop:
            return [
                range(base.start, mask.start),
                shift_range(mask, offset),
                *apply_transformations(range(mask.stop, base.stop), transforms),
            ]

        # 4 - mask overlaps only the left side,
        # return masked left, recurse for the rest
        if mask.start <= base.start and mask.stop <= base.stop:
            return [
                shift_range(range(base.start, mask.stop), offset),
                *apply_transformations(range(mask.stop, base.stop), transforms),
            ]

        # 5 - mask overlaps only the right side
        # return unshifted left, masked right
        if base.start <= mask.start and base.stop <= mask.stop:
            return [
                range(base.start, mask.start),
                shift_range(range(mask.start, base.stop), offset),
            ]

    # no masks overlapped this base; pass it through
    return [base]


class Solution(TextSolution):
    _year = 2023
    _day = 5

    @answer(462648396)
    def part_1(self) -> int:
        blocks = self.input.split("\n\n")
        seeds = [int(s) for s in blocks[0][6:].split()]

        map_layers = [parse_map(b) for b in blocks[1:]]

        result = []
        for seed in seeds:
            for transformations in map_layers:
                seed = mask_number(seed, transformations)  # noqa: PLW2901

            result.append(seed)

        return min(result)

    @answer(2520479)
    def part_2(self) -> int:
        blocks = self.input.split("\n\n")
        seeds = [
            range(start, start + size)
            for start, size in batched(map(int, blocks[0][6:].split()), 2)
        ]

        transformations = [parse_map(b) for b in blocks[1:]]

        result = []
        for seed_range in seeds:
            ranges = [seed_range]

            for block in transformations:
                ranges = list(
                    chain.from_iterable(apply_transformations(r, block) for r in ranges)
                )

            result.append(sorted(ranges, key=lambda r: r.start)[0].start)

        return min(result)
