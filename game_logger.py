from datetime import datetime

from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode


class GameLogger:
    def __init__(self):
        now = str(datetime.now())[:19].replace(':', '')
        self.file = None
        self.file = open(f'./logs/log-{now}.txt', 'w', encoding="utf-8")

    def log(self, game_event: GameEvent):
        if game_event.name == EventNames.SessionStartedEvent:
            self.file.write('Session started\n')
        elif game_event.name == EventNames.PartyStartedEvent:
            self.file.write(f'New party; first_hand: {game_event.party.first_hand}\n')
            for player in game_event.party.players:
                self.file.write(f'Cards; {player}: {player.hand}\n')
            self.file.write(f'Cards; table: {game_event.party.table.community_cards}\n')
        elif game_event.name == EventNames.SelectGameModeEvent:
            current_selection = game_event.selected_game_mode
            if current_selection == GameMode.PASS:
                self.file.write(f'Selected PASS; by: {game_event.player}\n')
        elif game_event.name == EventNames.GameModeSelectedEvent:
            self.file.write(f'Game mode selected; mode: {game_event.selected_game_mode}; by: {game_event.player}\n')
            for player in game_event.party.players:
                self.file.write(f'Role; {player}:{player.role}\n')
        elif game_event.name == EventNames.CardPickUpEvent:
            pass
        elif game_event.name == EventNames.DiscardCardsEvent:
            pass
        elif game_event.name == EventNames.CardsDiscardedEvent:
            player = game_event.player
            cards = game_event.community_cards
            self.file.write(f'Discarded; cards: {cards}; by: {player}\n')
        elif game_event.name == EventNames.TrickStartedEvent:
            pass
        elif game_event.name == EventNames.PlayCardEvent:
            pass
        elif game_event.name == EventNames.CardPlayedEvent:
            self.file.write(f'Played; card: {game_event.card}; by: {game_event.player}\n')
        elif game_event.name == EventNames.TrickEndedEvent:
            self.file.write(f'End of trick; cards: ({game_event.trick}); value: {game_event.trick.score()}; taken_by: {game_event.trick.tacker()}\n')
        elif game_event.name == EventNames.PartyEndedEvent:
            results = game_event.party_results
            txt = None
            if results.party.game_mode != GameMode.GALDINS:
                txt = f'lielais_score:{results.party.lielais.tricks_score}; winner: {"Lielais" if results.lielais_won else "mazie"}\n'
                txt+=str(results.player_results[0])+'\n'
                txt+=str(results.player_results[1])+'\n'
                txt+=str(results.player_results[2])
            self.file.write(f'End of party; {txt}\n')
        elif game_event.name == EventNames.ContinueSessionEvent:
            pass
        elif game_event.name == EventNames.SessionEndedEvent:
            self.file.write(f'End of session\n')
        else:
            pass

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def __del__(self):
        if self.file:
            self.file.close()
