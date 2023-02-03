class Card:
    def __init__(self, i: int, suit: str, rank: str, score: int, is_trump: bool):
        self.i = i
        self.suit = suit
        self.rank = rank
        self.score = score
        self.is_trump = is_trump
        # Visualization
        self.image = None

    def __repr__(self):
        return self.suit + self.rank

    def is_club(self):
        return self.suit == '♣'

    def is_spade(self):
        return self.suit == '♠'

    def is_heart(self):
        return self.suit == '♥'

    def is_diamond(self):
        return self.suit == '♦'


# ♣♠♥♦
all_cards = (
    Card(0, '♣', 'Q', 3, True),
    Card(1, '♠', 'Q', 3, True),
    Card(2, '♥', 'Q', 3, True),
    Card(3, '♦', 'Q', 3, True),
    Card(4, '♣', 'J', 2, True),
    Card(5, '♠', 'J', 2, True),
    Card(6, '♥', 'J', 2, True),
    Card(7, '♦', 'J', 2, True),
    Card(8, '♦', 'A', 11, True),
    Card(9, '♦', '10', 10, True),
    Card(10, '♦', 'K', 4, True),
    Card(11, '♦', '9', 0, True),
    Card(12, '♦', '8', 0, True),
    Card(13, '♦', '7', 0, True),
    Card(14, '♣', 'A', 11, False),
    Card(15, '♣', '10', 10, False),
    Card(16, '♣', 'K', 4, False),
    Card(17, '♣', '9', 0, False),
    Card(18, '♠', 'A', 11, False),
    Card(19, '♠', '10', 10, False),
    Card(20, '♠', 'K', 4, False),
    Card(21, '♠', '9', 0, False),
    Card(22, '♥', 'A', 11, False),
    Card(23, '♥', '10', 10, False),
    Card(24, '♥', 'K', 4, False),
    Card(25, '♥', '9', 0, False)
)
no_card = Card(999, '_', '_', 0, False)


class Cards:
    def __init__(self, max_size: int):
        self.cards = [no_card]*max_size
        self.size = 0
        self.n = 0  # for iterator

    def clear(self):
        self.size = 0
        for i in range(len(self.cards)):
            self.cards[i] = no_card

    def __getitem__(self, key):
        return self.cards[key]

    def __len__(self):
        return self.size

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.size:
            self.n += 1
            return self.cards[self.n-1]
        else:
            raise StopIteration

    def has_cards(self):
        return self.size > 0

    def add_card(self, card: Card):
        try:
            self.cards[self.size] = card
        except:
            Exception(f'ERROR index out of bounds for cards object {self} and adding {card}')
        self.size += 1

    def add_cards(self, cards: 'Cards'):
        for ci in range(len(cards)):
            self.add_card(cards[ci])

    def take_all_cards_from(self, cards: 'Cards'):
        self.add_cards(cards)
        cards.clear()

    def remove_card(self, card: Card):
        found_at: int = -1
        for i in range(self.size):
            if self.cards[i] == card:
                found_at = i
                break
        if found_at == -1:
            return False
        for j in range(found_at, self.size-1):
            self.cards[j] = self.cards[j + 1]
        self.cards[self.size-1] = no_card
        self.size -= 1
        return True

    def copy(self):
        c = Cards(len(self.cards))
        c.size = self.size
        for ci in range(self.size):
            c.cards[ci] = self.cards[ci]
        return c

    def get_valid_cards(self, first_card: Card):
        if first_card == no_card:
            return self.copy()
        valid_cards = Cards(8)
        if first_card.is_trump:
            for card in self.cards:
                if card.is_trump:
                    valid_cards.add_card(card)
        else:  # first card is not a trump
            for card in self.cards:
                if card.suit == first_card.suit and not card.is_trump:
                    valid_cards.add_card(card)
        if valid_cards.has_cards():
            return valid_cards
        else:
            return self.copy()

    def sort(self):
        for j in range(1, len(self.cards)):
            for i in range(len(self.cards) - j):
                if self.cards[i].i > self.cards[i + 1].i:
                    c = self.cards[i]
                    self.cards[i] = self.cards[i + 1]
                    self.cards[i + 1] = c

    def __repr__(self):
        if self.size > 0:
            s = '[' + str(self.cards[0])
            for ci in range(1, self.size):
                s += ','+str(self.cards[ci])
            return s+']'
        else:
            return '[]'
