# Advent of Code

This is my tried-and-true helper package for the phenominal [Advent of Code](https://adventofcode.com/) puzzles.

## Quickstart

This repo has two main executables: `start` and `advent`. See below for their features.

1. Fork & clone this repo
1. Delete my solution files (`rm -rf solutions/20*`)
1. Start a new solution `./start 1`
1. Edit the newly created file at `solutions/YEAR/day_N/solution.py`
1. Get your answers using `./advent 1`
1. Repeat!

## ./start

### Usage

> `./start [-h] [day] [--year YEAR]`

Start a new Advent of Code solution

**positional arguments**:

- `day` (optional): Which puzzle day to start, between [1,25]. Defaults to the next day without a folder (matching `day_N`) in that year.

**optional arguments**:

- `-h, --help` (optional): show this help message and exit
- `--year YEAR` (optional): Puzzle year. Defaults to current year if December has begun, otherwise previous year.

### Examples

- `./start 1`
- `./start 3 --year 2019`

## ./advent

### Usage

> `./advent [-h] [--year year] [--slow] [--debug] [--profile] day`

Run a day of Advent of Code

positional arguments:

- `day` (required): Which puzzle day to run

optional arguments:

- `-h, --help` (optional): show this help message and exit
- `--year YEAR` (optional): Puzzle year. Defaults to current year if December has begun, otherwise previous year
- `--slow` (optional): specify that long-running solutions (or those requiring manual input) should be run
- `--debug` (optional): prints normally-hidden debugging statements
- `--profile` (optional): run solution through a performance profiler

### Examples

- `./advent 2`
- `./advent 5 --year 2019`
- `./advent 3 --slow`

## File Structure

<!-- generated with https://tree.nathanfriend.io/ -->

```
solutions/
├── ...
└── 2020/
    ├── day_1/
    │   ├── solution.py
    │   ├── input.txt
    │   └── README.md
    └── ...
```

- each year has a folder (`YYYY`)
- each day in that year (will eventually) have a folder (`day_N`)

Each `day_N` folder has the following files:

- `solution.py`, which has a `class Solution`. `./advent` epects both that filename and that classname exactly, so you shouldn't change them. See [Writing Solutions](#writing-solutions) for how the file is structured
- `input.txt` your input from the AoC site. You can put the example inputs in there as well while you're working
- `README.md` is a convenient place to take notes or explain your solution

## Writing Solutions

### The `Solution` Class

A helpful base class on which to build your AoC solutions. It's got 2 required properties (which should be pre-filled) if you use `./start`): `year` and `number`, corresponding to the puzzle you're solving.

Your puzzle input (the parsed contents of the local `input.txt`, see [File Structure](#file-structure)) will be available at `self.input`. It's also got an optional `input_type` property that gives you control over how the input is parsed (see [Reading Input](#reading-input)).

It's also got some convenience methods for print-based debugging: `self.pp` (pretty-print) and `self.newline`, which each only print anything if `self.debug` is true. You can set that manually, or via the `--debug` flag on the `./advent` command.

### Reading Input

AoC input takes a number of forms, so there are a number of simple modes in which input can be read. Pick a mode by setting `Solution.input_type` to one of the following `Enum` values:

| InputTypes.X | description                                             | input for this mode   |
| ------------ | ------------------------------------------------------- | --------------------- |
| TEXT         | one solid block of text; the default                    | `abcde`               |
| INTEGER      | one number                                              | `12345`               |
| TSV          | tab-separated values                                    | `a b c`<br>`d e f`    |
| STRSPLIT     | str[], split by a specified separator (default newline) | a<br>b<br>c<br>d<br>e |
| INTSPLIT     | int[], split by a specified separator (default newline) | 1<br>2<br>3<br>4<br>5 |

Specify `Solution.separator` to control how the SPLIT methods separate their input.

### Solution Functions

Each AoC puzzle has two parts, so there are two functions you need to write: `part_1` and `part_2`. Each should return an `int`, since that's the input that AoC expects back.

Sometimes, it's easier to calculate both parts in a single function (such as if the answer is asking about two parts of a single computation). In that case, there's also a `solve()` method, which should return a two-tuple with your answers (like `(5, 7)`).

`solve` takes precent if present. Feel free to delete any unused functions from this section.
