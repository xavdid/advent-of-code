"""
A script to rename directories for days 1-9 each year to include a padded 0.
This ensures they'll sort as expected in all lists, especially on GitHub.
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path.resolve(Path(__file__, "..", ".."))
WRITEUPS_ROOT = Path(REPO_ROOT, "blog", "src", "content", "writeups")


def move_readmes():
    total = 0
    for file_or_folder in Path.resolve(Path(REPO_ROOT, "solutions")).iterdir():
        if not (file_or_folder.is_dir() and file_or_folder.name.isdigit()):
            continue

        for day_folder in file_or_folder.iterdir():
            to_move = []
            if (writeup := Path(day_folder / "README.md")).exists():
                to_move.append(str(writeup.relative_to(REPO_ROOT)))

            if (images := Path(day_folder / "images")).exists():
                to_move.append(str(images.relative_to(REPO_ROOT)))

            if to_move:
                destination_path = Path(
                    WRITEUPS_ROOT,
                    file_or_folder.name,
                    # strip leading 0 from single-digit folders, since we don't care about ordering on GH now
                    str(int(day_folder.name.split("_")[1])),
                )
                destination_path.mkdir(exist_ok=True)
                result = subprocess.run(
                    [
                        "git",
                        "mv",
                        *to_move,
                        str(destination_path.relative_to(REPO_ROOT)),
                    ],
                    capture_output=True, check=False,
                )
                if result.returncode:
                    print(f"failed to move {to_move}: ", result.stderr)

    print(f"updated {total} folders")


# if I were clever, I would have done this as part of the move
def leave_breadcrumbs():
    for year in WRITEUPS_ROOT.iterdir():
        if not year.is_dir():
            continue
        for day in year.iterdir():
            if not day.is_dir():
                continue
            readme_path = Path(day / "README.md")
            if readme_path.exists():
                breadcrumb = Path(
                    REPO_ROOT,
                    "solutions",
                    year.name,
                    f"day_{int(day.name):02}",
                    "README.md",
                )
                print(breadcrumb)
                if not breadcrumb.exists():
                    breadcrumb.write_text(
                        "\n\n".join(
                            [
                                f"# Day {day.name} ({year.name})",
                                f"This writeup has been moved my standalone AoC site: https://advent-of-code.xavd.id/writeups/{year.name}/day/{day.name}",
                                "",
                            ]
                        )
                    )

            else:
                print("empty folder??")


def add_frontmatter_to_writeups():
    for year in WRITEUPS_ROOT.iterdir():
        if not year.is_dir():
            continue
        for day in year.iterdir():
            if not day.is_dir():
                continue
            readme_path = Path(day / "README.md")
            readme_content = readme_path.read_text()
            if readme_content.startswith("---"):
                continue
            parts = readme_content.split("## Part 1", maxsplit=1)

            if not (title := re.search(r"`(.*)`", parts[0])):
                print("malformed README?", day)
                continue

            frontmatter = "\n".join(
                [
                    "---",
                    f"year: {int(year.name)}",
                    f"day: {int(day.name)}",
                    f'title: "{title.group(1)}"',
                    f'slug: "{int(year.name)}/day/{int(day.name)}"',
                    "---",
                    "",
                    "## Part 1",
                ]
            )

            result = "".join([frontmatter, parts[1]])

            readme_path.write_text(result)


if __name__ == "__main__":
    add_frontmatter_to_writeups()
