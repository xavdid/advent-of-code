---
year: 2020
day: 16
title: "Ticket Translation"
slug: "2020/day/16"
pub_date: "2020-12-19"
---

## Part 1

The oddest part of this prompt is the unusual input structure. After that, it's pretty straightforward.

First, we look at the requirements block. Each row follows the format `NAME: A-B or C-D`. Given it's rigid structure, we'll be relying on `string.split` to parse data for storage. What exactly are we storing though? Later we'll need to be able to quickly tell whether or not a value is between those two numbers. Off the top of my head, I had two ideas:

- a nameless lambda function once we've parsed out both `int`s, we could return `lambda v: a <= v <= b`
- a 2-tuple of the low and high values. I could check that values are between those with a similar approach to the function

Both of those would work, but there's an even better option: Python's `range`. The range object can check if a number is in its bounds, and it does so [very quickly](https://stackoverflow.com/a/30081318/1825390). Sounds like a great way to store this info:

```py
def parse_requirements(self) -> None:
    if self.validators:
        return
    requirements_block = self.input.split("\n\n")[0]
    for line in requirements_block.split("\n"):
        field, function_blueprint = line.split(": ")
        ranges = []
        for f in function_blueprint.split(" or "):
            low, hi = f.split("-")
            # the last number isn't included in the range
            # our input is inclusive, so we have to inc the top by 1
            ranges.append(range(int(low), int(hi) + 1))

        self.validators[field] = ranges
```

Once we've done that, we can write a function that runs a value through all the `range`s and ensures the value passes _something_:

```py
def is_valid_value(self, value: int) -> bool:
    for validators in self.validators.values():
        for r in validators:
            if value in r:
                return True
    return False
```

Now we call it and get our answer:

```py
self.parse_requirements()
nearby_tickets_block = self.input.split("\n\n")[2]
total = 0
for line in nearby_tickets_block.split("\n")[1:]:
    for v in line.split(","):
        if not self.is_valid_value(int(v)):
            total += int(v)

return total
```

## Part 2

Now we get to the matching. First, we throw out the invalid tickets (tickets where any value falls outside the range of every validator). I've refactored my part 1 code a bit so I don't actually use the following function, but the gist is the following:

```py
def is_valid_ticket(self, ticket: str) -> bool:
    return all([self.is_valid_value(int(v)) for v in ticket.split(",")])

# ---

tickets = self.input.split("\n\n")[2].split("\n")[1:]
valid_tickets = [
    list(map(int, t.split(","))) for t in tickets if self.is_valid_ticket(t)
]
```

Now that we only have valid tickets, we need to group up all the numbers for each field. The prompt mentions that the fields are always in the same order for each ticket. So, we need groups of each ticket's 1st element, 2nd element, etc. You can think of this as _rotating_ the tickets. If we've got tickets `A`-`E` and each row is a `list`:

```
A0 A1 A2 A3 A4
B0 B1 B2 B3 B4
C0 C1 C2 C3 C4
D0 D1 D2 D3 D4
E0 E1 E2 E3 E4
```

becomes the following (the ticket order doesn't matter):

```
E0 D0 C0 B0 A0
E1 D1 C1 B1 A1
E2 D2 C2 B2 A2
E3 D3 C3 B3 A3
E4 D4 C4 B4 A4
```

The rest of this code is going to have a lot of `list`/`set` comprehensions, so strap in. We can rotate the tickets like so:

```py
value_sets: List[Set[int]] = [
    {ticket[column] for ticket in valid_tickets}
    for column in range(len(self.validators))
]
```

We step through each column and, for each, return a set of the value in that position in each ticket. Now that we know all the values for each unknown column, we can compare the `value_set` to all the validators. If a `value_set` only passes a single pair of validators, then we know we've found that field and can take it out of the pool. Let's start with the standalone function:

```py
def all_values_pass_validators(
    self, value_set, validators: List[Sequence[int]]
) -> bool:
    return all([any(v in validator for validator in validators) for v in value_set])
```

Another nested comprehension. It's only necessary because the validators come in pairs, but it's necessary nonetheless. For each value in the `value_set`, we're checking if it passes `any` validator. Then, we're running each of those results (a `List[bool]`) through `all` to know if we have an exact match. We'll call this like so:

```py
def possible_columns_for_values(self, value_set) -> List[str]:
return [
    field_name
    for field_name, validators in self.validators.items()
    if self.all_values_pass_validators(value_set, validators)
]
```

We make a list of field names (the keys from `self.validators`) if all values in the `value_set` pass all the validators for that name. Lots of list comprehensions here, but nothing too tricky!

Now, back to the main loop. We want to keep looping over `self.validators` until it's empty. For each `value_set`, we calculate all the columns the set fulfills. If there's only 1, bingo! We'll store the name (which we'll need later) and the index of that field. We also remove the validator from contention. This means our first loop through `self.validators` will be the longest, but it will speed up once we start identifying fields. Let's check it out:

```py
column_names = {}
while self.validators:
    for index, value_set in enumerate(value_sets):
        possible_columns = self.possible_columns_for_values(value_set)
        if len(possible_columns) == 1:
            field_name = possible_columns[0]
            column_names[field_name] = index
            self.validators.pop(field_name)
```

This approach only works if we're able to uniquely identify any fields. Luckily, we are! Here's the output when we log at the top of the `while` loop and when we identify a column:

<details>
<summary>Log Output</summary>

```
Top of loop, 20 unknown fields remain
field "arrival location" identified at column 2
field "class" identified at column 17
field "arrival platform" identified at column 18

Top of loop, 17 unknown fields remain
field "row" identified at column 0
field "arrival station" identified at column 16

Top of loop, 15 unknown fields remain
field "type" identified at column 13
field "train" identified at column 19

Top of loop, 13 unknown fields remain
field "arrival track" identified at column 15

Top of loop, 12 unknown fields remain
field "departure time" identified at column 14

Top of loop, 11 unknown fields remain
field "departure station" identified at column 7
field "departure platform" identified at column 10

Top of loop, 9 unknown fields remain
field "departure date" identified at column 4
field "departure track" identified at column 11

Top of loop, 7 unknown fields remain
field "departure location" identified at column 9

Top of loop, 6 unknown fields remain
field "route" identified at column 5

Top of loop, 5 unknown fields remain
field "seat" identified at column 1
field "wagon" identified at column 6

Top of loop, 3 unknown fields remain
field "duration" identified at column 3
field "price" identified at column 8
field "zone" identified at column 12
```

</details>

All that's left is to calculate the final answer. We need each `departure X` field and multiply the result. One last comprehension, for old times sake:

```py
from math import prod

my_ticket = list(
    map(int, self.input.split("\n\n")[1].split("\n")[1].split(","))
)

return prod(
    [
        my_ticket[field_index]
        for field_name, field_index in column_names.items()
        if field_name.startswith("departure")
    ]
)
```

I thought this nested (and nested (and nested)) approach would be slow, but all of our operations are fast and the data isn't big. I'm happy to report that Python never breaks a sweat.
