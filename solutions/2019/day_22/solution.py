# prompt: https://adventofcode.com/2019/day/22

from ...base import BaseSolution, InputTypes


class Deck:
    def __init__(self, deck_size) -> None:
        self.deck = list(range(deck_size))

    def new_stack(self):
        self.deck.reverse()

    def cut(self, num: int):
        self.deck = self.deck[num:] + self.deck[:num]

    def deal_with_increment(self, num: int):
        res = {}
        pos = 0
        for card in self.deck:
            res[pos] = card
            pos = (pos + num) % len(self.deck)

        self.deck = [res[x] for x in range(len(self.deck))]

    def handle_input(self, text: str):
        if text == "deal into new stack":
            self.new_stack()
        else:
            parts = text.split(" ")
            num = int(parts[-1])
            if parts[0] == "cut":
                self.cut(num)
            else:
                self.deal_with_increment(num)


class Solution(BaseSolution):
    _year = 2019
    _day = 22
    input_type = InputTypes.STRSPLIT

    def part_1(self):
        deck = Deck(10007)

        for text in self.input:
            deck.handle_input(text)

        return deck.deck.index(2019)

    def part_2(self):
        return
        deck = Deck(119315717514047)  # this causes an overflow, way too big

        for _ in range(101741582076661):
            for text in self.input:
                deck.handle_input(text)

        return deck.deck.index(2020)
