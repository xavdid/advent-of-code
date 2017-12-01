# The captcha requires you to review a sequence of digits (your puzzle input) and find the sum of all digits that match the next digit in the list. The list is circular, so the digit after the last digit is the first digit in the list.

# For example:

# 1122 produces a sum of 3 (1 + 2) because the first digit (1) matches the second digit and the third digit (2) matches the fourth digit.
# 1111 produces 4 because each digit (all 1) matches the next.
# 1234 produces 0 because no digit matches the next.
# 91212129 produces 9 because the only digit that matches the next one is the last digit, 9.

import os

with open(os.path.join(os.path.dirname(__file__), '../inputs/1.txt')) as file:
    captcha_input = file.read()

total = 0

for i, val in enumerate(captcha_input):
    # check the circular part of the last item
    if i == len(captcha_input) - 1:
        if val == captcha_input[0]:
            total += int(val)

    elif val == captcha_input[i + 1]:
        total += int(val)

print 'total is', total
