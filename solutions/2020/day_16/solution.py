# prompt: https://adventofcode.com/2020/day/16

from typing import Set, Tuple

from ...base import BaseSolution


class Solution(BaseSolution):
    year = 2020
    number = 16
    validators = {}
    # input_type = InputTypes.

    def parse_requirements(self) -> None:
        requirements_block = self.input.split("\n\n")[0]
        for line in requirements_block.split("\n"):
            field, function_blueprint = line.split(": ")
            ranges = []
            for f in function_blueprint.split(" or "):
                low, hi = f.split("-")
                # the last number isn't included in the range
                # our input is inclusive, so we have to inc the top by 1
                ranges.append(range(int(low), int(hi) + 1))

            self.validators[field] = ranges

    def is_valid_value(self, value: int) -> bool:
        """
        returns `True` if the value passes any validator
        """
        for validators in self.validators.values():
            for r in validators:
                if value in r:
                    return True
        return False

    def is_valid_ticket(self, ticket: str) -> bool:
        return all([self.is_valid_value(int(v)) for v in ticket.split(",")])

    def possible_fields_for_value(self, value: int) -> Set[str]:
        return {
            field
            for field, validators in self.validators.items()
            if any([value in r for r in validators])
        }

    def part_1(self) -> int:
        self.parse_requirements()
        nearby_tickets_block = self.input.split("\n\n")[2]
        total = 0
        for line in nearby_tickets_block.split("\n")[1:]:
            for v in line.split(","):
                if not self.is_valid_value(int(v)):
                    total += int(v)

        return total

    def part_2(self) -> int:
        self.parse_requirements()
        tickets = self.input.split("\n\n")[2].split("\n")[1:]
        valid_tickets = [
            list(map(int, t.split(","))) for t in tickets if self.is_valid_ticket(t)
        ]

        answer = {}

        for ticket in valid_tickets:
            for index, value in enumerate(ticket):
                possible_fields = self.possible_fields_for_value(value)
                if len(possible_fields) == 1:
                    answer[index] = possible_fields.pop()
                    print(f"value {index} is {answer[index]}")

        # any uniquely identified fields have now been found

    def solve(self) -> Tuple[int, int]:
        self.parse_requirements()

        nearby_tickets_block = self.input.split("\n\n")[2]
        total = 0
        valid_tickets = []
        for line in nearby_tickets_block.split("\n")[1:]:
            ticket = list(map(int, line.split(",")))
            valid = True
            for v in ticket:
                if not self.is_valid_value(v):
                    valid = False
                    total += int(v)

            if valid:
                valid_tickets.append(ticket)

        # --- part 2
        answer = {}
        for ticket in valid_tickets:
            for index, value in enumerate(ticket):
                possible_fields = self.possible_fields_for_value(value)
                if len(possible_fields) == 1:
                    answer[index] = possible_fields.pop()
                    print(f"value {index} is {answer[index]}")

        return total, len(valid_tickets)
