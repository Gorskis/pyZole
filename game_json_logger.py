from datetime import datetime
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import json

from zole.game_session import GameSession


class JSONPlayer:
    def __init__(self):
        self.chips_change = -1
        self.cards_dealt = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.tricks_count = -1
        self.tricks_points = -1
        self.tricks = []  # list of tricks [card.i, card.i, card.i] taken by player

    def as_json(self):
        return {
            "chips_change": self.chips_change,
            "cards_dealt": self.cards_dealt,
            "tricks_count": self.tricks_count,
            "tricks_points": self.tricks_points,
            "tricks": self.tricks
        }


class JSONTrick:
    def __init__(self):
        self.position = -1  # Who won the trick
        self.trick = [[-1, -1], [-1, -1], [-1, -1]]  # 3 tricks of PlayerCircle.index(player) and card.i

    def as_json(self):
        return {
            "position": self.position,
            "trick": self.trick
        }

class JSONBoard:
    def __init__(self):
        self.dealer = -1  #Party#PlayerCircle.index(player.next_player.next_player)
        self.cards_dealt = [-1, -1]  # Cards on table
        self.tricks = []  # List of 8 JSONTrick objects

    def as_json(self):
        return {
            "dealer": self.dealer,
            "cards_dealt": self.cards_dealt,
            "tricks": [trick.as_json() for trick in self.tricks]
        }


class JSONGame:
    def __init__(self):
        self.board = JSONBoard()
        self.players = [JSONPlayer(), JSONPlayer(), JSONPlayer()]
        self.type = ''  # t - ņemt galdu; d - galds; b - zole; s - mazā
        self.type_user = -1  # lielais*

    def as_json(self):
        return {
            "board": self.board.as_json(),
            "players": [player.as_json() for player in self.players],
            "type": self.type,
            "type_user": self.type_user
        }


class JSONGameMeta:
    def __init__(self):
        self.table_id = -1
        self.game_points = [0, 0, 0]  # New Points assigned after party end, based on player index
        self.game = JSONGame()

    def as_json(self):
        return {
            "table_id": self.table_id,
            "game_points": self.game_points,
            "game": self.game.as_json()
        }


class JSONLog:
    def __init__(self):
        self.gamelist = []

    def as_json(self):
        return {
            "gamelist": [game_meta.as_json() for game_meta in self.gamelist]
        }


class GameJSONLogger:
    def __init__(self, session: GameSession):
        self.session = session
        now = str(datetime.now())[:19].replace(':', '')
        self.file = None
        self.file = open(f'./logs/log-{now}.json', 'w', encoding="utf-8")
        self.game_log = JSONLog()
        self.current_game_meta: JSONGameMeta = None


    def log(self, game_event: GameEvent):
        if game_event.name == EventNames.SessionStartedEvent:
            pass
        elif game_event.name == EventNames.PartyStartedEvent:
            self.current_game_meta = JSONGameMeta()
            party = game_event.party
            dealer = party.first_hand.next_player.next_player
            self.current_game_meta.game.board.dealer = self.session.players.index(dealer)
            table_cards = party.table.community_cards
            self.current_game_meta.game.board.cards_dealt = table_cards.as_index_array()
            for pi in range(3):
                player = self.session.players[pi]
                hand = player.hand.as_index_array()
                self.current_game_meta.game.players[pi].cards_dealt = hand

        elif game_event.name == EventNames.SelectGameModeEvent:
            pass
        elif game_event.name == EventNames.GameModeSelectedEvent:
            lielais_i = self.session.players.index(game_event.player)
            self.current_game_meta.game.type_user = lielais_i
            if game_event.selected_game_mode == GameMode.PACELT:
                self.current_game_meta.game.type = 't'
                self.current_game_meta.game.players[lielais_i].tricks.append(self.current_game_meta.game.board.cards_dealt)
            elif game_event.selected_game_mode == GameMode.GALDINS:
                self.current_game_meta.game.type = 'd'
            elif game_event.selected_game_mode == GameMode.ZOLE:
                self.current_game_meta.game.type = 'b'
            elif game_event.selected_game_mode == GameMode.MAZAZOLE:
                self.current_game_meta.game.type = 's'
            else:
                self.current_game_meta.game.type = str(game_event.selected_game_mode)

        elif game_event.name == EventNames.CardPickUpEvent:
            pass
        elif game_event.name == EventNames.DiscardCardsEvent:
            pass
        elif game_event.name == EventNames.CardsDiscardedEvent:
            pass
        elif game_event.name == EventNames.TrickStartedEvent:
            pass
        elif game_event.name == EventNames.PlayCardEvent:
            pass
        elif game_event.name == EventNames.CardPlayedEvent:
            pass
        elif game_event.name == EventNames.TrickEndedEvent:
            jtrick = JSONTrick()
            ti = 0
            trick_arr = [-1, -1, -1]
            for card, player in game_event.trick:
                jtrick.trick[ti] = [self.session.players.index(player), card.i]
                trick_arr[ti] = card.i
                ti += 1
            taker_i = self.session.players.index(game_event.trick.tacker())
            jtrick.position = taker_i
            self.current_game_meta.game.board.tricks.append(jtrick)
            self.current_game_meta.game.players[taker_i].tricks.append(trick_arr)

        elif game_event.name == EventNames.PartyEndedEvent:
            result = game_event.party_results
            for player_res in result.player_results:
                player = player_res.player
                player_i = self.session.players.index(player)
                score_change = player_res.score_change
                self.current_game_meta.game_points[player_i] = score_change

            for pi in range(3):
                player = self.session.players[pi]
                self.current_game_meta.game.players[pi].chips_change = player.points
                self.current_game_meta.game.players[pi].tricks_count = player.tricks_taken
                self.current_game_meta.game.players[pi].tricks_points = player.tricks_score

            self.game_log.gamelist.append(self.current_game_meta)
            self.current_game_meta = None

        elif game_event.name == EventNames.ContinueSessionEvent:
            pass
        elif game_event.name == EventNames.SessionEndedEvent:
            self.close()
        else:
            pass

    def close(self):
        if self.file:
            self.file.write('{"gamelist":[\n')

            for gmi in range(len(self.game_log.gamelist)):
                game_meta = self.game_log.gamelist[gmi]
                self.file.write(json.dumps(game_meta.as_json()))
                if gmi < len(self.game_log.gamelist) - 1:
                    self.file.write(',\n')
                else:
                    self.file.write('\n')
            self.file.write(']}\n')
            self.file.close()
            self.file = None

    def __del__(self):
        if self.file:
            self.file.close()
