---
year: 2020
day: 19
title: "Monster Messages"
slug: "2020/day/19"
pub_date: "2020-12-22"
---

## Part 1

This one looks a bit intimidating, but never fear. It's solved using techniques we're well familiar with at this point: RegEx and recursion.

Let's peek at the input. Each rule has both a key (`NUMBER:`) and a value, which is one of:

- a single letter in quotes: `"a"`
- space separated numbers: `1 2 3`
- 2 pair of numbers separated by a bar: `1 2 | 2 1`

We'll start by reading the input into a `dict` the key will the, well, they key. The value will be the raw rule. The only processing we'll do is to liberate the single characters for their extraneous quotes.

```py
self.rules = {}

for line in self.input.split("\n\n")[0].split("\n"):
    key, rule = line.split(": ")
    if '"' in rule:
        # single character
        rule = rule.strip('"')

    self.rules[key] = rule
```

Next we need to build a function that turns rule references into the actual contents of the rule. All rules eventually resolve to the letters (either `a` or `b`), so that'll be our base case. After that, we have to build our regex string (minus any spaces) which doesn't take much:

```py
@cache
def resolve_rules(self, key):
    if self.rules[key] in ("a", "b"):
        return self.rules[key]

    result = ""
    parts = self.rules[key].split(" ")
    for p in parts:
        result += "|" if p == "|" else self.resolve_rules(p)

    if "|" in result:
        result = f"({result})"

    return result
```

Once we've turned `1` into it's matching combination of `a`s and `b`s, we wrap it in parens to keep neighboring rules distinct. If we didn't, `a(aa|bb)b` would be read as `aaa|bbb`, which isn't the same. Note that we use our old friend `@cache` so we don't repeat work. Funnily enough, I tested it and there's no speed difference here with and without cache. I'm going to leave it though, to prevent me wondering down the line why I didn't cache the function.

Anyway, that out of the way, we can count the number of rules that match our string. We need to make sure to add bounds to our built regex so that a string that's too long doesn't match:

```py
rule_0 = self.resolve_rules("0")

return len(
    [
        message
        for message in self.input.split("\n\n")[1].split("\n")
        if re.match(f"^{rule_0}$", message)
    ]
)
```

## Part 2

Part of what we could rely on in part 1 was that `0` would always eventually resolve into a finite regex. That protection has been taken away in part 2. If we update the rules and run our part 1 solution without modifications, we get `RecursionError: maximum recursion depth exceeded in comparison`.

Turns out the Python regex engine doesn't handle recursion (though some other languages' engines do; each language has its own regex implementation). We need to modify our `resolve_rules` function to break the infinite recursion. Can we do this and still get the right answer? It turns out, yes! We don't need to recurse infinitely - just far enough that our final `rule_0` matches messages correctly.

Let's say we've got the rule `8: "a" | "a" 8`. As a regex, that would be `(a|a(a|a(a|a(...)))))` and so on. This gets very messy with the capture groups, but as long as the recursion level is deep enough, strings of a certain length will match it consistently. I'm not sure what exactly the math is here, but I did a bit of trial and error to prove my hunch. After 6 levels of recursion, the puzzle answer stopped changing, so that was the number I stuck with.

To implement this, special care is taken to track how many times we've recursed on our loop keys. A simple counter will do:

```py
num_loops = {"8": 0, "11": 0}  # detects loops

def resolve_rules(self, key):
    if key in self.num_loops:
        if self.num_loops[key] == 6:
            return ""
        self.num_loops[key] += 1
```

Once we've recursed 6 times, we can break and return `''`, which is a no-op when added to a string. Truth be told, that's the only serious change needed here! Note that we dropped the `@cache` because we _do_ need the answer to change the second time around. And like I said, no measurable performance benefit, so drop we did. After our rules are parsed as part of part 1, we just add this:

```py
self.rules["8"] = "42 | 42 8"
self.rules["11"] = "42 31 | 42 11 31"

rule_0 = self.resolve_rules("0")
part_2 = len(
    [message for message in messages if re.match(f"^{rule_0}$", message)]
)
```

As for the trial and error, the hardcoded 6 started as a 10. That was the correct answer on the site. Then, I tried each lower number until my code put out a different number (5 levels of recursion) and then stuck with that + 1 (6).
