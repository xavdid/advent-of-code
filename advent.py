#! /usr/bin/python

import sys

def main(day):
    solver = __import__('code.day_{}'.format(day), fromlist=['Solution']).Solution

    s = solver(day)
    s.print_solutions()

try:
    day_num = int(sys.argv[1])
    main(day_num)

except IndexError:
    print 'usage: advent <day>'
