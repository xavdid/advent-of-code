#!/usr/bin/env python3

import argparse
import cProfile
import sys
from importlib import import_module
from pathlib import Path
from time import perf_counter_ns
from typing import Type, cast

from misc.date_utils import current_puzzle_year, next_day
from solutions.base import AoCException, BaseSolution

__version__ = "4.0.3"

PARSER = argparse.ArgumentParser(
    description="Run a specific day of Advent of Code", prog="advent"
)
PARSER.add_argument("--version", action="version", version=__version__)
PARSER.add_argument(
    "day",
    nargs="?",
    type=int,  # so that padding works correctly in `main`
    help=(
        "Which puzzle day to run, between [1,25]. Defaults to the latest day in the specified year (defaulting to this year)."
    ),
)
PARSER.add_argument("--year", default=current_puzzle_year(), help="which year to use f")
PARSER.add_argument(
    "-t",
    "--test-data",
    action="store_true",
    help="run using test_input.txt instead of the day's actual input.",
)
PARSER.add_argument(
    "--debug", action="store_true", help="prints normally-hidden debugging statements"
)
PARSER.add_argument(
    "--profile", action="store_true", help="run solution through a performance profiler"
)
PARSER.add_argument(
    "--slow",
    action="store_true",
    help="specify that long-running solutions (or those requiring manual input) should be run",
)
PARSER.add_argument(
    "--time",
    action="store_true",
    help="Print information about how long the solution (both parts) took to run",
)


def main(
    day: int | None, year: str, slow: bool, debug: bool, test_data: bool, time_it: bool
):
    try:
        # class needs to have this name
        if day is None:
            year_dir = Path(f"solutions/{year}")
            day = next_day(year_dir)
        else:
            if not 1 <= day <= 25:
                PARSER.error(f"day {day} is not in range [1,25]")

        solution_class = cast(
            Type[BaseSolution],
            import_module(f"solutions.{year}.day_{day:02}.solution").Solution,
        )
    except ModuleNotFoundError:
        print(
            f"solution not found for day {day} ({year}) (or there's an ImportError in your code)"
        )
        sys.exit(1)

    try:
        solution = solution_class(
            run_slow=slow, is_debugging=debug, use_test_data=test_data
        )

        start = perf_counter_ns()
        solution.run_and_print_solutions()
        stop = perf_counter_ns()
    except AoCException as e:
        print("ERR:", e)
        sys.exit(1)

    if time_it:
        print("== Performance")
        print(f"=== Both parts ran in {round((stop - start) / 1_000_000_000, 3)}s\n")


if __name__ == "__main__":
    ARGS = PARSER.parse_args()

    if ARGS.profile:
        cProfile.run(
            "main(ARGS.day, ARGS.year, ARGS.slow, ARGS.debug, ARGS.test_data, False)",
            sort="tottime",
        )
    else:
        main(ARGS.day, ARGS.year, ARGS.slow, ARGS.debug, ARGS.test_data, ARGS.time)
