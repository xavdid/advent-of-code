# Advent of Code 2017

These are my results in the [Advent of Code](https://adventofcode.com/).
Hopefully I'll do it every day in December. Maybe not.

## Usage

To see solution(s) for a day, run the following:

```
./advent <day>
```

## New Solutions

To solve a new day, run `./start <day>` which will set you up with some files
with blank methods to implement and a placeholder input file.

## Shortcuts

### Reading input

That got repetitive fast. Each solution reads its corresponding input .txt file
and depending on the value of `self.input_type()`, it'll parse the file
differently. See `BaseSolution.InputTypes` for the options.

### Same function, two ansewrs

If the answer ends up being a single method that returns a tuple for parts 1 and
2, put the whole thing in `solve()` and you can delete the placeholders for
parts 1 and 2. See days 6, 8, and 9 for exmples.
