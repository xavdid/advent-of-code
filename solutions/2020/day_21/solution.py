# prompt: https://adventofcode.com/2020/day/21

from typing import Dict, List, Set, Tuple

from ...base import BaseSolution, InputTypes


class Solution(BaseSolution):
    _year = 2020
    _number = 21
    input_type = InputTypes.STRSPLIT

    def solve(self) -> Tuple[int, str]:
        possible_translations: Dict[str, Set[str]] = {}
        safe_ingredients = set()
        ingredients_lists: List[Set[str]] = []

        for line in self.input:
            raw_ingredients, raw_allergens = line.rstrip(")").split(" (contains ")
            ingredient_set = set(raw_ingredients.split(" "))

            ingredients_lists.append(ingredient_set)
            safe_ingredients.update(ingredient_set)

            for allergen in raw_allergens.split(", "):
                if allergen in possible_translations:
                    possible_translations[allergen] = (
                        possible_translations[allergen] & ingredient_set
                    )
                else:
                    possible_translations[allergen] = ingredient_set

        for unknown_allergen in possible_translations.values():
            safe_ingredients -= unknown_allergen

        total_safe_occurances = sum(
            [len(ingredients & safe_ingredients) for ingredients in ingredients_lists]
        )

        # part 2
        found_allergens = {}
        while possible_translations:
            # consume the generator before we start walking
            for allergen, ingredients in list(
                (k, v) for k, v in possible_translations.items() if len(v) == 1
            ):
                found_ingredient = ingredients.pop()
                found_allergens[allergen] = found_ingredient
                del possible_translations[allergen]
                for a in possible_translations:
                    possible_translations[a].discard(found_ingredient)

        bad_ingredients = ",".join(v for _, v in sorted(found_allergens.items()))

        answers = total_safe_occurances, bad_ingredients
        assert answers == (2230, "qqskn,ccvnlbp,tcm,jnqcd,qjqb,xjqd,xhzr,cjxv")
        return answers
