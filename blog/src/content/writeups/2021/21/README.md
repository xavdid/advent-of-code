---
year: 2021
day: 21
title: "Dirac Dice"
slug: "2021/day/21"
pub_date: "2021-12-30"
---

## Part 1

Part 1 here is... suspiciously straightforward. Let's code it out!

First we'll need a board and a die:

```py
from itertools import cycle

BOARD = list(range(1, 10 + 1))
BOARD_SIZE = len(BOARD)
DIE = cycle(range(1, 100 + 1))
```

`cycle` is an iterator that infinitely repeats its iterable. Perfect for our die that's going to roll over and over as we "roll" it with the `next(DIE)` function.

Next, we parse our input and store our players and their score:

```py
import re
from dataclasses import dataclass

@dataclass
class Player:
    position: int
    score = 0

players = list(
    # pos - 1, because they give us a square on the board, not an index
    map(lambda pos: Player(int(pos) - 1), re.findall(r": (\d+)", self.input))
)
```

Now, a little code trick. In Python, `bool` is a subset of `int`. Among other things, this means you can use `bool` wherever you usually use an `int`. In cases where you've a list with exactly 2 elements, you can easily swap the value of the bool to get the other item:

```py
l = ['a', 'b']

index = False # eqiv to 0
print(l[index]) # => 'a'

index = not index
print(l[index]) # => 'b'

index = not index
print(l[index]) # => 'a'
```

It's sort of a dumb trick, but very convenient when you need to swap between 2 values concisely.

Anyway, we can use this for our loop:

```py
total_rolls = 0
player_turn = False  # booleans are ints!
while True:
    p = players[player_turn]

    rolls = (next(DIE), next(DIE), next(DIE))
    total_rolls += 3

    p.position = (p.position + sum(rolls)) % BOARD_SIZE
    p.score += BOARD[p.position]

    if p.score >= 1000:
        return total_rolls * players[not player_turn].score

    player_turn = not player_turn
```

That should do it! I'm not sure part 2 won't be _dramatically_ worse on this day 21.

## Part 2

Welp. Those example values (~400 trillion) mean that it's unlikely we'll be able to re-use our part 1 code. We'll have to think through a different way to model this data.

We'll need to use _dynamic programming_ a technique that breaks down a big, complex problem into a combination of smaller, solvable ones. The classic example of how to implement this is the Fibonacci sequence. Wikipedia has [a great explanation](https://en.wikipedia.org/wiki/Dynamic_programming#Fibonacci_sequence) of this, which I'll summarize below.

The Fibonacci sequence is a list of numbers where each element is the sum of the previous 2. So, it's hard to know what the 10th number in that sequence is, since you have to know what the 8th and 9th are (and then need to know the 7th and 8th (and then need to know then 6th and 7th (and can you tell this is recursive?))).

The basic approach is simple:

```py
def fib(n) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

But, we're doing a lot of repeated work. If we call `fib(10)` (to get the 10th element), then it calls:

1. `fib(9)` + `fib(8)`
2. (`fib(8)` + `fib(7)`) + (`fib(7)` + `fib(6)`)
3. ((`fib(7)` + `fib(6)`) + (`fib(6)` + `fib(5)`)) + ((`fib(6)` + `fib(5)`) + (`fib(5)` + `fib(4)`))
4. ...

We've still got many more layers to go, and we've already called `fib(6)` four separate times (which will each spawn a whole tree of their own. But, every call to `fib(6)` has the exact same answer. So, once we've called it once, why don't we store the answer and just look it up any time we need it?

```py
answers = {0: 0, 1: 1}
def fib(n) -> int:
    if n in answers:
        return answers[n]
    result = fib(n - 1) + fib(n - 2)
    answers[n] = result
    return result
```

It's the same basic algorithm, but we store the answer for each input so a given `fib(N)` is only ever calculated once! This is a great tool to have in your arsenal any time you're doing a function with a lot of identical work.

---

Today's pt 2 follows a similar idea. Though there may seem like many games to play(and there are! trillions, in fact), there is a finite number of states a game can be in. Each player can be in one of 10 positions, and their score can only be one of 21 values, so a player is in one of `210` states. With 2 players we have to multiply that by itself, so there are `44,100` different states an active game can be in. Sounds much more manageable, right? If we cache the result of a given game state, we'll be able to stop early.

The hardest thing for me about this part was conceptualizing _what_ I was going to code. Reddit came in big here once again, especially this "[explain like I'm 5 thread](https://old.reddit.com/r/adventofcode/comments/rm7ygy/2021_day_21_part2_could_someone_explain_the/)". Let's walk through a simpler version of the problem, then scale up our code.

In our toy version, we'll make the following changes:

- We'll roll 2, two-sided dice. So on a given player's turn, they can score 2, 3, or 4 points (by moving that many steps).
- You just get the number of points you roll, no moving
- Games just end after 1 round (1 turn for each player)

So, we begin our game! On the first turn, we spawn 4 "sub games" for [each of the possible die rolls](https://youtu.be/POT3plx0vBs?t=2). Here are each of their results:

1. rolls `(1,1)`, p1 has 2 points
2. rolls `(1,2)`, p1 has 3 points
3. rolls `(2,1)`, p1 has 3 points
4. rolls `(2,2)`, p1 has 4 points

Easy enough so far. The same thing happens with player 2. For _each_ of those 4 games above, 4 more games happen:

1. rolls `(1,1)`, score is (in p1-p2 notation):
   1. 2-2
   2. 3-2
   3. 3-2
   4. 4-2
2. rolls `(1,2)` or `(2,1)`, score is:
   1. 2-3
   2. 3-3
   3. 3-3
   4. 4-3
3. rolls `(2,2)`, score is:
   1. 2-4
   2. 3-4
   3. 3-4
   4. 4-4

The game is now over! Some number of games are tied, but the rest of the games, someone wins. (and remember- in the real puzzle, there are no ties)

Let's think back to the actual puzzle - the question we're trying to answer is "how many games does each player win?". So, if a player won, we should return a tuple of `(1, 0)` for games player 1 wins and `(0, 1)` for games player 2 wins. This is the base case of our recursive function.

If no one has won, we run the game again after updating the position and points per the instructions. The resulting tuple for any given game is the number of sub-games each player won. So, if we do recurse, we should add those results to our running tally. Since we're calculating the game for a single player at a time, we can track them as the Active Player (`ap`) and the Inactive Player (`ip`).

With all that out of the way, I think we're finally ready to write some code!

```py
def play(ap_pos: int, ap_score: int, ip_pos: int, ip_score: int) -> Tuple[int, int]:
    ap_wins, ip_wins = 0, 0

    ...
```

Here's our basic function. We've got our active and inactive players, and we're tracking their scores and positions. Now, we do all the rolls:

```py
...

for roll in product([1, 2, 3], repeat=3):
    new_ap_pos = (ap_pos + sum(roll)) % BOARD_SIZE
    new_ap_score = ap_score + BOARD[new_ap_pos]

    if new_ap_score >= 21:
        ap_wins += 1
    else:
        ...
```

I touched on `itertools.product` [yesterday](/writeups/2021/day/20/); it gives us a nested loop so we can get every combination of the 3 rolls. For each game the active player has won, count the win otherwise, we'll recurse. To do that, we play a round where the active and inactive players have swapped. After all, it's the other person's turn.

```py
...

else:
    added_ip_wins, added_ap_wins = play(
        ip_pos, ip_score, new_ap_pos, new_ap_score
    )
    ap_wins += added_ap_wins
    ip_wins += added_ip_wins
```

Note that the variables come out backwards too- in this function, the current inactive player was the sub-games active player. Add those up, and we can return `ap_wins, ip_wins`.

Lastly, we slap on the magic `functools.cache`, which the runtime of our solution from "infinite time" to "instant". Not bad, not bad at all. That lets us use our logic from Fibonacci where as soon as we call the function with a state we've seen before, we skip all the calculation and just return the answer.

Here's the whole solution:

```py
... # part 1 imports
from functools import cache

@cache
def play(ap_pos: int, ap_score: int, ip_pos: int, ip_score: int) -> Tuple[int, int]:
    """
    describes a turn between the Active Player (`ap`) and the Inactive Player (`ip`).
    """
    ap_wins, ip_wins = 0, 0

    for roll in product([1, 2, 3], repeat=3):
        new_ap_pos = (ap_pos + sum(roll)) % BOARD_SIZE
        new_ap_score = ap_score + BOARD[new_ap_pos]

        if new_ap_score >= 21:
            ap_wins += 1
        else:
            # the active player becomes inactive
            added_ip_wins, added_ap_wins = play(
                ip_pos, ip_score, new_ap_pos, new_ap_score
            )
            ap_wins += added_ap_wins
            ip_wins += added_ip_wins

    return ap_wins, ip_wins

p1, p2 = parse_input() # parse input from part 1
return max(play(p1.position, 0, p2.position, 0))
```

Lot of mental complexity to today's but after all that, the code ended up pretty concise. That's how it goes sometimes. :smile:
