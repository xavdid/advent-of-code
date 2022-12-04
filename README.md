# Advent of Code

This is my tried-and-true Python helper package for the phenomenal [Advent of Code](https://adventofcode.com/) puzzles. It contains helpful utilities, plus my [daily solution write-ups](https://github.com/xavdid/advent-of-code/tree/main/solutions).

It expects to be run using at least Python 3.9.

## Quickstart

To use this base class for your own solutions:

1. Fork & clone this repo
2. Delete my solution files (`rm -rf solutions/20*`)
3. Start a new solution using `./start` (defaults to the current year once December starts)
4. Edit the newly created file at `solutions/YEAR/day_01/solution.py`
5. Get your answers using `./advent`
6. Repeat!

## Commands

This repo has two main commands: `start` and `advent`.

### `./start`

#### Usage

> `./start [-h] [--year YEAR] [day]`

Start a new Advent of Code solution

**positional arguments**:

- `day` (optional): Which puzzle day to start, between `[1,25]`. Defaults to the next day _without_ a folder (matching `day_NN`) in the specified year.

**optional arguments**:

- `-h, --help` (optional): show this help message and exit
- `--year YEAR` (optional): Puzzle year. Defaults to current year if December has begun, otherwise previous year.

#### Examples

- `./start`
- `./start 1`
- `./start 3 --year 2019`

### `./advent`

#### Usage

> `./advent [--year year] [--test-data] [--debug] [--profile] [--slow] [day]`

Run a specific day of Advent of Code

**informational flags**

- `-h, --help`: Show this help message and exit
- `--version`: Print version info and exit

**positional arguments**:

- `day` (optional): Which puzzle day to start, between `[1,25]`. Defaults to the latest day _with_ a folder (matching `day_NN`) in the specified year.

**optional flags**:

- `--year YEAR`: puzzle year. Defaults to current year if December has begun, otherwise previous year
- `-t, --test-data`: read puzzle input from `input.test.txt` instead of `input.txt`
- `--debug`: prints normally-hidden debugging statements (written with `self.pp(...)`)
- `--profile`: run solution through a performance profiler
- `--slow`: specify that long-running solutions (or those requiring manual input) should be run. They're skipped otherwise

#### Examples

- `./advent`
- `./advent 2`
- `./advent 5 --year 2019`
- `./advent 7 --test-data`

## File Structure

<!-- generated with https://tree.nathanfriend.io/ -->

```
solutions/
├── ...
└── 2020/
    ├── day_01/
    │   ├── solution.py
    │   ├── input.txt
    │   ├── input.test.txt
    │   └── README.md
    ├── day_02/
    │   ├── solution.py
    │   ├── ...
    └── ...
```

- each year has a folder (`YYYY`)
- each day in that year (will eventually) have a folder (`day_NN`)

Each `day_NN` folder has the following files:

- `solution.py`, which has a `class Solution`. `./advent` expects both that filename and that class name exactly, so you shouldn't change them. See [Writing Solutions](#writing-solutions) for how the file is structured
- `input.txt` holds your input from the AoC site
- `input.test.txt` holds the example input from the prompt. It's read when the `--test-input` flag is used (see below). It also won't throw errors if the result doesn't match the [answer](#saving-answers). You can also do all your work in `input.txt`, but it's marginally less convenient
- `README.md` is a convenient place to take notes or explain your solution

## Writing Solutions

### The `Solution` Class

A helpful base class on which to build your AoC solutions. It's got 2 required properties (which should be pre-filled if you use `./start`): `_year` and `_day`, corresponding to the puzzle you're solving.

Your puzzle input (the parsed contents of the local `input.txt`, see [File Structure](#file-structure)) will be available at `self.input`. It's also got an optional `input_type` property that gives you control over how the input is parsed (see [Reading Input](#reading-input)).

It's also got some convenience methods for print-based debugging: `self.pp` (pretty-print) and `self.newline`, which each only print anything if `self.debug` is true. You can set that manually, or via the `--debug` flag on the `./advent` command.

### Reading Input

AoC input takes a number of forms, so there are a number of simple modes in which input can be read & parsed. Your generated `Solution` class should inherit from one of the below classes, which will parse (and add types to) `self.input` for you

| Inherited Class    | description                                               | input for this mode   |
| ------------------ | --------------------------------------------------------- | --------------------- |
| `TextSolution`     | one solid block of text; the default                      | `abcde`               |
| `IntSolution`      | one number                                                | `12345`               |
| `StrSplitSolution` | `str[]`, split by a specified separator (default newline) | a<br>b<br>c<br>d<br>e |
| `IntSplitSolution` | `int[]`, split by a specified separator (default newline) | 1<br>2<br>3<br>4<br>5 |
| `TSVSolution`      | tab-separated values                                      | `1 2 3`<br>`4 5 6`    |

Specify `Solution.separator` to control how the SPLIT methods separate their input.

### Solution Functions

Each AoC puzzle has two parts, so there are two functions you need to write: `part_1` and `part_2`. Each should return an `int`, since that's typically the answer that AoC expects.

Sometimes, it's easier to calculate both parts in a single function (such as if the answer is asking about two parts of a single computation). In that case, there's also a `solve()` method, which should return a 2-tuple with your answers (like `(5, 7)`). `solve` takes precedence if present. Feel free to delete any unused functions when you're done.

### Saving Answers

Once you've solved the puzzle, you can decorate your function (`solve` or `part_N`) with the `@answer` decorator. It asserts that the value returned from the function is whatever you pass to the decorator:

```py
@answer(3)
def only_three(i):
    return i

only_three(1) # error!
only_three(3) # ok
```

This is helpful for ensuring your answer doesn't change when editing your code after you've solved the puzzle. It's included as a comment in the template. It's ignored when running against test input, so it's easy to verify as you go.

### Debugging

The base class includes a `self.pp` method which will pretty-print all manner of inputs. These only show up when the `--debug` flag is used, making it a convenient way to show debugging info selectively.

### Marking Slow Solutions

If you're running many solutions at once and want to exclude individual parts of solutions (or entire days), you can mark individual functions with the `@slow` decorator. They'll print a warning, but won't actually run the solution.
