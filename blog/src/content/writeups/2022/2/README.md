---
year: 2022
day: 2
title: "Rock Paper Scissors"
slug: "2022/day/2"
pub_date: "2022-12-02"
---

## Part 1

Readers will hopefully feel right at home with the rules of rock-paper-scissors, but can [read up](https://en.wikipedia.org/wiki/Rock_paper_scissors) if it's unfamiliar. It's our job to implement it!

While there may be a clever way to do this, the most maintainable [^1] way will be rather verbose. But, it'll be easy to follow and maintain. Let's start with an `enum`, so we can be extra sure which shapes we're dealing with:

```py
from enum import Enum

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
```

Enums are great for descriptive code. Because they're plain english, we can be very expressive with our conditionals. As written, Python enums are only comparable to other enum members.[^2] We also have a helper function to translate from a letter into an enum property.

Next, we should parse our input. We'll use a similar construct to [day 1](/writeups/2022/day/1/), where we combine `map` with a function to quickly transform input data:

```py
from typing import List, Tuple

...

# my base class
class Solution(StrSplitSolution):

    def parse_games(self) -> List[Tuple[Shape, Shape]]:
        return [tuple(map(Shape.from_letter, game.split(" "))) for game in self.input]
```

Note that we didn't actually call `Shape.from_letter` (it has no parens). Instead, we provide `map` the function _to_ call, and it takes care of actually running `Shape.from_letter(game.split(" ")`. Also, the function includes some basic type information (which isn't strictly necessary, but I find helps me catch bugs while writing). With that, we'll have a list of tuples like `(Shape.ROCK, Shape.Scissors)`.

Next we have to actually play the game. Given a game, we should return a number based on who won and the shape used:

```py
...

def value_for_game(moves: Tuple[Shape, Shape]) -> int:
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
```

In each case, we're returning the `.value` of a `Shape` (the number the enum was declared with) added to the value of the result. There are's only 3 cases, so it's not too hard to write out.

All that remains is to put everything together:

```py
class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        return sum(value_for_game(game) for game in self.parse_games())
```

## Part 2

For part 2, instead of the second letter describing your move, it describes what your move should be _based_ on your opponent's move. This will require an extra lookup step, but isn't actually much more complicated.

First we need another enum, to describe the desired result of the game:

```py
...

class Result(Enum):
    LOSE = "X"
    TIE = "Y"
    WIN = "Z"
```

Notice how we can use both letters and numbers for enum values! This is a convenient way to go from a string into its corresponding enum member, which we have to do now:

```py
...

def parse_shape_and_result(game: str) -> Tuple[Shape, Result]:
    shape, result = game.split(" ")
    return Shape.from_letter(shape), Result(result)

class Solution(StrSplitSolution):
    ...

    def parse_goals(self) -> List[Tuple[Shape, Result]]:
        return [parse_shape_and_result(game) for game in self.input]
```

Similar to before, we'll end up with semantically meaningful versions of our input. Next we have to turn that pair into a game state, which we can plug into our `value_for_game` from part 1. To do that, we need a way to get a `Shape` based on a `Shape` & `Result`. While we could write a big function with lots of `if` statements, there's a simpler way. As luck would have it, `enum` members can be used as dictionary keys! Check this out:

```py
...

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
```

We've built ourselves a little decision tree! We didn't even have to include the `TIE` case, since we don't need any extra info for that. Here's our function to calculate the value for a desired result:

```py
...

def value_for_desired_result(game_state: Tuple[Shape, Result]) -> int:
    opp, res = game_state

    if res == Result.TIE:
        return value_for_game((opp, opp))

    return value_for_game((opp, SHAPE_TO_PICK[opp][res]))
```

Each branch returns the game value, but what we send to that function depends on what comes out of `SHAPE_TO_PICK`. Finally, we put it all together and we've done it!

```py
class Solution(StrSplitSolution):
    ...

    def part_2(self) -> int:
        return sum(value_for_desired_result(state) for state in self.parse_goals())
```

[^1]: Remember, in these writeups we're practicing writing clear, maintainable solutions. My goal isn't to write my solution the quickest or with the fewest [characters](https://en.wikipedia.org/wiki/Code_golf).
[^2]: In our case, `Shape.ROCK != 1`, even though `Shape.ROCK.value == 1`. To make your enum compare to its underlying primitive, it should inherit from that type (e.g. `class X(int, Enum)`).
