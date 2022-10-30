# prompt: https://adventofcode.com/2020/day/4

import re
from typing import Dict, Tuple

from ...base import BaseSolution


def flatten_passport(passport: str) -> Dict[str, str]:
    return dict([s.split(":") for s in re.split(r" |\n", passport)])


# this one can't quite fit in a lambda
def valid_height(x: str) -> bool:
    match = re.match(r"(\d{2,3})(cm|in)$", x)
    if not match:
        return False

    size, unit = match.groups()
    if unit == "cm":
        return 150 <= int(size) <= 193

    return 59 <= int(size) <= 76


VALIDATORS = {
    "byr": lambda x: len(x) == 4 and 1920 <= int(x) <= 2002,
    "iyr": lambda x: len(x) == 4 and 2010 <= int(x) <= 2020,
    "eyr": lambda x: len(x) == 4 and 2020 <= int(x) <= 2030,
    "hgt": valid_height,
    "hcl": lambda x: bool(re.match(r"#[0-9a-f]{6}", x)),
    "ecl": lambda x: x in {"amb", "blu", "brn", "gry", "grn", "hzl", "oth"},
    "pid": lambda x: len(x) == 9 and int(x),
    "cid": lambda x: True,  # ignored
}


def passport_has_valid_keys(passport: Dict[str, str]) -> bool:
    if len(passport) == 8:
        return True
    if len(passport) == 7 and "cid" not in passport:
        return True
    return False


def passport_has_valid_values(passport: Dict[str, str]) -> bool:
    for k, v in passport.items():
        if not VALIDATORS[k](v):
            # print(f"invalid {k}: {v}")
            # break early on failure
            return False
    return True


class Solution(BaseSolution):
    _year = 2020
    _day = 4

    def solve(self) -> Tuple[int, int]:
        num_with_correct_key_count = 0  # part 1
        num_valid_values = 0  # part 2

        passports = self.input.split("\n\n")
        for passport in passports:
            cleaned = flatten_passport(passport)
            if not passport_has_valid_keys(cleaned):
                # no need to check further validity
                continue

            num_with_correct_key_count += 1

            if passport_has_valid_values(cleaned):
                num_valid_values += 1

        return num_with_correct_key_count, num_valid_values
