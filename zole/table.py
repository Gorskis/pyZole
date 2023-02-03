from zole.cards import Cards
from zole.trick import Trick


class Table:
    def __init__(self):
        self.trick = Trick()
        self.community_cards = Cards(2)

    def clear(self):
        self.trick = Trick()
        self.community_cards.clear()
