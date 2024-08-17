# prompt: https://adventofcode.com/2020/day/12

from typing import List

from ...base import BaseSolution, InputTypes

# from typing import Tuple

COMPASS = ["N", "E", "S", "W"]

DIRECTIONS = {*COMPASS, "F"}


class Ship:
    def __init__(self, waypoint=False) -> None:
        self.x = 0
        self.y = 0
        # index in the compass
        self.facing = 1

        self.waypoint = waypoint
        self.waypoint_x = 10
        self.waypoint_y = 1

    def distance(self) -> int:
        return abs(self.x) + abs(self.y)

    def execute(self, instructions: List[str]):
        for instruction in instructions:
            move_type = instruction[0]
            value = int(instruction[1:])
            if move_type in DIRECTIONS:
                self.move(move_type, value)
            else:
                self.rotate(move_type, value)

    def move(self, direction: str, distance: int):
        if self.waypoint:
            if direction == "F":
                self.x += distance * self.waypoint_x
                self.y += distance * self.waypoint_y
            elif direction == "N":
                self.waypoint_y += distance
            elif direction == "S":
                self.waypoint_y -= distance
            elif direction == "E":
                self.waypoint_x += distance
            elif direction == "W":
                self.waypoint_x -= distance
        else:
            if direction == "F":
                direction = COMPASS[self.facing]

            if direction == "N":
                self.y += distance
            elif direction == "S":
                self.y -= distance
            elif direction == "E":
                self.x += distance
            elif direction == "W":
                self.x -= distance

    def rotate(self, direction: str, degrees: int):
        num_steps = degrees // 90
        if self.waypoint:
            for _ in range(num_steps):
                temp = self.waypoint_y
                self.waypoint_y = self.waypoint_x
                self.waypoint_x = temp
                # when turning L, the new X swaps sign
                # opposite is true for R
                if direction == "L":
                    self.waypoint_x *= -1
                else:
                    self.waypoint_y *= -1

        else:
            if direction == "L":
                num_steps *= -1

            self.facing = (self.facing + num_steps) % len(COMPASS)


class Solution(BaseSolution):
    _year = 2020
    _day = 12
    input_type = InputTypes.STRSPLIT

    def part_1(self) -> int:
        ship = Ship()
        ship.execute(self.input)
        return ship.distance()

    def part_2(self) -> int:
        ship = Ship(waypoint=True)
        ship.execute(self.input)
        return ship.distance()
