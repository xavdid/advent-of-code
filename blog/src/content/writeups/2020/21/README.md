---
year: 2020
day: 21
title: "Allergen Assessment"
slug: "2020/day/21"
pub_date: "2020-12-30"
---

## Part 1

If you're having trouble parsing this problem, don't worry - it's pretty confusing.

Each allergen is exactly one of the nonsense words and they are **not** always listed. Here's the example, but with simplified words so that we (as humans) can more easily read it:

```
A B C D (contains 1, 2)
E F G A (contains 1)
C F (contains 3)
C A G (contains 2)
```

We know that `A` must be `1` because it's the only ingredient that appears in both lines 1 and 2. `2` could be anything that's in both lines 1 and 4, so both `C` and `A` are potential allergens. `3` only appears once, so everything in that line are potentials allergens as well. All in all, `A, C, F` are the potential allergens. Let's code that up.

The input parsing is pretty straightforward. We'll be making liberal use of `set`s, since they're easy to get sums and differences for:

```py
translation = {}
safe_ingredients = set()
ingredients_lists: List[Set[str]] = []

for line in self.input:
    raw_ingredients, raw_allergens = line.rstrip(")").split(" (contains ")
    ingredient_set = set(raw_ingredients.split(" "))

    ingredients_lists.append(ingredient_set) # need this soon
    safe_ingredients.update(ingredient_set) # need this soon

    for allergen in raw_allergens.split(", "):
        if allergen in translation:
            translation[allergen] = translation[allergen] & ingredient_set
        else:
            translation[allergen] = ingredient_set
```

We might have used a `defaultdict` here for `translation`, but `set() & {1,2}` is always `set()`, so we need to only do the intersection with non-empty data. If we run the above on the example, we get:

```py
{
    'dairy': {'mxmxvkd'},
    'fish': {'sqjhc', 'mxmxvkd'},
    'soy': {'sqjhc', 'fvjkl'}
}
```

The prompt asks about the number of occurrences of the ingredients that _aren't_ in those sets. While we walk the list, we'll create a set (`safe_ingredients`) that has _all_ the ingredients and pull from it after that first pass:

```py
for line in self.input:
    ...

for unknown_allergen in possible_translations.values():
    safe_ingredients -= unknown_allergen
```

All that's left is to walk each ingredient set and count how many times safe ingredients appear.

```py
return sum(
    [len(ingredients & safe_ingredients) for ingredients in ingredients_lists]
)
```

## Part 2

Now we actually have to figure out which allergens map to which ingredients. This'll play out a lot like [day 16](/writeups/2020/day/16/#part-2). We start with any allergens that map to a single ingredient (like `A` in the cleaned example above), then remove that one from all other places it's a potential. We keep doing that until all the potential values are empty.

The only tricky thing here is that we have to take care to not modify the size of the dict as we're iterating through it. Instead, we consume the generator before iterating through it, which looks a little unusual:

```py
found_allergens = {}
while possible_translations:
    # consume the generator before we start walking
    for allergen, ingredients in list(
        (k, v) for k, v in possible_translations.items() if len(v) == 1
    ):
        found_ingredient = ingredients.pop()
        found_allergens[allergen] = found_ingredient
        del possible_translations[allergen]
        # remove the ingredient from contention in any remaining unknowns
        for a in possible_translations:
            possible_translations[a].discard(found_ingredient)

return ",".join(v for _, v in sorted(found_allergens.items()))
```
