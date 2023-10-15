---
year: 2020
day: 2
title: "Password Philosophy"
slug: "2020/day/2"
pub_date: "2020-12-02"
---

## Part 1

Our first goal today, like most days, is extracting the important information out of the input. Each line is well-structured, so we can safely break each down in a reliable fashion:

<!-- prettier-ignore -->
1. We start with `'1-3 a: abcde'`
2. Splitting on `: ` gives `['1-3 a', 'abcde']`. Our actual password is free!
3. Splitting the first result from (2) on `' '` gives `['1-3', 'a']` - the char is now available.
3. Splitting the first result from (3) on `'-'` gets us the string version of our two numbers: `['1', '3']`.

Now that we've got each part separated, we can wrap this logic in a function. The last thing we need is to make sure to return `int`s instead of strings for the count:

```py
def parse_policy(line: str) -> Tuple[int, int, str, str]:
    policy, password = line.split(": ")

    counts, char = policy.split(" ")
    min_count, max_count = counts.split("-")

    return int(min_count), int(max_count), char, password
```

Back in our main logic, we can actually do the counts:

```py
num_valid = 0
for line in self.input:
    min_count, max_count, char, password = parse_policy(line)

    if min_count <= password.count(char) <= max_count:
        num_valid += 1

return num_valid
```

## Part 2

Much of this will look the same as part 1, our loop logic just changes a bit. Looking up the character in each location is simple. In fact, the only tricky new thing is how to express exactly one of the characters matching. We want exactly one, not both or neither.

As luck would have it, the `XOR` (aka "Exclusive Or", [wiki](https://en.wikipedia.org/wiki/Exclusive_or)) operation (`^`) does exactly that!

Result of `A ^ B`:

| A input | B input | result |
| ------- | ------- | ------ |
| false   | false   | false  |
| true    | false   | true   |
| false   | true    | true   |
| true    | true    | false  |

Those match our test cases, so let's use it:

```py
num_valid = 0
for line in self.input:
    first_index, second_index, char, password = parse_policy(line)

    if (password[first_index - 1] == char) ^ (
        password[second_index - 1] == char
    ):
        num_valid += 1

return num_valid
```
