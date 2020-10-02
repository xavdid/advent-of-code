# prompt: https://adventofcode.com/2019/day/15

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List

from .day_2 import IntcodeComputer, IntcodeSolution


class Direction(IntEnum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


# pylint: disable=invalid-name
@dataclass(frozen=True, eq=True)
class Point:
    x: int
    y: int

    def point_in_direction(self, direction: Direction) -> "Point":
        if direction == Direction.NORTH:
            return Point(self.x, self.y + 1)
        if direction == Direction.SOUTH:
            return Point(self.x, self.y - 1)
        if direction == Direction.WEST:
            return Point(self.x - 1, self.y)
        if direction == Direction.EAST:
            return Point(self.x + 1, self.y)

        raise ValueError("not a direction")


HOME = Point(0, 0)


class Exa:
    """
    EXAPUNKS
    """

    visited = {
        HOME,
        HOME.point_in_direction(Direction.NORTH),
        HOME.point_in_direction(Direction.EAST),
        HOME.point_in_direction(Direction.SOUTH),
        HOME.point_in_direction(Direction.WEST),
    }
    next_id = 1

    def __init__(
        self,
        program: List[int],
        direction: Direction,
        trail: List[Point],
        computer: IntcodeComputer = None,
    ) -> None:
        self.id = Exa.next_id
        Exa.next_id += 1
        self.direction = direction
        if computer:
            self.computer = computer.copy()
            self.computer.add_input(self.direction)
        else:
            self.computer = IntcodeComputer(program[:], [self.direction])
        self.trail = trail[:]

    def pretty(self):
        return str(self)

    def __str__(self) -> str:
        return f"id:{self.id} - dir:{Direction(self.direction).name} - pos:{self.trail[-1]}"

    def step(self) -> int:
        self.computer.run(num_outputs=1)
        result = self.computer.output[-1]

        # it's ok if we append to the trail even if we're standing on a wall
        # because that exa won't be replicated
        self.trail.append(self.trail[-1].point_in_direction(self.direction))

        return result

    @property
    def last_position(self):
        return self.trail[-1]

    def fork(self, direction: Direction) -> "Exa":
        return Exa([], direction, self.trail, computer=self.computer)


class Maze:
    def __init__(self) -> None:
        self.maze: Dict[Point, str] = {HOME: "H"}

    def add_point(self, point: Point, value: int):
        if point in self.maze:
            raise ValueError("repeat maze point")
        self.maze[point] = value

    def char(self, c):
        return {0: "x", 1: ".", 2: "W", "H": "H"}.get(c, " ")

    def __str__(self) -> str:
        rows = []
        # have to get maze corners
        min_x = min(p.x for p in self.maze)
        max_x = max(p.x for p in self.maze)
        min_y = min(p.y for p in self.maze)
        max_y = max(p.y for p in self.maze)

        for y in range(max_y, min_y - 1, -1):
            row = []
            for x in range(min_x, max_x + 1):
                row.append(self.char(self.maze.get(Point(x, y), "default")))
            rows.append(row)

        return "\n".join(["".join([char for char in row]) for row in rows])


class Solution(IntcodeSolution):
    year = 2019
    number = 15

    def part_1(self):
        # 4 initial directions
        to_check: List[Exa] = [
            Exa(self.input, Direction.NORTH, [HOME]),
            Exa(self.input, Direction.EAST, [HOME]),
            Exa(self.input, Direction.SOUTH, [HOME]),
            Exa(self.input, Direction.WEST, [HOME]),
        ]
        maze = Maze()

        while to_check:
            exa = to_check.pop(0)
            self.pp(f"checking: {exa}")
            result = exa.step()
            self.pp(f"got {result} | (now at {exa.trail[-1]})")
            maze.add_point(exa.last_position, result)
            if result == 0:
                self.pp(f"kill {exa.id}")
                self.newline()
                continue
            if result == 1:
                for direction in Direction:
                    next_point = exa.last_position.point_in_direction(direction)
                    if next_point not in Exa.visited:
                        Exa.visited.add(next_point)
                        new_exa = exa.fork(direction)
                        to_check.append(new_exa)
                        self.pp(f"queueing {new_exa}")
                self.pp(f"there are {len(to_check)} EXAs remaining", newline=True)
            if result == 2:
                self.pp(str(maze))
                return len(exa.trail) - 1  # don't count starting position

        raise Exception("Unable to find the exit")  # should return before we get here

    def part_2(self):
        pass

    def solve(self):
        pass
