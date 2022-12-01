import re
from datetime import date
from pathlib import Path


def current_puzzle_year() -> str:
    """
    if it's on or after nov 30, use this year. Otherwise, use last year.

    Returns a string because math is never done on the result
    """

    now = date.today()
    if now.month == 12 or (now.month == 11 and now.day == 30):
        return str(now.year)
    return str(now.year - 1)


def next_day(year_dir: Path) -> int:
    """
    Finds the day of the last completed puzzle in a given folder.

    Returns 0 by default. Uses int because we add 1 later.
    """
    return max(
        [
            0,  # included so that new years don't break without anything in them
            *[
                int(x.parts[-1].split("_")[1])
                for x in year_dir.iterdir()
                if x.is_dir() and re.search(r"day_\d+$", str(x))
            ],
        ]
    )
