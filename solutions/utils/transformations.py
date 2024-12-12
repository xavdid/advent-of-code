from typing import Iterable


def parse_ints(l: Iterable[str]) -> list[int]:
    return [int(i) for i in l]
