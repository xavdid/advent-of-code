"""
A script to rename directories for days 1-9 each year to include a padded 0.
This ensures they'll sort as expected in all lists, especially on GitHub.
"""
import subprocess
from pathlib import Path

SCRIPT_LOCATION = __file__


def main():
    result = subprocess.run(
        ["ls", Path.resolve(Path(__file__, "..", "solutions"))], check=True
    )
    print(result.stdout)


if __name__ == "__main__":
    main()
