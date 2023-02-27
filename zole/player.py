from zole.cards import Cards

class PlayerRoles:
    NAV = ''
    LIELAIS = 'Lielais'
    ZOLE = 'Zole'
    MAZAZOLE = 'Mazā zole'
    MAZAIS = 'Mazais'
    GALDINS = 'Galdiņš'


class Player:
    def __init__(self, name: str):
        self.name = name
        self.points = 0
        self.next_player: Player = None

        #Party data
        self.hand = Cards(10)
        self.tricks_taken:int = 0
        self.tricks_score:int = 0
        self.role = PlayerRoles.NAV

    def handle_game_event(self, event: 'GameEvent'):
        pass

    def __repr__(self):
        return f'{self.name}'

    def clear_party_data(self):
        self.hand.clear()
        self.tricks_taken = 0
        self.tricks_score = 0
        self.role = PlayerRoles.NAV


class PlayerCircle:
    def __init__(self, first: Player, second: Player, third: Player):
        self.players = (first, second, third)

    def shift(self):
        return PlayerCircle(self.players[1], self.players[2], self.players[0])

    def shifts(self, count):
        res = self
        for i in range(count):
            res = res.shift()
        return res

    def index(self, player):
        # self.players.index(player)  # doesn't work for some reason
        if self.players[0] == player:
            return 0
        elif self.players[1] == player:
            return 1
        elif self.players[2] == player:
            return 2
        return -1

    def first(self):
        return self.players[0]

    def second(self):
        return self.players[1]

    def third(self):
        return self.players[2]

    def __getitem__(self, items):
        return self.players[items]

    def __iter__(self):
        return self.players.__iter__()

    def __next__(self):
        return self.players.__next__()

    def sit_players(first: Player, second: Player, third: Player) -> 'PlayerCircle':
        first.next_player = second
        second.next_player = third
        third.next_player = first
        return PlayerCircle(first, second, third)
