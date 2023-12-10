## About

[Advent of Code](https://adventofcode.com) is a programming-focused puzzle contest run every December by [Eric Wastl](http://was.tl/). The puzzles are imaginative and engaging; there's nothing quite like them.

I've been solving portions of Advent of Code since 2017 but I've only been writing solutions since 2020. At the time, I was a mentor in Zapier's _Path Into Engineering_ program. In an effort to ensure everyone (regardless of their programming experience) could solve the puzzles, I started writing full explanations for every puzzle that anyone familiar with Python could follow.

I adored this routine. Not only did it ensure I understood the problem (and my code) enough to communicate a solution, it helped me iterate on my code as I was forced to explain it. It turns out that being able to explain your code is an important skill in software engineering. Who would have guessed!

### Mentoring

Even today, I prefer to work AoC problems with mentees than find tasks in our actual codebase. It gives them a chance to get to the essence of software engineering immediately (rather than wading through the complexity of a large codebase). These puzzles give a finite, constrained space for growing engineers to practice:

- writing readable code
- breaking down a problem
- learning and applying classic CS concepts
- and more!

Best of all, we can revisit their old solutions to let them practice reading old code that they now have to fix or improve. It really is a microcosm of software engineering.

## Audience

These posts should be accessible to programmers of any skill level, but they're especially geared towards intermediate-level Python programmers. Readers are expected to be familiar with basic Python, such as:

- variables
- functions
- common Python data structures (`list`, `dict`, `set`, etc)
- loops & list comprehensions

Posts assume readers have read all the previous ones from that year, so I won't re-explain something I've already covered (though I may link back to it).

I _will_ typically explain more complex Python patterns, useful stdlib functions, and novel ways to approach the puzzle.

## Methodology

Typically I'll solve part 1 and write its half of the post before solving and writing part 2. This helps me write the same way other solvers will read- doing part 1 without knowing what part 2 is.

Sometimes, I'll go back and clean up the part 1 solution or post to serve part 2 better. It may make the whole thing look like I totally knew what I was doing the whole time, but don't let me mislead you - I don't.

Occasionally I don't know how to solve a day. In that case, I take to the [subreddit](https://old.reddit.com/r/adventofcode/) and find a solution I can understand. Then I walk through that solution like a regular post (with attribution) so I make sure I know how it works (and you can too!).

## Goals

My overall goal with AoC is to improve as an engineer and as a writer. To that end, I try to write the code I'd like to read at work. It should be clear, maintainable, and at least a little documented; practice makes perfect, after all! When writing solutions, I keep a few overall goals in mind.

1. My solution should work for all inputs without any hardcoded data or manual input required.
2. My solution should produce a result in a reasonable amount of time. Generally I aim for "instantaneous", but many problems take ~2 seconds and a few take even longer. If it's more than about 10 seconds, I usually re-evaluate my approach.
3. Learn more about the Python stdlib. Python is chock-full of great functionality and I make sure to use it where possible. Knowing what tools are available makes me a much better Python programmer. To this end, I don't use any external libraries; Python comes with [batteries included](https://en.wikipedia.org/wiki/Batteries_Included) and dang it, I'm gonna use them.

### Non-Goals

1. I'm not trying to get on the global leaderboard.
2. I don't always finish puzzles (& writeups) the day the puzzle is released. On earlier days I can get everything done quickly, but as December goes on, I get busy with work and family things. Plus, the harder puzzles & writeups take much longer than the easier ones. I'm usually done by the end of January, but it depends. I suggest following in the [RSS Feed](/feed.rss) to be notified when a new solution is ready.
3. I'm not trying to write the smallest, fastest, or cleverest code.
4. I don't solve every puzzle. As much as it pains me to admit it, I sometimes turn to Reddit for solution inspiration (or explanation). In these cases, I'll first understand someone else's solution in place of my own. I'll adapt it to be in line with code I'd write myself, and then write the explanation like normal (obviously crediting and linking to the original author). See [2022 Day 22](/writeups/2022/day/22#part-2) for an example.
