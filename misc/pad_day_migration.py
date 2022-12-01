"""
A script to rename directories for days 1-9 each year to include a padded 0.
This ensures they'll sort as expected in all lists, especially on GitHub.
"""

from pathlib import Path
import subprocess

REPO_ROOT = Path.resolve(Path(__file__, "..", ".."))


def main():
    total = 0
    for file_or_folder in Path.resolve(Path(REPO_ROOT, "solutions")).iterdir():
        if not file_or_folder.is_dir() or not file_or_folder.name.isdigit():
            continue

        for day in range(1, 10):
            bad_path = Path.resolve(Path(file_or_folder, f"day_{day}"))
            fixed_path = Path.resolve(Path(file_or_folder, f"day_0{day}"))
            if bad_path.exists():
                nice_path = str(bad_path).removeprefix(f"{REPO_ROOT}/solutions/")
                res = subprocess.run(
                    ["git", "mv", bad_path, fixed_path],
                    capture_output=True,
                )
                if res.returncode:
                    print(f"failed to update {nice_path}: {res.stderr}")
                    continue
                else:
                    print("updated", nice_path)
                    total += 1

    print(f"updated {total} folders")


if __name__ == "__main__":
    main()
