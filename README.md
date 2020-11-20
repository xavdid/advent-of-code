# Advent of Code

These are my results in the [Advent of Code](https://adventofcode.com/). Hopefully I'll do it every day in December. I usually don't.

## Usage

> see more info by running ./advent -h

To see solution(s) for a day, run the following:

```
./advent <day>
```

There's also an option to run solutions from a certain year (the `--year` flag) and to run solutions that have been marked slow.

## New Solutions

To solve a new day, run `./start <day> [year]` which will set you up with some files with blank methods to implement and a placeholder input file. It defaults to the recent year, but you can generate new files for past years too.

## Conveniences

### Reading input

That got repetitive fast. Each solution reads its corresponding input .txt file and depending on the value of `self.input_type`, it'll parse the file differently. See `BaseSolution.InputTypes` for the options.

### Same function, two ansewrs

It's easier to get two answers out of a single function call; for this, we use `solve()`. See 2018 days 6, 8, and 9 for exmples.

If the solutions are different enough, `part_1()` and `part_2()` can return individual ansswers. For example, 2018 days 1 and 2.

## New Year

Note to self:

Update the year in both `start` and `advent`. If I ever have a test suite, then I'll want to always include the year so they won't break year to year.
