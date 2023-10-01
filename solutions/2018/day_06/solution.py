# prompt: https://adventofcode.com/2018/day/6

from collections import defaultdict

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    _year = 2018
    _day = 6

    @property
    def input_type(self):
        return InputTypes.STRSPLIT

    def __init__(self, run_slow=False):
        super().__init__(run_slow)
        # don't remember why I needed to subclass this. mayb eso it only happened once?
        self.build_grid()

    # takes two points, (x, y)
    def distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def is_border(self, p):
        return (
            p[0] == self.min_x
            or p[0] == self.max_x
            or p[1] == self.min_y
            or p[1] == self.max_y
        )

    def build_grid(self):
        self.input_points = []
        for line in self.input:
            x, y = line.split(", ")
            self.input_points.append((int(x), int(y)))

        self.min_x = min(i[0] for i in self.input_points)
        self.max_x = max(i[0] for i in self.input_points)
        self.min_y = min(i[1] for i in self.input_points)
        self.max_y = max(i[1] for i in self.input_points)

    def traverse_grid(self):
        for i in range(self.min_x, self.min_x + self.max_x):
            for j in range(self.min_y, self.min_y + self.max_y):
                yield (i, j)

    def part_1(self):
        city = defaultdict(set)
        border_ids = set()

        for p in self.traverse_grid():

            # could speed this up by not recalculating every distance every time
            # it's neighbor + 1, if we've got spacial awareness

            # [(distance, id)]
            local_distances = [
                (self.distance(input_point, p), owner)
                for owner, input_point in enumerate(self.input_points)
            ]
            local_distances.sort()

            if local_distances[0][0] == local_distances[1][0]:
                # tie! no winner
                continue

            owner = local_distances[0][1]
            # if a point is on a border, it's not finite
            if owner in border_ids:
                continue

            if self.is_border(p):
                border_ids.add(owner)
                continue

            city[owner].add(p)

        return len(max(city.values(), key=len))

    def part_2(self):
        close_enough = set()
        for p in self.traverse_grid():
            if sum([self.distance(p, ip) for ip in self.input_points]) < 10000:
                close_enough.add(p)

        return len(close_enough)
