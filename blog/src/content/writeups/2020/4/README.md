---
year: 2020
day: 4
title: "Passport Processing"
slug: "2020/day/4"
pub_date: "2020-12-04"
---

## Part 1

Off the bat, the core challenge here is breaking this disorganized input into its component keys.

Let's start by isolating each passport by splitting on empty lines:

```py
passports = self.input.split("\n\n")

['ecl:gry pid:860033327 eyr:2020 hcl:#fffffd\nbyr:1937 iyr:2017 cid:147 hgt:183cm', 'iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884\nhcl:#cfa07d byr:1929', 'hcl:#ae17e1 iyr:2013\neyr:2024\necl:brn pid:760753108 byr:1931\nhgt:179cm', 'hcl:#cfa07d eyr:2025 pid:166559648\niyr:2011 ecl:brn hgt:59in']
```

The real rub comes from the prompt:

> a sequence of key:value pairs separated by spaces or newlines

Having to work through that is an extra step, but is pretty doable. We'll want to store fields in a dict so that we can quickly check how many keys we have. We don't need values yet, but I'm guessing that for part 2, they'll become relevant.

<!-- this block has inline code with a leading space, which apparently prettier doesn't like -->
<!-- prettier-ignore -->
Rather than using the regular `string.split` method (which can only split on a single separator at a time), let's use `re.split`, which lets us use [regex](https://en.wikipedia.org/wiki/Regular_expression) to provide multiple separators at once. In our case, we want ` |\n`, aka "space or newline".

```py
import re
re.split(r' |\n', passport)

['ecl:gry', 'pid:860033327', 'eyr:2020', 'hcl:#fffffd', 'byr:1937', 'iyr:2017', 'cid:147', 'hgt:183cm']
```

From there, a list comprehension lets us build a list of the keys and values which can be piped right into `dict`.

```py
dict([s.split(":") for s in re.split(r" |\n", passport)])

{'ecl': 'gry', 'pid': '860033327', 'eyr': '2020', 'hcl': '#fffffd', 'byr': '1937', 'iyr': '2017', 'cid': '147', 'hgt': '183cm'}
```

From there, it's pretty easy to write rules for validity. It either needs:

- all 8 keys (`cid` is ignored, but that's fine)
- 7 keys and `cid` is the missing one

So for each cleaned passport:

```py
cleaned = flatten_passport(passport)
if len(cleaned) == 8 or (len(cleaned) == 7 and "cid" not in cleaned):
    num_valid += 1
```

This approach doesn't check that the 8 keys are the _correct_ ones, but that doesn't seem to be an issue. Looks like we can safely assume that if a key is present, it'll be one of the approved ones.

## Part 2

Ah yep, there's values validation!

Luckily, all the validation functions are pretty byte-sized. We can make a single little validator dict with python `lambda` functions. They're just like regular functions, but less syntax and restricted to a single expression:

```py
VALIDATORS = {
    'byr': lambda x: len(x) == 4 and 1920 <= int(x) <= 2002,
    ...
}

VALIDATORS['byr']('1991') # True
VALIDATORS['byr']('19910') # False
```

We can easily loop through these functions and fail passports that don't pass muster.

The validators mostly aren't super interesting, but there _are_ a couple of good regex in there:

matching hex values:

```py
lambda x: bool(re.match(r"#[0-9a-f]{6}", x)),
```

matching heights, which was the only one I couldn't reasonably fit in a lambda:

```py
def valid_height(x: str) -> bool:
    match = re.match(r"(\d{2,3})(cm|in)$", x)
    if not match:
        return False

    size, unit = match.groups()
    if unit == "cm":
        return 150 <= int(size) <= 193

    return 59 <= int(size) <= 76
```

And just like that, valid passports.
