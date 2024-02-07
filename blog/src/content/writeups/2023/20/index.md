---
year: 2023
day: 20
slug: 2023/day/20
title: "Pulse Propagation"
concepts: [oop]
# pub_date: "TBD"
---

## Part 1

Today we're tracking signals through modules in a big computer. We'll be tracking the signals sent and adjusting state accordingly. This design immediately screamed [Object Oriented Programming](https://en.wikipedia.org/wiki/Object-oriented_programming), since we can have a base `Module` to implement shared properties and child classes which handle the different module types. Let's talk through our overall design and then dig into the actual implementations.

We'll need 2 modules: `FlipFlopModule` and `ConjunctionModule`. They'll each have a `send` method which takes information about the received pulse and returns a list of new pulses to send. A pulse will be a 3-tuple of `from, is_high_pulse, to`, describing the two involved modules and the low/high status (like the diagram in the prompt).

The logic for the modules themselves is quite straightforward. We'll start with the base class:

```py
from dataclasses import dataclass

# from, high pulse?, to
Pulse = tuple[str, bool, str]


@dataclass
class BaseModule:
    name: str
    targets: list[str]

    def build_pulses(self, is_high_pulse: bool) -> list[Pulse]:
        return [(self.name, is_high_pulse, t) for t in self.targets]

    def send(self, source: str, is_high_pulse: bool) -> list[Pulse]:
        raise NotImplementedError()

    def store_sources(self, sources: list[str]):
        raise NotImplementedError()
```

Because we want methods that interact with modules to take a `BaseModule` as their argument, it's useful to define all the methods a descendant class _could_ implement (even if it raises a runtime error when called).

Our first real module is the `FlipFlopModule`, which tracks an internal `state` and only broadcasts on low pulses. That code is straightforward:

```py
...

class FlipFlopModule(BaseModule):
    state = False

    def send(self, _: str, is_high_pulse: bool) -> list[Pulse]:
        # high pulses are ignored
        if is_high_pulse:
            return []

        # otherwise, invert and send new state pulse to all targets
        self.state = not self.state

        return self.build_pulses(self.state)
```

Note that we didn't redefine `store_sources`, so that'll be an unexpected error if it ever gets called (which is fine).

Next is the `ConjunctionModule`. It has to know all the modules that send _to_ it. Unfortunately, we can't do this lazily, since a single high pulse would make it remember `high` for "every" input, triggering it incorrectly. Instead, we'll have to do a couple of passes on the parsing; we'll get to that soon. In the meantime, here's the code to register those sources and send pulses:

```py
class ConjunctionModule(BaseModule):
    _sources: dict[str, bool] = {}

    def send(self, source: str, is_high_pulse: bool) -> list[Pulse]:
        self._sources[source] = is_high_pulse

        # if all high, send low
        # else, high
        to_send = not all(self._sources.values())

        return self.build_pulses(to_send)

    def register_sources(self, sources: list[str]):
        if self._sources:
            raise ValueError("already registered sources!")
        self._sources = {s: False for s in sources}
```

Finally, we're ready to parse the input. My approach does 3 passes, which I'm not super pleased with. Unfortunately, I needed to pre-identify each of the conjunction modules so I could identify which modules are pointed at them. So, let's see the three passes. We'll be building a new class to house all the business logic:

```py
...

class Computer:
    def __init__(self, lines: list[str]) -> None:
        # first pass: identify conjunction modules and initialize an empty array of what points at them
        conj_modules = {
            line.split(" ")[0][1:]: [] for line in lines if line.startswith("&")
        }
```

A little terse, but simple enough. Now before parsing any actual modules, we know which ones will be conjunction type.

Next, we'll actually initialize all our classes in a `dict`:

```py
...

class Computer:
    modules: dict[str, BaseModule] = {}

    def __init__(self, lines: list[str]) -> None:
        ...

        # second pass: generate and store BaseModule classes
        for line in lines:
            raw_source, raw_target = line.split(" -> ")
            source = raw_source[1:]
            targets = raw_target.split(", ")

            for t in targets:
                if t in conj_modules:
                    conj_modules[t].append(source)

            if raw_source == "broadcaster":
                self.initial_targets = targets
            if raw_source.startswith("%"):
                self.modules[source] = FlipFlopModule(source, targets)
            if raw_source.startswith("&"):
                self.modules[source] = ConjunctionModule(source, targets)
```

Crucially, we're telling each conjunction module which modules (of any type) point at it. This becomes vital for the third pass, where we register those sources:

```py
...

class Computer:
    ...

    def __init__(self, lines: list[str]) -> None:
        ...

        # third pass: update existing conjunction module with their sources
        for k, v in conj_modules.items():
            self.modules[k].register_sources(v)
```

Now those modules will correctly handle pulses because they have their full input list.

Next, we push the button! We're building a queue that each mode will add to. We also have to track the counts of our low and high pulses. Luckily, Python's got built-in classes to make short work of both of these: `collections.deque` and `collections.Counter`. The `deque` allows fast pushing and popping from both sides of the list, which is vital for queue-like behavior. `Counter`s can be added together, so we can track each pulse type separately, but in a single variable (which will be useful in just a sec). In the meantime, here's our `push_button` method:

```py
...

class Computer:
    ...

    def push_button(self) -> Counter:
        queue: deque[Pulse] = deque(
            ("broadcaster", False, t) for t in self.initial_targets
        )

        # False starts at 1 for button -> broadcaster
        pulse_counts = Counter({False: 1})

        while queue:
            source, pulse, target = queue.popleft()
            pulse_counts[pulse] += 1

            # ignore writing to `rx` or `output`
            if target not in self.modules:
                continue

            queue += self.modules[target].send(source, pulse)

        return pulse_counts
```

Modules can return any number of new states from their `send` method (including 0), which all plays nicely with the `deque`. The method won't return until every pulse is resolved, which is what the spec requires.

All that remains is to push the button 1000 times! And because we're using a `Counter`, which can be added to itself, we can write this very concisely:

```py
...

class Computer:
    ...

    def run(self):
        totals = sum((self.push_button() for _ in range(1000)), Counter())

        return totals[False] * totals[True]
```

This takes advantage of a new-to-me fact: `sum` can take a `start` parameter! Without it, we get a fairly cryptic type error:

```py
from collections import Counter

a = Counter({"a": 1, "b": 2})
b = Counter({"b": 2, "c": 3})
a + b  # Counter({'b': 4, 'c': 3, 'a': 1})

# 🤔
sum([a, b]) # TypeError: unsupported operand type(s) for +: 'int' and 'Counter'

# 💡
sum([a, b], Counter())  # Counter({'b': 4, 'c': 3, 'a': 1})
```

That's because `sum` assumes it's adding numbers, so `start` is `0` by default. If we're adding anything else, we should seed it with that type.

And just like that, we have our totals! Returning those gives us our answer:

```py
...

class Solution(StrSplitSolution):
    def part_1(self) -> int:
        return Computer(self.input).run()
```

## Part 2

I spent some non-trivial time in part 1 expecting to have to find a loop in the input. Well, quickly had to tear that all out when it became apparent that a loop (for the full state) didn't exist in any reasonable time.
