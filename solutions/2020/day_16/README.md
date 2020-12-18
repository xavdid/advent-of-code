# Day 16 (2020)

`Ticket Translation` ([Prompt](https://adventofcode.com/2020/day/16))

## Part 1

The oddest part of this prompt is the unusual input structure. After that, it's pretty straightforward.

First, we look at the requirements block. Each row follows the format `NAME: A-B or C-D`. Givne it's rigid structure, we'll be relying on `stirng.split` to parse data for storage. What exactly are we storing though? Later we'll need to be able to quickly tell whether or not a value is between those two numbers. Off the top of my head, I had two ideas:

- a nameless lambda function once we've parsed out both `int`s, we could return `lambda v: a <= v <= b`
- a 2-tuple of the low and high values. I could check that values are betwen those with a similar approach to the function

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

Now we get to the matching. We need a way to tie values to fields. There's probably a known algorithm for that, but I don't know it offhand. Let's take a swing at a solution and check Reddit if we can't figure it out.

My first approach will be doing a pass over all tickets to see if I can isolate values that only match a single field. Let's see where that gets us.

First we need to filter out invalid tickets:

```py
def is_valid_ticket(self, ticket: str) -> bool:
    return all([self.is_valid_value(int(v)) for v in ticket.split(",")])

# ---

tickets = self.input.split("\n\n")[2].split("\n")[1:]
valid_tickets = [t for t in tickets if self.is_valid_ticket(t)]
```
