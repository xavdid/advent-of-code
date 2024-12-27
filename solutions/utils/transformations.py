from itertools import compress, repeat
from typing import Iterable


def parse_ints(l: Iterable[str]) -> list[int]:
    return [int(i) for i in l]


def ilen(i: Iterable) -> int:
    """
    Return the number of items in *i*.

        >>> ilen(x for x in range(1000000) if x % 3 == 0)
        333334

    This consumes the i, so handle with care.

    Pulled directly from more_itertools: https://more-itertools.readthedocs.io/en/latest/api.html#more_itertools.ilen

    > note to self: uses zip so that every item in `i` is truthy. otherwise, elements that happen to be falsy (but should otherwise be included in the result) are skipped). For instance, `sum(compress(repeat(1), range(3)))` returns `2`, because the first `0` is excluded. However, the 1-tuple `(0,)` is correctly included.
    """
    return sum(compress(repeat(1), zip(i)))
