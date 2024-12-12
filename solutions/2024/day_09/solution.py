# prompt: https://adventofcode.com/2024/day/9

from dataclasses import dataclass
from itertools import batched, chain
from typing import Literal

from ...base import TextSolution, answer
from ...utils.transformations import parse_ints


@dataclass
class Item:
    type: Literal["file", "gap"]
    size: int
    id_: int = 0


def expand(i: Item) -> list[int]:
    return [i.id_] * i.size


class Solution(TextSolution):
    _year = 2024
    _day = 9

    @answer(6385338159127)
    def part_1(self) -> int:
        # we pad for unpacking reasons, so we need the input to end on a file
        assert len(self.input) % 2 == 1

        # parse
        disk: dict[int, int] = {}
        max_write_location = 0

        for file_id, (file_size, gap_size) in enumerate(
            batched(parse_ints(self.input + "0"), 2)
        ):
            for pointer in range(max_write_location, max_write_location + file_size):
                disk[pointer] = file_id

            max_write_location += file_size + gap_size

        # pack
        writer = 0
        reader = max_write_location

        while True:
            while writer in disk:
                writer += 1

            while reader not in disk:
                reader -= 1

            if writer >= reader:
                break

            disk[writer] = disk[reader]
            del disk[reader]

        return sum(
            idx * disk.get(j, 0) for idx, j in enumerate(range(max_write_location))
        )

    @answer(6415163624282)
    def part_2(self) -> int:
        disk: list[Item] = []
        for file_id, (file_size, gap_size) in enumerate(
            batched(parse_ints(self.input + "0"), 2)
        ):
            disk.append(Item("file", id_=file_id, size=file_size))
            disk.append(Item("gap", gap_size))

        # the last item is the padded gap, so the 2nd to last item's id is the highest
        reader = len(disk) - 1
        for file_id in range(disk[-2].id_, -1, -1):
            while (f := disk[reader]).type != "file" or f.id_ != file_id:
                reader -= 1

            try:
                writer, g = next(
                    (writer, g)
                    for writer, g in enumerate(disk)
                    if g.type == "gap" and g.size >= f.size
                )
            except StopIteration:
                continue

            if writer > reader:
                continue

            disk[reader] = Item("gap", f.size)

            disk.insert(writer, f)
            g.size -= f.size

        return sum(
            idx * i for idx, i in enumerate(chain.from_iterable(map(expand, disk)))
        )
