# prompt: https://adventofcode.com/2022/day/7


from typing import Dict, List, Tuple

from ...base import StrSplitSolution, answer


class Solution(StrSplitSolution):
    _year = 2022
    _day = 7

    directory_sizes: List[int] = []

    def parse_filesystem(self):
        filesystem = {"/": {}}
        current_path = []

        def get_dir() -> Dict:
            res = filesystem
            for segment in current_path:
                res = res[segment]
            return res

        current_dir = get_dir()

        for line in self.input:
            match line.split():
                case ["$", "ls"]:
                    continue
                case ["$", "cd", "/"]:
                    current_path = ["/"]
                    current_dir = filesystem["/"]
                case ["$", "cd", ".."]:
                    current_path.pop()
                    current_dir = get_dir()
                case ["$", "cd", new_dir]:
                    current_path.append(new_dir)
                    current_dir = get_dir()
                case ["dir", dir_name]:
                    current_dir[dir_name] = {}
                case [size, file_name]:
                    current_dir[file_name] = int(size)
                case _:
                    raise ValueError("unknown line shape")

        return filesystem

    def calculate_directory_sizes(self, directory: Dict) -> int:
        total = 0
        for size_or_dir in directory.values():
            if isinstance(size_or_dir, int):
                total += size_or_dir
            else:
                subtotal = self.calculate_directory_sizes(size_or_dir)
                self.directory_sizes.append(subtotal)
                total += subtotal

        return total

    def calculate_unused_space(self) -> int:
        TOTAL_SPACE = 70_000_000
        SPACE_REQUIRED = 30_000_000

        unused_space = TOTAL_SPACE - self.directory_sizes[-1]  # the root directory
        return SPACE_REQUIRED - unused_space

    @answer((1391690, 5469168))
    def solve(self) -> Tuple[int, int]:
        filesystem = self.parse_filesystem()
        self.debug(filesystem)

        self.calculate_directory_sizes(filesystem)

        # part 1
        small_directories_total = sum([v for v in self.directory_sizes if v <= 100_000])

        # part 2
        min_size = self.calculate_unused_space()
        smallest_directory_to_clear = min(
            [v for v in self.directory_sizes if v >= min_size]
        )

        return small_directories_total, smallest_directory_to_clear
