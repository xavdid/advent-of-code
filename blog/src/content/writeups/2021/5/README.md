---
year: 2021
day: 5
title: "Hydrothermal Venture"
slug: "2021/day/5"
pub_date: "2021-12-05"
---

## Part 1

While it may look like we need to reach for our grid from [yesterday](/writeups/2021/day/4/), it's not actually the case. Really we're just tracking segments, which are made of points (which are in turn an `(x, y)` pair. While it's not necessary, I have a feeling we'll thank ourselves later if we do the parsing and filtering with a lot of structure. Let's make some classes!

First is the `Point`. We could use a regular class, but we'll eventually want to use `Point` instances as keys in a dict. You can only do that with a user-defined class if you define some special methods (specifically `__eq__` and `__hash__`, so Python knows how to store and compare them).

But, we're not here to do extra work, let's let the language handle that for us. Enter one of my favorite Python classes, the `dataclass`. I've written about them [at length](https://xavd.id/blog/post/python-dataclasses-from-scratch/), but the gist is that they're a class that automatically creates a number of methods for you. And wouldn't you guess, they'll handle the aforementioned `__eq__` and `__hash__`! Here it is:

```py
from dataclasses import dataclass

@dataclass(frozen=True, eq=True)
class Point:
    x: int
    y: int
```

That's all it takes! The `__init__` function is also handled for us, so we'll be able to call `Point(1, 2)` like we'd expect. Truly :sparkles: magic.

Next is our `Segment`. Each should have a `start` and `stop`. This should look familiar:

```py
@dataclass
class Segment:
    start: Point
    stop: Point
```

Note that we didn't need the extra arguments to the `dataclass` decorator - we're not doing anything fancy with this class, so the defaults are fine.

Next is input parsing. We need a list of `Segment`s and a way to easily make `Points` from a string:

```py
class Point:
    ...

    @staticmethod
    def from_input(input_: str) -> "Point":
        x, y = input_.split(",")
        return Point(int(x), int(y))

...

segments: List[Segment] = []
for line in self.input:
    start, stop = line.split(" -> ")
    s = Segment(Point.from_input(start), Point.from_input(stop))
```

Because a dataclass's `__init__` takes only the attributes it expects (in this case, `(x, y)`, we want a little helper to turn `"1,2"` into a `Point`. That `staticmethod` is just that - a helper attached to a class (but bound to the class _itself_ not instances; note the lack of `self`).

At least for now, we only want to worry about the segments which are flat, so let's add a check for that:

```py
class Segment:
    ...

    @property
    def is_flat(self) -> bool:
        """
        Exactly vertical or horizontal
        """
        return self.start.x == self.stop.x or self.start.y == self.stop.y

for line in self.input:
    ...
    if s.is_flat:
        segments.append(s)
```

Now that we have the groundwork, it's time for the final touches to solve the puzzle. Ultimately, we need to count how many time we see each point and then return the number of points we see more than once. That sounds like a job for a `Counter`!

Before we get there though, we need a way to turn a `Segment` into a bunch of `Point`s. This code firmly falls into the category of "ugly, but it works":

```py
class Segment:
    ...

    @property
    def points(self) -> List[Point]:
        if self.start.x == self.stop.x:
            # vertical line
            low = min(self.start.y, self.stop.y)
            high = max(self.start.y, self.stop.y)
            return [Point(self.start.x, y) for y in range(low, high + 1)]

        # horizontal line
        low = min(self.start.x, self.stop.x)
        high = max(self.start.x, self.stop.x)
        return [Point(x, self.start.y) for x in range(low, high + 1)]
```

Note `high + 1`, since `range` doesn't include the end of the ragne.

Last is our counting:

```py
from collections import Counter

c = Counter()
for segment in segments:
    c.update(segment.points)

return len([v for v in c.values() if v > 1])
```

Because a `Counter` is actually a `dict`, all the methods we're used to using still work.

That's probably the most code we've written all week, but it's hopefully easy enough to follow. Onwards!

## Part 2

I had a feeing we were going to get to diagonals, and here we are. The good news is, we set our self up for success! There are only a couple of things we need to tweak.

First, we need an `is_diagonal` method. A quick trip to [StackExchange](https://math.stackexchange.com/questions/1194565/how-to-know-if-two-points-are-diagonally-aligned) reminds us that there's a simple formula:

```py
class Segment:
    ...

    @property
    def is_diagonal(self) -> bool:
        """
        Exactly a 45 degree angle
        """
        return abs(self.start.x - self.stop.x) == abs(self.start.y - self.stop.y)
```

Next, our `.points` property needs to account for diagonals. I've done some refactoring to help the code re-use. It's still a little verbose, but I'm happier with it now:

```py
class Segment:
    ...

    @property
    def points(self) -> List[Point]:
        x_min = min(self.start.x, self.stop.x)
        x_max = max(self.start.x, self.stop.x)
        x_vals = range(x_min, x_max + 1)

        y_min = min(self.start.y, self.stop.y)
        y_max = max(self.start.y, self.stop.y)
        y_vals = range(y_min, y_max + 1)

        if self.is_flat:
            if self.start.x == self.stop.x:
                return [Point(self.start.x, y) for y in y_vals]
            return [Point(x, self.start.y) for x in x_vals]

        if self.start.x > self.stop.x:
            x_vals = reversed(x_vals)

        if self.start.y > self.stop.y:
            y_vals = reversed(y_vals)

        return [Point(x, y) for x, y in zip(x_vals, y_vals)]
```

Nothing too surprising. The tough thing for me was working out the logic for the diagonal ranges when the `range` function doesn't handle `stop > start`. Zipping them together gives us the exact right number of steps, and in the right increments. It actually ended up pretty clean.

Lastly is our solve loop. We can do both parts in one swing here:

```py
# moved to a function
def num_repeated(c: Counter) -> int:
    return len([v for v in c.values() if v > 1])

for line in self.input:
    ...
    if s.is_flat or s.is_diagonal: # changed!
        segments.append(s)


part_1 = Counter()
part_2 = Counter()
for segment in segments:
    part_2.update(segment.points)
    if segment.is_flat:
        part_1.update(segment.points)

return num_repeated(part_1), num_repeated(part_2)
```

Part 2 counts every segment, while part 1 only counts the flat ones. That should do it!

Fun trivia - this is the first day where running my solution isn't instant on my computer (there's a very short but perceptible pause). I don't imagine this'll be the last time that happens.

---

Upon further reflection, this solution is more memory-heavy than it needs to be. Rather than store all the objects and then count all the objects, we can count as we go. The final loop could be changed to be:

```py
part_1 = Counter()
part_2 = Counter()

for line in self.input:
    start, stop = line.split(" -> ")
    s = Segment(Point.from_input(start), Point.from_input(stop))
    if s.is_flat:
        part_1.update(s.points)
        part_2.update(s.points)
    if s.is_diagonal:
        part_2.update(s.points)

return num_repeated(part_1), num_repeated(part_2)
```

I tested it and it ran... at the exact same speed. But it certainly used less memory. Doesn't seem like it's super easy to tell exactly [how much less](https://stackoverflow.com/questions/938733/total-memory-used-by-python-process), but we can feel a little better about ourselves.
