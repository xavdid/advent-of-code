---
year: 2022
day: 11
title: "Monkey in the Middle"
slug: "2022/day/11"
pub_date: "2022-12-11"
---

## Part 1

Another day, another unusual bout of input parsing. Before we get into it, it's worth examining our sample input (and our actual input) to see what sorts of cases in the input we can ignore. For example, the id of the monkey is only ever 1 digit long. Can we leverage that to make parsing our input simpler?

Take a sec to make a little list of observations and then come back to compare with what I found.

---

Each of these items would make our code worse at parsing the "general case" of valid monkey input, but make our parsing code much simpler. Here's what I found:

1. The monkey id is only ever a single digit, and it's in the same index in the first line. It doesn't need to be a number, we never do math with it
2. Items are comma separated and _do_ need to be numerical
3. Every operation line starts with `Operation: new = old `, so we really only need to worry about the operator that comes right after that
4. The only operators are `+` and `*`
5. The second value in that equation is either `old` or a (potentially multi-digit) number
6. Each test begins with `Test: divisible by`, so we can split that line by spaces and just look at the last thing
7. The last lines are always "if true" followed by "if false", and they each specify a monkey id in the last (space-separated) position. So we can do the same thing- split and look at the last item (which doesn't need to be an `int`, as discussed in point #1)

Put those together, and our parsing looks downright simple! Here it is, wrapped in a `Monkey` class:

```py
from operator import add, mul

OPS = {"+": add, "*": mul}

class Monkey:
    operation: Callable[[int], int]

    def __init__(self, raw_monkey: str) -> None:
        lines = raw_monkey.split("\n")
        self.num_inspections = 0

        # monkey id
        self.id = lines[0][7]
        # starting items
        self.items = list(map(int, lines[1].split(":")[1].split(",")))
        # operation
        operator, val = lines[2].split(" = old")[1].split()
        if val == "old":
            self.operation = lambda old: old * old
        else:
            self.operation = lambda old: OPS[operator](old, int(val))
        # test
        self.divisor = int(lines[3].split()[-1])
        # if true
        self.if_true = lines[4].split()[-1]
        # if false
        self.if_false = lines[5].split()[-1]

    def __repr__(self) -> str:
        return f"<Monkey id={self.id} num_inspections={self.num_inspections} items={self.items}>"
```

The only really tricky thing is the `lambda`s to dynamically define functions. Because we don't know what we'll need ahead of time, we have to create them as we go, based on the monkey spec. We combine that with Python's `operator` module, which houses the functions that power basic operations, including arithmetic. That let's us map `+` and `*` dynamically to the `add` and `mul` functions, respectively. We also include a `__repr__` function, which will pretty-print our monkeys when we need to do any debugging, like so (showing the monkeys after the first round of the sample data):

```py
{'0': <Monkey id=0 num_inspections=2 items=[20, 23, 27, 26]>,
 '1': <Monkey id=1 num_inspections=4 items=[2080, 25, 167, 207, 401, 1046]>,
 '2': <Monkey id=2 num_inspections=3 items=[]>,
 '3': <Monkey id=3 num_inspections=5 items=[]>}
```

Then, we parse the monkeys into a lookup map:

```py
class Solution(StrSplitSolution):

    separator = "\n\n" # each item of input is a full monkey block

    def parse_monkeys(self) -> Dict[str, Monkey]:
        result = {}
        for monkey in self.input:
            m = Monkey(monkey)
            result[m.id] = m
        return result
```

All that remains is to step through the instructions, carefully. That mostly speaks for itself:

```py
class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        monkeys = self.parse_monkeys()
        for _ in range(20):
            for monkey in monkeys.values():
                monkey.num_inspections += len(monkey.items)
                for item in monkey.items:
                    item = monkey.operation(item) // 3
                    dest = (
                        monkey.if_true
                        if item % monkey.divisor == 0
                        else monkey.if_false
                    )
                    monkeys[dest].items.append(item)

                monkey.items = []
```

We step through the instructions per the prompt and shuffle items around. Monkeys' `num_inspections` go up by the number of items they have at the start of the turn.

The last thing is calculating the answer. We have to sort our `Monkey` objects, which doesn't work out of the box; we get `'<' not supported between instances of 'A' and 'A'` when trying to sort `monkeys.values()`. To remedy this, we need to give `Monkey` a way to compare itself to other instances. All we need to define is `__lt__`:

```py
class Monkey:
    ...

    def __lt__(self, other: "Monkey") -> bool:
        return self.num_inspections < other.num_inspections

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        ...

        sorted_monkeys = list(sorted(monkeys.values()))
        return sorted_monkeys[-1].num_inspections * sorted_monkeys[-2].num_inspections
```

Once they know how to get in order, we have our answer!

## Part 2

Part 2 starts out easy enough- we pull our `// 3` and run the game for 10k rounds instead of just 20. But... it runs without finishing. A quick peek in the profiler (see my `./advent` [command's docs](https://github.com/xavdid/advent-of-code/#advent)) shows that all the time is being spent on the line that processes `old * old`. Without our worry level decreasing, the numbers just grow indefinitely. Turns out squaring increasingly large numbers gets slow.

To fix this, we'll need to shrink the worry levels as we go, but in a way that doesn't change any of our math. Specifically, we have to shrink each item by a value that doesn't change the result of `item % monkey.divisor`. Turns out, if you mod a number by the least common multiple of a group of numbers, it remains evenly divisible by all those numbers individually. This is one of those puzzle tricks that I remembered, but don't understand the justification for well. Basically the AoC equivalent of [crosswordese](https://en.wikipedia.org/wiki/Crosswordese).

Once I had my answer, I stopped by the [subreddit's answer thread](https://old.reddit.com/r/adventofcode/comments/zifqmh/2022_day_11_solutions/) and found [a great explanation](https://old.reddit.com/r/adventofcode/comments/zifqmh/2022_day_11_solutions/izrrnr3/) by `/u/QultrosSanhattan`. Definitely recommend reading if you're curious about the math backing this part.

Anyway, the code for part 2 isn't actually much once you know the trick. We'll move our solution into a function so we can control individual bits of it:

```py
class Solution(StrSplitSolution):
    ...
    def simulate_monkeys(
        self, num_rounds: int, worry_decreaser: int, shrinker: int | None = None
    ) -> int:
        monkeys = self.parse_monkeys()
        for _ in range(num_rounds): # add variable
            for monkey in monkeys.values():
                monkey.num_inspections += len(monkey.items)
                for item in monkey.items:
                    item = monkey.operation(item) // worry_decreaser # add variable
                    # mod the value, if applicable
                    if shrinker:
                        item = item % shrinker
                    dest = (
                        monkey.if_true
                        if item % monkey.divisor == 0
                        else monkey.if_false
                    )
                    monkeys[dest].items.append(item)

                monkey.items = []
```

And finally, our answers:

```py
from math import lcm
...

class Solution(StrSplitSolution):
    ...

    def part_1(self) -> int:
        return self.simulate_monkeys(20, 3)

    def part_2(self) -> int:
        monkeys = self.parse_monkeys()
        shrinker = lcm(*(m.divisor for m in monkeys.values()))
        return self.simulate_monkeys(10_000, 1, shrinker)
```

Days like this are tough, since you either know the trick or you don't. But, now that you've seen it, you'll know it in the future!
