# prompt: https://adventofcode.com/2020/day/16

from math import prod
from typing import List, Sequence, Set, Tuple

from ...base import BaseSolution


class Solution(BaseSolution):
    year = 2020
    number = 16
    validators = {}

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

    def possible_columns_for_values(self, value_set) -> List[str]:
        return [
            field_name
            for field_name, validators in self.validators.items()
            if self.all_values_pass_validators(value_set, validators)
        ]

    # pylint: disable=no-self-use
    def all_values_pass_validators(
        self, value_set, validators: List[Sequence[int]]
    ) -> bool:
        return all([any(v in validator for validator in validators) for v in value_set])

    # pylint: disable=too-many-locals
    def solve(self) -> Tuple[int, int]:
        self.parse_requirements()

        nearby_tickets_block = self.input.split("\n\n")[2]
        total_invalid_value = 0
        valid_tickets: List[List[int]] = []
        for line in nearby_tickets_block.split("\n")[1:]:
            ticket = list(map(int, line.split(",")))
            valid = True
            for v in ticket:
                if not self.is_valid_value(v):
                    valid = False
                    total_invalid_value += v

            if valid:
                valid_tickets.append(ticket)

        # --- part 2

        value_sets: List[Set[int]] = [
            {ticket[column] for ticket in valid_tickets}
            for column in range(len(self.validators))
        ]

        column_names = {}
        while self.validators:
            self.pp(f"Top of loop, {len(self.validators)} unknown fields remain")
            for index, value_set in enumerate(value_sets):
                possible_columns = self.possible_columns_for_values(value_set)
                if len(possible_columns) == 1:
                    field_name = possible_columns[0]
                    column_names[field_name] = index
                    self.pp(f'field "{field_name}" identified at column {index}')
                    self.validators.pop(field_name)

        my_ticket = list(
            map(int, self.input.split("\n\n")[1].split("\n")[1].split(","))
        )

        departure_info = prod(
            [
                my_ticket[field_index]
                for field_name, field_index in column_names.items()
                if field_name.startswith("departure")
            ]
        )

        return total_invalid_value, departure_info
