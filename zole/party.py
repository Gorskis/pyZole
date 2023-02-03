from typing import List

from zole.game_modes import GameMode
from zole.player import Player, PlayerCircle, PlayerRoles
from zole.score_chart import set_points
from zole.table import Table
from zole.trick import Trick


class PlayerResult:
    def __init__(self, player: Player, has_won: bool, score_change: int):
        self.player = player
        self.has_won = has_won
        self.score_change = score_change

    def __repr__(self):
        return f'{self.player.name}: {"Won" if self.has_won else "lost"}, score: {self.score_change if self.score_change<0 else "+"+str(self.score_change)}'

class PartyResults:
    def __init__(self, party: 'Party'):
        self.party = party
        self.lielais_won: bool = None
        self.player_results = (
            PlayerResult(self.party.players.first(), False, 0),
            PlayerResult(self.party.players.second(), False, 0),
            PlayerResult(self.party.players.third(), False, 0)
        )

    def __repr__(self):
        return f'End of party({self.party.game_mode}, first:{self.party.first_hand}, lielais={self.party.lielais.name}:{self.party.lielais.tricks_score}) > {"Lielais won" if self.lielais_won else "mazais/ie won"}, {self.player_results[0]}, {self.player_results[1]}, {self.player_results[2]}'

class Party:
    def __init__(self, players: PlayerCircle):
        self.game_mode = GameMode.NOTSET
        self.players = players
        self.first_hand = self.players.first()
        self.tricks: List[Trick] = []
        self.active_player = self.first_hand
        self.lielais: Player = None  # Lielais, lielais Zolē vai mazā zolē
        self.table = Table()

    def next_party(self) -> 'Party':
        return Party(self.players.shift())

    def resolve_trick(self) -> Trick:
        last_trick = self.table.trick
        self.tricks.append(last_trick)
        self.table.clear()
        tacker: Player = last_trick.tacker()
        tacker.tricks_taken += 1
        tacker.tricks_score += last_trick.score()
        self.active_player = tacker
        return last_trick

    def player_relative_position(self, player: Player):  # 0-first hand, 1-2nd, 2-3rd
        return self.players.index(player)

    def resolve_game_mode(self, player: Player, game_mode: GameMode):
        self.game_mode = game_mode
        self.lielais = player
        if self.lielais:
            for player in self.players:
                if player != self.lielais:
                    player.role = PlayerRoles.MAZAIS
            if self.game_mode == GameMode.PACELT:
                self.lielais.role = PlayerRoles.LIELAIS
            elif self.game_mode == GameMode.ZOLE:
                self.lielais.role = PlayerRoles.ZOLE
            elif self.game_mode == GameMode.MAZAZOLE:
                self.lielais.role = PlayerRoles.MAZAZOLE
        else:
            for player in self.players:
                player.role = PlayerRoles.GALDINS

    def score_party(self) -> PartyResults:
        results = PartyResults(self)
        if self.game_mode == GameMode.PACELT:
            self.lielais.tricks_score += self.table.community_cards[0].score
            self.lielais.tricks_score += self.table.community_cards[1].score

        results = set_points(self.game_mode, results)
        for player_res in results.player_results:
            player_res.player.points += player_res.score_change

        return results
