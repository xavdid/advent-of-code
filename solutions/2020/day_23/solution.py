# prompt: https://adventofcode.com/2020/day/23

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List

from ...base import BaseSolution, slow


class Solution(BaseSolution):
    year = 2020
    number = 23

    def part_1(self) -> int:
        cups: Deque[int] = deque(map(int, self.input))
        current_cup_value = cups[0]

        for _ in range(100):
            # rotate until the current cup is 4 from the end
            assert current_cup_value in cups
            while cups[-4] != current_cup_value:
                cups.rotate()

            to_insert = [cups.pop(), cups.pop(), cups.pop()]
            to_insert.reverse()

            target_value = 9 if current_cup_value == 1 else current_cup_value - 1
            while target_value in to_insert:
                target_value = 9 if target_value == 1 else target_value - 1

            assert target_value in cups
            while cups[-1] != target_value:
                cups.rotate()

            cups.extend(to_insert)
            current_cup_value = cups[(cups.index(current_cup_value) + 1) % 9]

        assert 1 in cups
        while cups[0] != 1:
            cups.rotate()

        answer = "".join(map(str, cups))[1:]
        assert answer == "53248976"
        return answer

    @slow
    def part_2(self) -> int:
        @dataclass
        class Node:
            val: int
            # always defined, but not when the node is created
            next: "Node" = None

        list_size = 1_000_000
        num_loops = 10_000_000

        # https://gist.github.com/bluepichu/b42adaed79beba60ccdd53249a815d7e
        sequence: List[int] = [*map(int, self.input), *range(10, list_size + 1)]
        cups: Dict[int, Node] = {}
        assert list_size == len(sequence)

        for i in sequence:
            cups[i] = Node(i)

        for index, value in enumerate(sequence):
            cups[value].next = cups[sequence[(index + 1) % list_size]]

        current = cups[sequence[0]]

        for _ in range(num_loops):
            pickup_head = current.next
            # "remove" 3 elements
            current.next = current.next.next.next.next

            val = current.val
            while val in [
                current.val,
                pickup_head.val,
                pickup_head.next.val,
                pickup_head.next.next.val,
            ]:
                val = list_size if val == 1 else val - 1

            # swap
            target = cups[val]
            pickup_head.next.next.next = target.next
            target.next = pickup_head

            current = current.next

        answer = cups[1].next.val * cups[1].next.next.val
        assert answer == 418_819_514_477
        return answer
