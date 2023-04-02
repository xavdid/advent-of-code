# prompt: https://adventofcode.com/2022/day/22


import re
from math import sqrt

# pylint: disable=no-name-in-module
from typing import Literal, NotRequired, TypedDict

from ...base import GridPoint, TextSolution, answer

MAP_DIRECTIONS = Literal["east", "south", "west", "north"]
DIRECTIONS_CLOCKWISE = ("east", "south", "west", "north")

CUBE_FACE_DIRECTIONS = Literal["up", "down", "left", "right", "forward", "back"]
CUBE_FACES_CLOCKWISE: dict[CUBE_FACE_DIRECTIONS, list[CUBE_FACE_DIRECTIONS]] = {
    "up": ["right", "forward", "left", "back"],
    "right": ["up", "back", "down", "forward"],
    "forward": ["up", "right", "down", "left"],
}
CUBE_FACES_CLOCKWISE["down"] = list(reversed(CUBE_FACES_CLOCKWISE["up"]))
CUBE_FACES_CLOCKWISE["left"] = list(reversed(CUBE_FACES_CLOCKWISE["right"]))
CUBE_FACES_CLOCKWISE["back"] = list(reversed(CUBE_FACES_CLOCKWISE["forward"]))

# negative safe modulo operator; not sure if required
def modulo(x: int, m: int):
    mod = x % m
    if mod < 0:
        return mod + m
    return mod


class Face(TypedDict):
    i: int
    j: int
    grid: list[list[str]]
    face: NotRequired[CUBE_FACE_DIRECTIONS]
    neighbors: dict[MAP_DIRECTIONS, CUBE_FACE_DIRECTIONS]


Faces = dict[int, Face]
FaceMap = dict[int, dict[int, int | None]]


def parse_input(raw_input: str):
    raw_grid, path = raw_input.split("\n\n")
    size = int(sqrt((raw_grid.count(".") + raw_grid.count("#")) / 6))
    # print(f"grid is of {size=}")

    grid = raw_grid.split("\n")

    faces: Faces = {}
    face_map: FaceMap = {}

    n = 0

    # print(f"loop from 0 < {len(grid) // size}")
    for i in range(len(grid) // size):
        face_map[i] = {}
        # print(f"inner loop 0 < {(max(len(l) for l in grid) // size)}")
        for j in range((max(len(l) for l in grid) // size)):
            # print(f"reading {i=} {j=}")
            try:
                c = grid[i * size][j * size]
                # print(f"  {c=} at {i*size}][{j*size}")
            except IndexError:
                # print(grid)
                # print(f"failed for {i=} {j=}")
                face_map[i][j] = None
            else:
                if c != " ":
                    face_map[i][j] = n
                    res = [
                        list(line[j * size : (j + 1) * size])
                        for line in grid[i * size : (i + 1) * size]
                    ]
                    faces[n] = {"i": i, "j": j, "grid": res, "neighbors": {}}
                    # pprint(res)
                    n += 1
                else:
                    face_map[i][j] = None

    # ans = {
    #     "faces": faces,
    #     "faceMap": face_map,
    #     "size": size,
    #     "instructions": parse_path(path),
    # }
    # pprint(ans)

    return faces, face_map, size, parse_path(path)


def calculate_face_connectivity(faces: Faces, face_map: FaceMap):
    faces[0]["face"] = "up"
    populate_neighbors(faces[0], "east", "right")

    closed = set()

    def walk(n: int):
        closed.add(n)

        i, j = faces[n]["i"], faces[n]["j"]
        neighbors = {
            "east": face_map.get(i, {}).get(j + 1),
            "south": face_map.get(i + 1, {}).get(j),
            "west": face_map.get(i, {}).get(j - 1),
            "north": face_map.get(i - 1, {}).get(j),
        }
        # print(neighbors)

        if (s := neighbors["east"]) and s not in closed:
            faces[neighbors["east"]]["face"] = faces[n]["neighbors"]["east"]
            assert "face" in faces[n]
            populate_neighbors(faces[neighbors["east"]], "west", faces[n]["face"])
            walk(neighbors["east"])

        if (s := neighbors["south"]) and s not in closed:
            faces[neighbors["south"]]["face"] = faces[n]["neighbors"]["south"]
            assert "face" in faces[n]
            populate_neighbors(faces[neighbors["south"]], "north", faces[n]["face"])
            walk(neighbors["south"])

        if (s := neighbors["west"]) and s not in closed:
            faces[neighbors["west"]]["face"] = faces[n]["neighbors"]["west"]
            assert "face" in faces[n]
            populate_neighbors(faces[neighbors["west"]], "east", faces[n]["face"])
            walk(neighbors["west"])

        if (s := neighbors["north"]) and s not in closed:
            faces[neighbors["north"]]["face"] = faces[n]["neighbors"]["north"]
            assert "face" in faces[n]
            populate_neighbors(faces[neighbors["north"]], "south", faces[n]["face"])
            walk(neighbors["north"])

    walk(0)


def populate_neighbors(
    face: Face, direction: MAP_DIRECTIONS, neighbor: CUBE_FACE_DIRECTIONS
):
    direction_index = DIRECTIONS_CLOCKWISE.index(direction)

    assert "face" in face
    face_index = CUBE_FACES_CLOCKWISE[face["face"]].index(neighbor)

    for i in range(4):
        d = DIRECTIONS_CLOCKWISE[(direction_index + i) % 4]
        s = CUBE_FACES_CLOCKWISE[face["face"]][(face_index + i) % 4]
        face["neighbors"][d] = s


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


class Solution(TextSolution):
    _year = 2022
    _day = 22

    @answer(66292)
    def part_1(self) -> int:
        return SparseGrid(self.input).run()

    # @answer(1234)
    def part_2(self) -> int:
        faces, face_map, size, instructions = parse_input(self.input)
        calculate_face_connectivity(faces, face_map)

        f = 0
        x = 0
        y = 0
        direction = "east"

        for instruction in instructions:
            if instruction == "L":
                direction = DIRECTIONS_CLOCKWISE[
                    (DIRECTIONS_CLOCKWISE.index(direction) + 3) % 4
                ]
                continue
            if instruction == "R":
                direction = DIRECTIONS_CLOCKWISE[
                    (DIRECTIONS_CLOCKWISE.index(direction) + 1) % 4
                ]
                continue

            for _ in range(instruction):
                print(f"\ntop! {f} {x} {y} {direction}")
                dx, dy = {
                    "east": [1, 0],
                    "south": [0, 1],
                    "west": [-1, 0],
                    "north": [0, -1],
                }[direction]

                new_x = x + dx
                new_y = y + dy
                new_f = f
                new_direction = direction

                # if not ((0 < new_x <= size) and (0 < new_y <= size)):
                print(f"  checking {new_x} {new_y}")
                if new_x < 0 or new_x >= size or new_y < 0 or new_y >= size:
                    print("resizing")
                    new_x = modulo(new_x, size)
                    new_y = modulo(new_y, size)
                    found = False
                    for k, v in faces.items():
                        print(
                            f'    does {v["face"]} eqq {faces[f]["neighbors"][direction]}?'
                        )
                        if v["face"] == faces[f]["neighbors"][direction]:
                            found = True
                            new_f = k
                            break
                    assert found
                    print(f"  going from {f} to {new_f}")

                    dir_index = DIRECTIONS_CLOCKWISE.index(direction)

                    new_dir_index = dir_index
                    print(
                        f'  outside comparing {faces[new_f]["neighbors"][ DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4] ]} to {faces[f]["face"]}'
                    )
                    while (
                        faces[new_f]["neighbors"][
                            DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4]
                        ]
                        != faces[f]["face"]
                    ):
                        print(
                            f'    comparing {faces[new_f]["neighbors"][ DIRECTIONS_CLOCKWISE[(new_dir_index + 2) % 4] ]} to {faces[f]["face"]}'
                        )
                        # raise ValueError()
                        new_x, new_y = size - 1 - new_y, new_x
                        new_dir_index = (new_dir_index + 1) % 4
                    new_direction = DIRECTIONS_CLOCKWISE[new_dir_index]

                print(f"  {new_f} {new_y} {new_x}")
                if faces[new_f]["grid"][new_y][new_x] == "#":
                    break

                x = new_x
                y = new_y
                f = new_f
                direction = new_direction

        i = faces[f]["i"] * size + y + 1
        j = faces[f]["j"] * size + x + 1

        return 1000 * i + 4 * j + DIRECTIONS_CLOCKWISE.index(direction)
