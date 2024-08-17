# prompt: https://adventofcode.com/2022/day/2


from enum import Enum
from typing import cast

from ...base import StrSplitSolution, answer


class Shape(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @classmethod
    def from_letter(cls, letter: str) -> "Shape":
        if letter in ["A", "X"]:
            return cls.ROCK
        if letter in ["B", "Y"]:
            return cls.PAPER
        if letter in ["C", "Z"]:
            return cls.SCISSORS

        raise ValueError("unknown letter", letter)


class Result(Enum):
    LOSE = "X"
    TIE = "Y"
    WIN = "Z"


def value_for_game(moves: tuple[Shape, Shape]) -> int:
    opp, you = moves

    # tie
    if you == opp:
        return you.value + 3

    # you win
    if (
        (you == Shape.ROCK and opp == Shape.SCISSORS)
        or (you == Shape.PAPER and opp == Shape.ROCK)
        or (you == Shape.SCISSORS and opp == Shape.PAPER)
    ):
        return you.value + 6

    # you lose
    return you.value


def parse_shape_and_result(game: str) -> tuple[Shape, Result]:
    shape, result = game.split(" ")
    return Shape.from_letter(shape), Result(result)


SHAPE_TO_PICK = {
    Shape.ROCK: {
        Result.LOSE: Shape.SCISSORS,
        Result.WIN: Shape.PAPER,
    },
    Shape.PAPER: {
        Result.LOSE: Shape.ROCK,
        Result.WIN: Shape.SCISSORS,
    },
    Shape.SCISSORS: {
        Result.LOSE: Shape.PAPER,
        Result.WIN: Shape.ROCK,
    },
}


def value_for_desired_result(game_state: tuple[Shape, Result]) -> int:
    opp, res = game_state

    if res == Result.TIE:
        return value_for_game((opp, opp))

    return value_for_game((opp, SHAPE_TO_PICK[opp][res]))


class Solution(StrSplitSolution):
    _year = 2022
    _day = 2

    def parse_shapes(self) -> list[tuple[Shape, Shape]]:
        return [
            cast(tuple[Shape, Shape], tuple(map(Shape.from_letter, game.split(" "))))
            for game in self.input
        ]

    def parse_goals(self) -> list[tuple[Shape, Result]]:
        return [parse_shape_and_result(game) for game in self.input]

    @answer(9177)
    def part_1(self) -> int:
        return sum(value_for_game(game) for game in self.parse_shapes())

    @answer(12111)
    def part_2(self) -> int:
        return sum(value_for_desired_result(state) for state in self.parse_goals())
