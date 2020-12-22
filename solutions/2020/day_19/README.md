# Day 19 (2020)

`Monster Messages` ([Prompt](https://adventofcode.com/2020/day/19))

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

Part 2 will come soonish! I'm taking these slow now that I'm on break. Thanks for your patience. :grin:
