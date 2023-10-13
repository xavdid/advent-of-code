---
layout: "../layouts/Layout.astro"
---

# Welcome!

This site houses one of my favorite projects: my step-by-step [Advent of Code](https://adventofcode.com) explanations. They're written in [Python](https://www.python.org/) and use [my custom solution template](https://github.com/xavdid/advent-of-code-python-template) (which handles input parsing, mostly).

Continue reading to learn about the project, or head right over to [this year's writeups](/writeups/2022).

## About

[Advent of Code](https://adventofcode.com) is a programming-focused puzzle contest run every December by [Eric Wastl](http://was.tl/). The puzzles are imaginative and engaging; they're an absolute joy to complete. I've been solving them since 2017, but it wasn't until 2020, in an effort to make sure everyone at my then-job could complete the puzzles, that I started writing out an explanation to the day's puzzle. I adored this practice. Not only did it ensure I understood the problem (and my code) enough to communicate a solution, it helped me iterate on my code as I was forced to explain it.

Even now, my #1 advice to engineers looking to level up is this: do Advent of Code!

## Goals

My overall goal with AoC is to improve as an engineer and as a writer. To that end,

### Code Goals

1. My solution should work for all inputs without any hardcoded data or manual input required
2. My code should be clear and maintainable; the sort of code I'd like to find at work (practice makes perfect!).
3. My solution should produce a result in a reasonable amount of time. Generally I aim for "instantaneous", but many problems take ~2 seconds and a few take even longer. If it's more than about 10 seconds, I usually re-evaluate my approach.
4. Learn more about the StdLib. Python is chock-full of great functionality and I make sure to use it where possible. Knowing what tools are available makes me a much better Python programmer. As a result, I don't use external libraries; Python comes with [batteries included](https://en.wikipedia.org/wiki/Batteries_Included) and dang it, I'm gonna use them.

### Non-Goals

1. I'm not trying to get on the global leaderboard.
2. I don't always finish puzzles (& writeups) the day the puzzle is released. On earlier days I can get everything done quickly, but as December goes on, I get busy with work and family things. Plus, the harder puzzles & writeups take much longer than the easier ones. I'm usually done by the end of January, but it depends. I suggest following in the [RSS Feed](/feed.rss) to be notified when a new solution is ready.
3. I'm not trying to write the smallest, fastest, or cleverest code; see [code goals](#code-goals) above.
4. I don't solve every puzzle. As much as it pains me to admit it, I sometimes turn to Reddit for solution inspiration (or explanation). In these cases, I'll first understand someone else's solution in place of my own. I'll adapt it to be in line with code I'd write myself, and then write the explanation like normal (obviously crediting and linking to the original author). See [2022 day 22](/writeups/2022/day/22#part-2) for an example.

## Audience

These posts should be accessible to programmers of any skill level, but they're especially geared towards intermediate-level Python programmers. Readers are expected to be familiar with basic Python, such as:

- variables
- functions
- common Python data structures (`list`, `dict`, `set`, etc)
- loops & list comprehensions

Posts assume readers have read all the previous ones from that year, so I won't re-explain something I've already covered (though I may link back to it).

I _will_ typically explain more complex Python patterns, useful stdlib functions, and novel ways to approach the puzzle.

<!-- <pre>
~
├── <a href="/about">about</a>
├── <a href="/getting-started">getting-started</a>
└── <a href="/writeups">writeups</a>
    ├── <a href="/writeups/2022">2022</a>
    ├── <a href="/writeups/2021">2021</a>
    └── <a href="/writeups/2020">2020</a>
</pre> -->

---
