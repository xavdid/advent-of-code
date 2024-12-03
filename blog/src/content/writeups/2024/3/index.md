---
year: 2024
day: 3
slug: "2024/day/3"
title: "Mull It Over"
# concepts: ["regex"]
pub_date: "2024-12-03"
---

## Part 1

Today we're tasked with finding specifically-shaped text in a larger string, which is a perfect use case for [Regular Expressions](https://en.wikipedia.org/wiki/Regular_expression)!

![](https://imgs.xkcd.com/comics/regular_expressions.png)

A lot of programmers shy away from regex because of the (admittedly) opaque syntax, but for simple use cases (like this!) they're extremely powerful and easy to write.

A regular expression involves:

1. a pattern, which is the shape of the text you want to extract, and
2. the input string, the text you're searching

Once we've written our pattern, Python will tell us if the given text (our puzzle input) matches that pattern. In our case, our pattern will look for the word `mul` followed by `(`, a 1-3 digit number, a comma, another number and a final `)`.

When writing a regex pattern, most text is treated literally. For example, the pattern `123` would find that exact substring anywhere in a larger string. As written, it works just like like `'some numbers like 123 or 456'.find('123')`, which isn't especially useful yet.

Regex shines when you use special tokens which can match text dynamically. Instead of just looking for literally `123`, we could use the `\d` token to match _any_ digit. We can supply that token multiple times to match numbers with a specific number of digits (e.g. `\d\d\d` would match all 3-digit numbers, but no 2-digit numbers). You can also use the `{min,max}` suffix to match the previous token between `min` and `max` times. So `\d{1,3}` will match all 1, 2, and 3 digit numbers (which is exactly what we need).

That's actually all we need to find our commands! We can now find all of our `mul` instructions with `re.findall` which finds all matches of your pattern:

```py
import re # built-in regex module

class Solution(TextSolution):
    def part_1(self) -> int:
        mul_instructions = re.findall(r"mul\(\d{1,3},\d{1,3}\)", self.input)
        # => ['mul(2,4)', 'mul(5,5)', 'mul(11,8)', 'mul(8,5)']
```

> NOTE: We use `\(` instead of `(` because parens are special regex tokens and we want to literally match against the paren characters.

There are our 4 example `mul`s! But we'll have to do more parsing to get those integers out. What if there were a better way?

Luckily, regex supports "capture groups". These don't affect whether a pattern will match text or not, but help extract specific data from within a match. In our case, we only actually care about the numbers (as long as they're still within `mul()`), so we can add parenthesis around our `\d` tokens:

```py rem={5} ins={6}
...

class Solution(TextSolution):
    def part_1(self) -> int:
        mul_instructions = re.findall(r"mul\(\d{1,3},\d{1,3}\)", self.input)
        mul_instructions = re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", self.input)
        # => [('2', '4'), ('5', '5'), ('11', '8'), ('8', '5')]
```

`re.findall` returns inner capture groups instead of full matches if you supplied any which is convenient. From there, finishing part 1 is as easy as iterating over that list:

```py rem={5} ins={6-9}
...

class Solution(TextSolution):
    def part_1(self) -> int:
        mul_instructions = re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", self.input)
        return sum(
            int(l) * int(r)
            for l, r in re.findall(r"mul\((\d{1,3}),(\d{1,3})\)", self.input)
        )
```

If you want to dig into exactly how this regex works, there's an interactive example that explains every character: https://regex101.com/r/hE7CFK/1

## Part 2

For this part, finding the `mul`s is the same, but we have to ignore some of them. To do this, we'll tweak our regex to find those `do()` and `don't()` function calls as well.

The `|` regex token acts as an "or". So `(b|c)at` would match both `bat` and `cat`, but not `hat`.

> NOTE: that example uses parenthesis to group an expression, just like you would in other programming languages. Without them, you'd be matching against `b` or `cat`, which probably isn't what you want

In our case, we want to our regex from part 1, or either of those other function calls:

```py
...

class Solution(TextSolution):
    ...

    def part_2(self) -> int:
        instructions = re.finditer(
            r"mul\((\d{1,3}),(\d{1,3})\)|do\(\)|don't\(\)", self.input
        )
```

We're swapping from `re.findall` to `re.finditer` for part 2. `findall` _only_ returns capture groups (our integers). But for part 2 part, we also want to extract matches that don't have numbers (e.g. `do()`) so we know what mode we should be in.

`finditer` returns `Match` objects ([docs](https://docs.python.org/3/library/re.html#match-objects)) which hold more information about what exactly we found. Most useful is the `.group()` method, which takes any number of integers and returns the captured data at that index. The full matched text is at `0` and our captured groups are at `1` and `2` respectively. So the (updated) example input gives:

```py
('mul(2,4)', '2', '4')
("don't()", None, None)
('mul(5,5)', '5', '5')
('mul(11,8)', '11', '8')
('do()', None, None)
('mul(8,5)', '8', '5')
```

> NOTE: I'm not using `match.groups()` here, but it's worth mentioning that it (confusingly) behaves differently from `match.group(0, 1, 2)`. `.groups()` _only_ includes your capture groups while we're also interested in the full match data here. Which is useful to you in the future will depend on what data you're extracting.

From there, calculating our answer is simple:

```py
class Solution(TextSolution):
    ...

    def part_2(self) -> int:
        instructions = re.finditer(
            r"mul\((\d{1,3}),(\d{1,3})\)|do\(\)|don't\(\)", self.input
        )

        total = 0
        active = True
        for i in instructions:
            command, l, r = i.group(0, 1, 2)
            if command == "do()":
                active = True
            elif command == "don't()":
                active = False
            elif active:
                total += int(l) * int(r)
            else:
                # we hit mul but are inactive; skip!
                pass

        return total
```

Regex are an _extremely_ powerful tool to have in your toolbelt. We only touched the surface here, but I recommend getting comfortable reading and writing them. I bet it's not the last you'll see of regex this year!

Once again, there's a full explanation of the regex we used: https://regex101.com/r/4KusP8/1
