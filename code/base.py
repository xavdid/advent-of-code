# Base class for other solutions
import os

class BaseSolution(object):
    def __init__(self, number):
        self.number = number
        self.input = self.read_input()

    def read_input(self):
        with open(os.path.join(os.path.dirname(__file__), '../inputs/{}.txt'.format(self.number))) as file:
            return file.read()

    def print_solutions(self):
        print '= Solutions for Day {}'.format(self.number)
        for i in [1, 2, 3]:
            if hasattr(self, 'part_{}'.format(i)):
                print '\n== Part {}'.format(i)
                sol_func = getattr(self, 'part_{}'.format(i))
                print '=== {}'.format(sol_func())
