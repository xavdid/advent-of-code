---
year: 2021
day: 4
title: "Giant Squid"
slug: "2021/day/4"
pub_date: "2021-12-04"
---

## Part 1

Nothing about this puzzle seemed too hard, but it took me a minute to figure out where to start. The game of bingo itself is simple, but knowing how to represent the boards and check them quickly is the rub. When we don't know how to start, we turn to the golden rule of writing code:

> make it work, make it fast, make it pretty

Let's get _something_ down (even if it's woefully inefficient) and we can figure everything else out later.

Our first task is to figure out how to represent the boards and rows. When representing any 2D grid, the classic approach is a list of lists:

```py
grid = [
  #  column
  #  0  1  2
    [1, 2, 3], # row 0
    [4, 5, 6], # row 1
    [7, 8, 9], # row 2
]
grid[0][1] # => 2
grid[1][2] # => 6
grid[2][0] # => 7
```

Once we've loaded the inputs into grids, we need to be able to check off pulled numbers. Each time a number is pulled, we'd need to loop through each row (and column; we can rotate rows using `zip` like we have [before](/writeups/2021/day/3/)) to see if any of them are a subset of the already-pulled numbers. If so, that board's a winner! If this approach sounds like a lot of repeated loops, it's because it is. We can certainly code it up, but let's consider an alternative way to store our input.

Because we're doing to be checking each row/column many times, it would be preferable to make that operation as fast as possible. Checking individual numbers with `if N in row` requires us to check every item in every row, every time. The `in` operator verifies membership in _linear_ time, meaning it takes longer as the length of the list grows. Ideally we'd use an approach that is always the same speed, no matter how long our list is. For that, we need a different data structure.

Whenever you need to check membership in a collection repeatedly and quickly, a `set` is usually a good place to start. It doesn't preserve the order of its elements, but it can check what it has super fast (aka in _constant_ time). But, don't we need to know the order of the items? We're relying on their positions in the grid to check for bingo in columns. Are there any other ways we could represent the board?

When you think about it, a board is really just 5 rows and 5 columns, or 10 sets of numbers that happen to have specific overlaps. Once you've stored those sets, the grid structure from before isn't all that important anymore. Then you can iterate through the lists and pull items out of the sets. If a set is empty, that row/column is empty and you've got a bingo! Make sense? Let's write some code. I have a feeling we'll need this in both parts, so let's put it in a function:

```py
def parse_boards(self):
    # first, get the list of pulled numbers
    pulls = list(map(int, self.input[0].split(",")))
    # then, get ready to parse boards
    raw_boards = [[]]
    # 2: so we can skip the pulls and the blank line
    for line in self.input[2:]:
        # an empty line means we're at the end of a board
        # add the columns and create a new, empty board
        if line == "":
            raw_boards[-1] += [*zip(*raw_boards[-1])]
            raw_boards.append([])
            continue

        # use .split() without an argument so it takes care of all the whitespace
        # also, save row as a tuple so order is preserved - we need that so columns are built right
        raw_boards[-1].append(tuple(map(int, line.split())))

    # save the last board because there's not a blank line at the end of the input
    raw_boards[-1] += [*zip(*raw_boards[-1])]

    # make everything a set
    # note the nested list comprehension!
    boards: List[List[Set[int]]] = [[set(x) for x in board] for board in raw_boards]
    return pulls, boards
```

Boom! I've left some detailed comments, so I'll let that code stand mostly on its own. You'll see that each board is now a list of 10 `set`s of `int`s; the first 5 are the rows, the second 5 are the columns.

Now we actually have to do our checking. We'll iterate through:

1. our pulled numbers
2. each board
3. each row/col in the board

and pull out that pulled number in each group. If the group is empty, bingo! Do some adding/multiplication. Because we set ourself up so nicely, this part is actually pretty straightforward:

```py
pulls, boards = self.parse_boards()

for pull in pulls:
   for board in boards:
       for group in board:
           group.discard(pull)
           if not group:
               # sum up all groups on this board; only do the first half
               # of the board since the remaining numbers are duplicated
               total = sum([sum(x) for x in board[:5]])
               return total * pull

# don't really need this since our puzzle is guaranteed to find the answer, but
# it's a good practice in case it's possible to fail to find
raise ValueError("no solution found")
```

The only thing to call out is that we only want to sum the _first 5_ groups. Remember, the numbers are duplicated in the columns, so our answers would be too high if we summed the whole board. Also, `.discard` is important because it happily does nothing if the item isn't in the set. Not all groups have each number, so it's important not to error. That's a wrap for part 1!

## Part 2

Part 2 isn't much harder than one, but we'll want to change our looping code. Luckily, we _can_ re-use all our parsing work.

The big difference is we need to track which boards haven't won yet. Once they do (using the same approach as above), we can skip them for the rest of the loops. If our code is too slow (which wasn't an issue, but it bears some thinking about), it'll save us some loops on as we narrow down the boards. Otherwise, our solution is similar:

```py
  pulls, boards = self.parse_boards()

  active_boards = set(range(len(boards)))
  for pull in pulls:
      for board_id, board in enumerate(boards):
          if board_id not in active_boards:
              continue

          for group in board:
              group.discard(pull)
              if not group:
                  active_boards.discard(board_id)
                  if not active_boards:
                      # sum up all groups on this board; only do the first half
                      # of the board since the remaining numbers are duplicated
                      total = sum([sum(x) for x in board[:5]])
                      return total * pull
```

`set(range(len(boards)))` is a cute way to get a set comprised of the numbers `0..N`, where `N` is the length of `boards`. Since a board's index is its "id", the initial set of active boards should be each of those indexes. After that, we have the same basic checks - whenever we find an empty set, that board is done for. If it's the last board (the `active_boards` set is now empty), then we do our same math.

Good job today! That parsing was tricky, but hopefully the actual solution was manageable.
