---
year: 2022
day: 7
title: "No Space Left On Device"
slug: "2022/day/7"
pub_date: "2022-12-07"
---

## Part 1

Welp, vacation's over. This looks intimidating, but it's not too bad once it's said and done.

The good news is that we'll get to use a feature I've wanted to try out since the final note in [2021 Day 2](https://github.com/xavdid/advent-of-code/blob/main/solutions/2021/day_02): [structural pattern matching](https://peps.python.org/pep-0636/)!

We don't know the shape of the filesystem, so we have to build it by reading our input. We'll build a deeply-nested dictionary that mirrors the structure. The thing I found trickiest was to maintain a pointer to our current directory _and_ its path. Eventually, I settled on a pair of variables that I'd keep in sync- not the most elegant approach, but it works.

We'll start with our basic filesystem, and an inner function to return a deeply-nested path:

```py
class Solution(StrSplitSolution):
    def parse_filesystem(self):
        filesystem = {"/": {}}
        current_path = []

        def get_dir() -> Dict:
            res = filesystem
            for segment in current_path:
                res = res[segment]
            return res

        current_dir = get_dir()
```

`current_path` is a list of strings that we'll push and pop directories into, while `current_dir` is the actual dictionary in `filesystem` that we're working in. Python variables that point to containers do so by reference, meaning anything that points to the same dict will modify the data that all variables share. This is the opposite of how primitives work (strings, ints, etc):

```py
# primitives
a = 1
b = a

# a is changed
a += 1

# b doesn't change
print(a) # 2
print(b) # 1

# ---

# containers
c = [1, 2, 3]
d = c

# c is changed
c.append(4)

# both c and d are updated, since they point to the same variable in memory
print(c) # [1, 2, 3, 4]
print(d) # [1, 2, 3, 4]
```

All that is to say, we can make modifications to `current_dir` and they'll get picked up wherever that `dict` lives in `filesystem`.

Next, we do the matching. For each line, we match the structure of the line and assign any variables we need:

```py
class Solution(StrSplitSolution):
    def parse_filesystem(self):
        filesystem = {"/": {}}

        ...

        for line in self.input:
            match line.split():
                case ["$", "ls"]:
                    continue
                case ["$", "cd", "/"]:
                    current_path = ["/"]
                    current_dir = filesystem["/"]
                case ["$", "cd", ".."]:
                    current_path.pop()
                    current_dir = get_dir()
                case ["$", "cd", new_dir]:
                    current_path.append(new_dir)
                    current_dir = get_dir()
                case ["dir", dir_name]:
                    current_dir[dir_name] = {}
                case [size, file_name]:
                    current_dir[file_name] = int(size)
                case _:
                    raise ValueError("unknown line shape")

        return filesystem
```

You should recognize the different types of lines in our input:

- `$ ls`: no action needed, since it doesn't change the filesystem map at all
- `$ cd /`: reset the `current_path` to the top and re-point `current_dir` at root manually
- `$ cd ..`: remove the last bit of the path and re-calculate our `current_dir` pointer
- `$ cd X`: add `X` to the end of the path and re-calculate `current_dir`
- `dir Y`: add a sub-dict under the current directory under its name
- `123 ABC`: add a file of size `123` in the current directory under its name
- a default case, so we know if we forgot a case. It getting silently ignored would lead to a tricky bug

This code was originally more defensive (making sure we didn't re-visit any directories, etc), but it turns out that wasn't necessary, so I pulled it. Run on the test input and we get:

```py
{
    "/": {
        "a": {
            "e": {
                "i": 584
            },
            "f": 29116,
            "g": 2557,
            "h.lst": 62596,
        },
        "b.txt": 14848514,
        "c.dat": 8504156,
        "d": {
            "d.ext": 5626152,
            "d.log": 8033020,
            "j": 4060174,
            "k": 7214296,
        },
    }
}
```

Which looks perfect!

Next, we need to roll up all the directory sizes. Whenever you're dealing with trees, [recursion](https://www.google.com/search?q=recursion) is useful. Remember the 2 rules:

1. always write a base case (that returns a value and does no further calculation)
2. otherwise, return a the function you're in with something different that it was called with before

Those in hand, we can write a recursive function to sum up all of the directories:

```py
class Solution(StrSplitSolution):
    ...

    directory_sizes: List[int] = []

    def calculate_directory_sizes(self, directory: Dict) -> int:
        total = 0
        for size_or_dir in directory.values():
            if isinstance(size_or_dir, int):
                total += size_or_dir
            else:
                subtotal = self.calculate_directory_sizes(size_or_dir)
                self.directory_sizes.append(subtotal)
                total += subtotal

        return total
```

Because we don't actually need to know _which_ directories correspond do which sizes when we're done (for either part; spoilers!) we'll just store the integer value in a list as we go.

Once we've run that, back in our main method, we can find `sum` the directories under the required size with a list comprehension:

```py
class Solution(StrSplitSolution):
    ...

    def part_1(self):
        filesystem = self.parse_filesystem()
        self.pp(filesystem)

        self.calculate_directory_sizes(filesystem)

        return sum([v for v in self.directory_sizes if v <= 100_000])
```

## Part 2

Now that we have a parsed tree and all of our filesizes, we need to do a little arithmetic and one more list comprehension. We'll also move our previous code into `solve`, since we'll solve both parts in 1 go:

```py
class Solution(StrSplitSolution):
    ...

    def calculate_unused_space(self) -> int:
        TOTAL_SPACE = 70_000_000
        SPACE_REQUIRED = 30_000_000

        unused_space = TOTAL_SPACE - self.directory_sizes[-1]  # the root directory
        return SPACE_REQUIRED - unused_space

    def solve(self) -> Tuple[int, int]:
        # part 1 code
        ...

        min_size = self.calculate_unused_space()
        smallest_directory_to_clear = min(
            [v for v in self.directory_sizes if v >= min_size]
        )

        #      part 1                   part 2
        return small_directories_total, smallest_directory_to_clear
```

`self.directory_sizes[-1]` works for getting the root because the recursive function won't store the size of the root directory until it's calculated everything else. So, root must be last.
