from zole.game_session import GameSession
from zole.player import Player, PlayerCircle


class GameSessionFactory:
    def __init__(self):
        self.pc = 0
        self.players = [None, None, None]
        self.seed = None

    def add_player(self, player) -> GameSession:
        self.players[self.pc] = player
        self.pc += 1
        return player

    def set_seed(self, val: int):
        self.seed = val

    def make_session(self):
        players = PlayerCircle.sit_players(self.players[0], self.players[1], self.players[2])
        game_session = GameSession(players, self.seed)
        return game_session
