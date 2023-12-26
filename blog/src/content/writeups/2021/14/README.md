---
year: 2021
day: 14
title: "Extended Polymerization"
slug: "2021/day/14"
pub_date: "2021-12-17"
---

## Part 1

Nothing too wild here. We're parsing our input and storing it in a `dict` that maps pairs to their output. Then we're looping to do the specified replacements. We can use the `zip` trick from [day 1](/writeups/2021/day/1/) to get our pairs. Then we use a `Counter` to get our totals. Nice and straightforward!

```py
from collections import Counter
from typing import Dict, Tuple

chain = list(self.input[0])
formula: Dict[Tuple, str] = {}
for line in self.input[2:]:
    inp, out = line.split(" -> ")
    formula[tuple(inp)] = out

for _ in range(10):
    next_chain = []
    for (l, r) in zip(chain, chain[1:]):
        next_chain += [l, formula[(l, r)]]
    next_chain.append(chain[-1])
    chain = next_chain

c = Counter(chain)
return c.most_common(1)[0][1] - c.most_common()[-1][1]
```

## Part 2

Alas, bumping our loop up to `40` times the whole thing out. We'll have to rethink how we're calculating the output. We should have know as soon as we saw the counts in example (whenever you have `2192039569602` of something, it's not easy to store). Unhelpfully, the profiler isn't showing any specific slow functions. I'd imagine iterating over such a long array is what's doing it.

I sat on the problem a bit and looked for other ways to approach the data. I spent some time looking for patterns- if there were cycles, we might be able to math our way out of this. No luck there; there _are_ some cycles (`NC` -> `NBC` -> `NBBBC`), but I couldn't figure out a way to make that useful.

The big breakthrough was realizing we don't care about the order of the input, just the frequency of the pairs. Instead of iterating through the whole list and potentially repeating a lot of work, we can perform the transform once by removing the input (`NC`) and incrementing the products by that much (`NB` & `BC`). Keeping individual counts also isn't too bad - letters are never removed, so I just need to count the number of times the new letter is added. Here's how that looks:

```py
# same input parsing as before
...

# initial values
def _solve(self, steps: int) -> int:
    chain = Counter(zip(self.input[0], self.input[0][1:]))
    counts = Counter(self.input[0])

    for _ in range(steps):
        # list() so we can modify `chain` as we go
        for (l, r), num in list(chain.items()):
            # there will be some 0s, we can skip those
            if not num:
                continue

            # NN: 1 gets broken up into NC and CN
            chain[(l, r)] -= num
            out = formula[(l, r)]

            chain[(l, out)] += num
            chain[(out, r)] += num

            # there are still only 2 Ns, and C was only actually added once (even though it appears in two pairs)
            counts[out] += num

    # faster to use max() than counter.most_common, since we don't care about the rest of the values being sorted
    return max(counts.values()) - min(counts.values())
```

What stumped me for a good bit ended up being pretty straightforward in the end!
