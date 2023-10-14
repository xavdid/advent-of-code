---
year: 2021
day: 2
title: "Dive!"
slug: "2021/day/2"
pub_date: "2021-12-02"
---

## Part 1

At first read, this seems very simple. Turns out, it is! There's probably a clever way to do it, but for something like this, I find that "clear" is best.

We need 2 variables: `depth` and `horiz` to track our position. Then we go through each line and split on the space. A little `if/else` block lets us choose which value to edit and in which direction. Then we multiply the results:

```py
depth = 0
horiz = 0

for ins in self.input:
    direction, value_str = ins.split(" ")
    value = int(value_str)
    if direction == "forward":
        horiz += value
    elif direction == "up":
        depth -= value
    elif direction == "down":
        depth += value
    else:
        raise ValueError(f'Unrecognized direction: "{direction}"')

return depth * horiz
```

The one thing to note is that we _could_ have done `else` instead of `elif direction == "down"`. Our input only has the 3 directions, so we'd be safe doing that. In the context of the puzzle, that's totally fine. In real life, I've found that pattern to be a common source of errors. If our input ever did add a 4th direction, then it would silently fall through to `down`'s block and cause weird bugs. So, if we get something we don't have an explicit case for, I'd rather error out than build on incomplete assumptions.

## Part 2

In an unusual move, part 2 needs only a couple of lines changed from part 1 to work. There's not much to say here- we'll add a third variable and slightly change what we do on each action. I've marked the lines that changed:

```py
depth = 0
horiz = 0
aim = 0 # added

for ins in self.input:
    direction, value_str = ins.split(" ")
    value = int(value_str)
    if direction == "forward":
        horiz += value
        depth += aim * value # added
    elif direction == "up":
        aim -= value # changed
    elif direction == "down":
        aim += value # changed
    else:
        raise ValueError(f'Unrecognized direction: "{direction}"')

return depth * horiz
```

---

A final note - if you're running Python `3.10`+, you can take advantage of "structural pattern matching" ([lengthy description](https://www.python.org/dev/peps/pep-0636/)). It doesn't change much about today's solution, but instead of saying "split the string and give me the direction and value", you can match against the _shape_ of the input. So it's more like "if `ins.split` is the word "forward" followed by any second item, do this". Here's that in practice:

```py
...

for ins in self.input:
    match ins.split(" "):
        case "forward", value:
            horiz += int(value)
        case "up", value:
            ...
```

Again, not super life changing here. But, hopefully we'll get a chance to do something else with it in a future day!
