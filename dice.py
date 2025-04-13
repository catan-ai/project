# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

import collections
import itertools
from random import randint

class Dice(object):

    def __init__(self, number=2, sides=6):
        self.number = number
        self.sides = sides
        self.odds = self.set_odds()

    def set_odds(self):
        combinations = itertools.product(range(self.sides), repeat=self.number)
        combinations = [ 
                [ x+1 for x in possibile] 
                for possibile in combinations
        ]
        total_amt = len(combinations)
        possible_counts = collections.Counter([ sum(possible) for possible in combinations])
        return {
                number: amt * 1.0 / total_amt
                for number, amt in possible_counts.items()
                }

    def get_odds(self, number):
        return self.odds.get(number)

    def roll(self):
        return [randint(1,self.sides) for i in range(self.number)]


