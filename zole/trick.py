from zole.cards import Cards, new_card_is_stronger


# Stich - eine Spielrunde bei verschiedenen Kartenspielen
class Trick:
    def __init__(self):
        self.cards = Cards(3)
        self.played_by = [None, None, None]
        self.top = 0

    def play_card(self, card, player):
        i = self.cards.size
        self.played_by[i] = player
        self.cards.add_card(card)
        if i > 0 and new_card_is_stronger(self.top_card(), card):
            self.top = i

    def first_card(self):
        return self.cards[0]

    def top_card(self):
        return self.cards[self.top]

    def __getitem__(self, key):
        return self.cards[key], self.played_by[key]

    def __len__(self):
        return self.cards.size

    def is_done(self):
        return self.cards.size == 3

    def score(self):
        sum = 0
        for card in self.cards:
            sum += card.score
        return sum

    def tacker(self):
        return self.played_by[self.top]

    def __repr__(self):
        return f'{self.cards[0]}, {self.cards[1]}, {self.cards[2]}'

