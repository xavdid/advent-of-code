# To ensure security, a valid passphrase must contain no duplicate words.

# For example:

# aa bb cc dd ee is valid.
# aa bb cc dd aa is not valid - the word aa appears more than once.
# aa bb cc dd aaa is valid - aa and aaa count as different words.
# The system's full passphrase list is available as your puzzle input. How many passphrases are valid?

# Part 2

# For added security, yet another system policy has been put in place. Now, a valid passphrase
# must contain no two words that are anagrams of each other - that is, a passphrase is invalid
# if any word's letters can be rearranged to form any other word in the passphrase.

# For example:

# abcde fghij is a valid passphrase.
# abcde xyz ecdab is not valid - the letters from the third word can be rearranged to form the first word.
# a ab abc abd abf abj is a valid passphrase, because all letters need to be used when forming another word.
# iiii oiii ooii oooi oooo is valid.
# oiii ioii iioi iiio is not valid - any of these words can be rearranged to form any other word.
# Under this new system policy, how many passphrases are valid?

from base import BaseSolution, InputTypes
from itertools import permutations


class Solution(BaseSolution):
    def input_type(self):
        return InputTypes.ARRAY

    def part_1(self):
        def unique(pw):
            return len(pw) == len(set(pw))

        return self.solve(unique)

    def part_2(self):
        def sans(arr, i):
            # return an array missing a single element
            if i < 0:
                raise ValueError('index must be positive, weird result otherwise')
            return arr[:i] + arr[(i + 1):]

        def anagram(pw):
            for i, phrase in enumerate(pw):
                anagrams = set([''.join(s) for s in permutations(phrase)])
                the_rest = set(sans(pw, i))
                if anagrams.intersection(the_rest):
                    return False
            return True

        return self.solve(anagram)

    def solve(self, f):
        total = 0
        for pw in self.input:
            pw = pw.split(' ')
            if f(pw):
                total += 1

        return total
