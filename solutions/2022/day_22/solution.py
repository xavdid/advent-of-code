# prompt: https://adventofcode.com/2022/day/22

import re
from dataclasses import dataclass, field
from math import sqrt
from typing import Literal

from ...base import TextSolution, answer
from ...utils.graphs import GridPoint

OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

MAP_DIRECTIONS = Literal["east", "south", "west", "north"]
MAP_DIRECTIONS_CLOCKWISE = ("east", "south", "west", "north")

CUBE_FACES = Literal["top", "bottom", "left", "right", "front", "back"]
CUBE_FACES_CLOCKWISE: dict[CUBE_FACES, list[CUBE_FACES]] = {
    "top": ["right", "front", "left", "back"],
    "right": ["top", "back", "bottom", "front"],
    "front": ["top", "right", "bottom", "left"],
}
CUBE_FACES_CLOCKWISE["bottom"] = list(reversed(CUBE_FACES_CLOCKWISE["top"]))
CUBE_FACES_CLOCKWISE["left"] = list(reversed(CUBE_FACES_CLOCKWISE["right"]))
CUBE_FACES_CLOCKWISE["back"] = list(reversed(CUBE_FACES_CLOCKWISE["front"]))


def add(loc: GridPoint, offset: GridPoint) -> GridPoint:
    return loc[0] + offset[0], loc[1] + offset[1]


def parse_path(s: str) -> list[Literal["L", "R"] | int]:
    return [int(c) if c.isdigit() else c for c in re.findall(r"\d+|\w", s)]


class BaseGrid:
    offset_index = 0

    def __init__(self, raw_input: str) -> None:
        raw_grid, path = raw_input.split("\n\n")
        self.location = 0, 0
        self.path = parse_path(path)
        self._post_init(raw_grid)

    def _post_init(self, raw_grid: str):
        """
        expected to do any setup and instance variable assignments
        """
        raise NotImplementedError

    @property
    def offset(self) -> GridPoint:
        return OFFSETS[self.offset_index]

    def rotate(self, direction: Literal["L", "R"]):
        x = -1 if direction == "L" else 1
        self.offset_index = (self.offset_index + x) % 4


class SparseGrid(BaseGrid):
    def _post_init(self, raw_grid: str):
        self.grid, self.max_rows, self.max_cols = self.parse_grid(raw_grid)
        self.location: GridPoint = 0, raw_grid.find(".")

    def parse_grid(self, raw_grid: str) -> tuple[dict[GridPoint, bool], int, int]:
        rows = raw_grid.split("\n")
        max_rows = len(rows)
        max_cols = max(len(s) for s in rows)

        grid: dict[GridPoint, bool] = {}

        for row, line in enumerate(rows):
            for col, c in enumerate(line):
                if c == " ":
                    continue
                grid[(row, col)] = c == "."

        return grid, max_rows, max_cols

    def next_valid_loc(self) -> GridPoint:
        next_loc = add(self.location, self.offset)
        while next_loc not in self.grid:
            # change next_loc to be in grid
            if next_loc[0] >= self.max_rows:
                next_loc = -1, next_loc[1]
            elif next_loc[1] >= self.max_cols:
                next_loc = next_loc[0], -1
            elif next_loc[0] < 0:
                next_loc = self.max_rows, next_loc[1]
            elif next_loc[1] < 0:
                next_loc = next_loc[0], self.max_cols

            next_loc = add(next_loc, self.offset)

        return next_loc

    def run(self):
        for instruction in self.path:
            if isinstance(instruction, str):
                self.rotate(instruction)
            else:
                for _ in range(instruction):
                    if self.grid[next_loc := self.next_valid_loc()]:
                        self.location = next_loc
                    else:
                        break

        return (
            1000 * (self.location[0] + 1)
            + 4 * (self.location[1] + 1)
            + self.offset_index
        )


@dataclass
class CubeFace:
    # (row, col) in the 2D map
    map_loc: tuple[int, int]
    # values from the original grid belonging to this cube face
    subgrid: list[list[str]] = field(repr=False)
    # map of the 2D neighbors of this face on the map to its cube side
    # e.g. the first 2D face's southern neighbor is the front of the cube
    neighbors: dict[MAP_DIRECTIONS, CUBE_FACES] = field(default_factory=dict)
    # managed property so we can not define it up front, but it's always defined on use
    _cube_position: CUBE_FACES | None = None

    @property
    def cube_position(self):
        assert self._cube_position
        return self._cube_position

    @cube_position.setter
    def cube_position(self, v: CUBE_FACES):
        self._cube_position = v

    def absolute_loc(self, face_size: int):
        return self.map_loc[0] * face_size + 1, self.map_loc[1] * face_size + 1

    def populate_neighbors(self, map_direction: MAP_DIRECTIONS, cube_face: CUBE_FACES):
        """
        populate `neighbors` clockwise, starting with the fact that
        its `map_direction` is the cube's `cube_face`
        """
        direction_index = MAP_DIRECTIONS_CLOCKWISE.index(map_direction)

        face_index = CUBE_FACES_CLOCKWISE[self.cube_position].index(cube_face)

        for i in range(4):
            map_direction = MAP_DIRECTIONS_CLOCKWISE[(direction_index + i) % 4]
            cube_face_direction = CUBE_FACES_CLOCKWISE[self.cube_position][
                (face_index + i) % 4
            ]
            self.neighbors[map_direction] = cube_face_direction


FlatCube = dict[int, dict[int, int | None]]


class CubeGrid(BaseGrid):
    faces: list[CubeFace]
    flat_cube: FlatCube

    cube_face_size: int

    face_index = 0

    def _post_init(self, raw_grid: str):
        self.cube_face_size = int(sqrt((raw_grid.count(".") + raw_grid.count("#")) / 6))

        self.faces, self.flat_cube = self.parse_cube(raw_grid)
        self.calculate_face_connectivity()

    def parse_cube(self, raw_grid: str) -> tuple[list[CubeFace], FlatCube]:
        grid = raw_grid.split("\n")

        longest_line_length = max(len(l) for l in grid) // self.cube_face_size

        faces: list[CubeFace] = []
        flat_cube: FlatCube = {}

        for row in range(len(grid) // self.cube_face_size):
            flat_cube[row] = {}
            for col in range(longest_line_length):
                try:
                    c = grid[row * self.cube_face_size][col * self.cube_face_size]
                except IndexError:  # noqa: PERF203
                    flat_cube[row][col] = None
                else:
                    if c == " ":
                        flat_cube[row][col] = None
                        continue

                    subgrid = [
                        list(
                            line[
                                col * self.cube_face_size : (col + 1)
                                * self.cube_face_size
                            ]
                        )
                        for line in grid[
                            row * self.cube_face_size : (row + 1) * self.cube_face_size
                        ]
                    ]

                    flat_cube[row][col] = len(faces)
                    faces.append(CubeFace((row, col), subgrid))

        return faces, flat_cube

    def calculate_face_connectivity(self):
        self.faces[0].cube_position = "top"
        self.faces[0].populate_neighbors("east", "right")

        finished = {0}

        def explore(face_index: int):
            face = self.faces[face_index]

            row, col = face.map_loc

            map_neighbor_indexes: dict[MAP_DIRECTIONS, int | None] = {
                "east": self.flat_cube.get(row, {}).get(col + 1),
                "south": self.flat_cube.get(row + 1, {}).get(col),
                "west": self.flat_cube.get(row, {}).get(col - 1),
                "north": self.flat_cube.get(row - 1, {}).get(col),
            }

            for dir_index, map_direction in enumerate(MAP_DIRECTIONS_CLOCKWISE):
                if (
                    (neighbor_index := map_neighbor_indexes[map_direction]) is not None
                ) and neighbor_index not in finished:
                    finished.add(neighbor_index)

                    self.faces[neighbor_index].cube_position = face.neighbors[
                        map_direction
                    ]
                    self.faces[neighbor_index].populate_neighbors(
                        self.opposite_direction(dir_index),
                        face.cube_position,
                    )

                    explore(neighbor_index)

        explore(0)
        assert self.faces[1].neighbors

    def find_next_cube_face(self) -> int:
        for idx, face in enumerate(self.faces):
            if self.face().neighbors[self.current_direction] == face.cube_position:
                return idx

        raise ValueError("failed to find!")

    def next_valid_loc(self) -> tuple[GridPoint, int, int]:
        new_row, new_col = add(self.location, self.offset)

        new_face_index = self.face_index
        new_offset_index = self.offset_index

        if not (
            0 <= new_row < self.cube_face_size and 0 <= new_col < self.cube_face_size
        ):
            new_row %= self.cube_face_size
            new_col %= self.cube_face_size

            new_face_index = self.find_next_cube_face()

            while (
                self.face().cube_position
                != self.faces[new_face_index].neighbors[
                    self.opposite_direction(new_offset_index)
                ]
            ):
                # this is the linear algebra magic,
                # which handles rotating a face and updating position correctly
                new_offset_index = (new_offset_index + 1) % 4
                new_col, new_row = self.cube_face_size - 1 - new_row, new_col

        return (new_row, new_col), new_face_index, new_offset_index

    def face(self, index=None) -> CubeFace:
        if index is None:
            index = self.face_index
        return self.faces[index]

    @property
    def current_direction(self) -> MAP_DIRECTIONS:
        return MAP_DIRECTIONS_CLOCKWISE[self.offset_index]

    def opposite_direction(self, direction_index: int) -> MAP_DIRECTIONS:
        return MAP_DIRECTIONS_CLOCKWISE[(direction_index + 2) % 4]

    def run(self):
        for instruction in self.path:
            if isinstance(instruction, str):
                self.rotate(instruction)
                continue

            for _ in range(instruction):
                (
                    (new_row, new_col),
                    new_face_index,
                    new_offset_index,
                ) = self.next_valid_loc()

                if self.faces[new_face_index].subgrid[new_row][new_col] == "#":
                    break

                self.location = new_row, new_col
                self.face_index = new_face_index
                self.offset_index = new_offset_index

        abs_row, abs_col = add(
            self.location, self.face().absolute_loc(self.cube_face_size)
        )

        return 1000 * abs_row + 4 * abs_col + self.offset_index


class Solution(TextSolution):
    _year = 2022
    _day = 22

    @answer(66292)
    def part_1(self) -> int:
        return SparseGrid(self.input).run()

    @answer(127012)
    def part_2(self) -> int:
        return CubeGrid(self.input).run()
