import re
from datetime import date
from pathlib import Path


def current_puzzle_year() -> int:
    # if it's on or after dec 1, use this year. Otherwise, use last year
    now = date.today()
    if now.month == 12:
        return str(now.year)
    return str(now.year - 1)


def next_day(year_dir: Path) -> int:
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
