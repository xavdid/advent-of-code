# prompt: https://adventofcode.com/2022/day/22

import re
from dataclasses import dataclass, field
from math import sqrt
from pprint import pprint
from typing import Literal

from ...base import GridPoint, TextSolution, answer

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


@dataclass
class CubeFace:
    # (row, col) in the 2D map
    map_loc: tuple[int, int]
    # portion of the grid belonging to this cube face
    subgrid: list[list[str]]
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

    def __repr__(self) -> str:
        return str(self.map_loc)

    def absolute_loc(self, face_size: int):
        return self.map_loc[0] * face_size + 1, self.map_loc[1] * face_size + 1


FlatCube = dict[int, dict[int, int | None]]


def parse_input(raw_input: str):
    raw_grid, path = raw_input.split("\n\n")
    cube_size = int(sqrt((raw_grid.count(".") + raw_grid.count("#")) / 6))

    grid = raw_grid.split("\n")
    longest_line_lenth = max(len(l) for l in grid) // cube_size

    faces: list[CubeFace] = []
    flat_cube: FlatCube = {}

    for row in range(len(grid) // cube_size):
        flat_cube[row] = {}
        for col in range(longest_line_lenth):
            try:
                c = grid[row * cube_size][col * cube_size]
            except IndexError:
                flat_cube[row][col] = None
            else:
                if c != " ":
                    subgrid = [
                        list(line[col * cube_size : (col + 1) * cube_size])
                        for line in grid[row * cube_size : (row + 1) * cube_size]
                    ]

                    flat_cube[row][col] = len(faces)
                    faces.append(CubeFace((row, col), subgrid))
                else:
                    flat_cube[row][col] = None

    pprint(
        {
            "faces": faces,
            "flat_cube": flat_cube,
            "size": cube_size,
            "instructions": parse_path(path),
        }
    )

    return faces, flat_cube, cube_size, parse_path(path)


def calculate_face_connectivity(faces: list[CubeFace], flat_cube: FlatCube):
    # orient the cube around the first side being "top"
    print("initial position\n  no checks")
    faces[0].cube_position = "top"
    populate_neighbors(faces[0], "east", "right")

    closed = set()

    def walk(face_index: int):
        closed.add(face_index)

        face = faces[face_index]
        print("\nexploring", face)
        row, col = face.map_loc

        map_neighbor_indexes: dict[MAP_DIRECTIONS, int | None] = {
            "east": flat_cube.get(row, {}).get(col + 1),
            "south": flat_cube.get(row + 1, {}).get(col),
            "west": flat_cube.get(row, {}).get(col - 1),
            "north": flat_cube.get(row - 1, {}).get(col),
        }

        for dir_index, map_direction in enumerate(MAP_DIRECTIONS_CLOCKWISE):
            print(f"  checking {map_direction}")
            if (
                neighbor_index := map_neighbor_indexes[map_direction]
            ) and neighbor_index not in closed:
                print(f"    found map tile at index {neighbor_index}")

                faces[neighbor_index].cube_position = face.neighbors[map_direction]

                print(
                    f"    set {faces[neighbor_index]}'s cube position to the {map_direction} of {face}, making it the {face.neighbors[map_direction]} cube face"
                )

                populate_neighbors(
                    faces[neighbor_index],
                    # opposite direction
                    MAP_DIRECTIONS_CLOCKWISE[(dir_index + 2) % 4],
                    face.cube_position,
                )
                walk(neighbor_index)
        print("returning")

    walk(0)


def populate_neighbors(
    face: CubeFace, map_direction: MAP_DIRECTIONS, cube_face: CUBE_FACES
):
    """
    given a CubeFace, populate its `neighbors` clockwise, starting with the fact that its `map_direction` is the cube's `cube_face`
    """
    direction_index = MAP_DIRECTIONS_CLOCKWISE.index(map_direction)

    face_index = CUBE_FACES_CLOCKWISE[face.cube_position].index(cube_face)

    print(
        f"    populating neighbors for {face} starting with {map_direction} ({direction_index}) -> {cube_face} ({face_index})"
    )

    for i in range(4):
        map_direction = MAP_DIRECTIONS_CLOCKWISE[(direction_index + i) % 4]
        cube_face_direction = CUBE_FACES_CLOCKWISE[face.cube_position][
            (face_index + i) % 4
        ]
        face.neighbors[map_direction] = cube_face_direction

    print("      wrote", face.neighbors)


def parse_grid(raw_grid: str) -> tuple[dict[GridPoint, bool], int, int]:
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


def parse_path(s: str) -> list[Literal["L", "R"] | int]:
    return [int(c) if c.isdigit() else c for c in re.findall(r"\d+|\w", s)]


def add(loc: GridPoint, offset: GridPoint) -> GridPoint:
    return loc[0] + offset[0], loc[1] + offset[1]


OFFSETS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


class SparseGrid:
    offset_index = 0

    def __init__(self, raw_input: str) -> None:
        grid, path = raw_input.split("\n\n")

        self.grid, self.max_rows, self.max_cols = self.parse_grid(grid)
        self.path = self.parse_path(path)

        self.location: GridPoint = 0, raw_input.find(".")

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

    def parse_path(self, s: str) -> list[Literal["L", "R"] | int]:
        return [int(c) if c.isdigit() else c for c in re.findall(r"\d+|\w", s)]

    @property
    def offset(self) -> GridPoint:
        return OFFSETS[self.offset_index]

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

    def rotate(self, direction: Literal["L", "R"]):
        x = -1 if direction == "L" else 1
        self.offset_index = (self.offset_index + x) % 4

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


# class CubeGrid(SparseGrid):
#     pass


class Solution(TextSolution):
    _year = 2022
    _day = 22

    @answer(66292)
    def part_1(self) -> int:
        return SparseGrid(self.input).run()

    @answer(127012)
    def part_2(self) -> int:
        faces, face_map, cube_face_size, instructions = parse_input(self.input)
        calculate_face_connectivity(faces, face_map)

        print("\n--------------")
        face_index = 0
        row = 0
        col = 0
        direction: MAP_DIRECTIONS = "east"

        for instruction in instructions:
            print(f"\ntop! at {row=} {col=} facing {direction=}; {face_index=}")
            if instruction == "L":
                print("  rotated L")
                direction = MAP_DIRECTIONS_CLOCKWISE[
                    (MAP_DIRECTIONS_CLOCKWISE.index(direction) - 1) % 4
                ]
                continue
            if instruction == "R":
                print("  rotated R")
                direction = MAP_DIRECTIONS_CLOCKWISE[
                    (MAP_DIRECTIONS_CLOCKWISE.index(direction) + 1) % 4
                ]
                continue

            for i in range(instruction):
                print(
                    f"  walking {direction} on {face_index} (step {i+1}/{instruction})"
                )
                row_offset, col_offset = {
                    "east": [0, 1],
                    "south": [1, 0],
                    "west": [0, -1],
                    "north": [-1, -0],
                }[direction]

                new_row = row + row_offset
                new_col = col + col_offset

                new_face_index = face_index
                new_direction = direction

                print(f"    now at ({new_row}, {new_col})")

                if not (
                    0 <= new_col < cube_face_size and 0 <= new_row < cube_face_size
                ):
                    print("    out of bounds, wrapping;")
                    new_row %= cube_face_size
                    new_col %= cube_face_size
                    print(f"      new pos: ({new_row}, {new_col})")

                    new_face_index = next(
                        idx
                        for idx, face in enumerate(faces)
                        if face.cube_position == faces[face_index].neighbors[direction]
                    )
                    print(
                        f"      now on face_index {new_face_index} because the {direction} of {faces[face_index].cube_position} is {faces[new_face_index].cube_position}"
                    )

                    new_dir_index = MAP_DIRECTIONS_CLOCKWISE.index(direction)

                    # loop until the direction behind us is the face we came from
                    print(
                        f"      looping until {faces[new_face_index].neighbors[ MAP_DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4] ]} matches {faces[face_index].cube_position}"
                    )
                    while (
                        faces[new_face_index].neighbors[
                            MAP_DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4]
                        ]
                        != faces[face_index].cube_position
                    ):
                        # this is the linear algebra magic, which handles rotating a face and updating position correctly
                        new_col, new_row = cube_face_size - 1 - new_row, new_col
                        new_dir_index = (new_dir_index + 1) % 4
                        print(
                            f"        updated position to ({new_row}, {new_col}) facing {MAP_DIRECTIONS_CLOCKWISE[new_dir_index]}"
                        )
                        print(
                            f"        - loop condition: {faces[new_face_index].neighbors[ MAP_DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4] ]} <> {faces[face_index].cube_position}"
                        )
                    new_direction = MAP_DIRECTIONS_CLOCKWISE[new_dir_index]

                if faces[new_face_index].subgrid[new_row][new_col] == "#":
                    print("    wall")
                    break

                face_index = new_face_index
                row = new_row
                col = new_col
                direction = new_direction

        # TODO: improve
        i, j = faces[face_index].absolute_loc(cube_face_size)

        return (
            1000 * (i + row) + 4 * (j + col) + MAP_DIRECTIONS_CLOCKWISE.index(direction)
        )
