from gui.game_screen import GameScreen
from zole.game_events import GameEvent, EventNames
from zole.player import Player


class GUIPlayer(Player):
    def __init__(self, name:str):
        super().__init__(name)
        self.gui: GameScreen = None

    def handle_game_event(self, event: GameEvent):
        if event.name == EventNames.PartyStartedEvent:
            self.gui.set_player_view_for(self, event)
        elif event.name == EventNames.SelectGameModeEvent:
            self.gui.set_player_view_for(self, event)
        elif event.name == EventNames.CardPickUpEvent:
            event.take_cards()
        elif event.name == EventNames.DiscardCardsEvent:
            self.gui.set_player_view_for(self, event)
        elif event.name == EventNames.PlayCardEvent:
            self.gui.set_player_view_for(self, event)
        elif event.name == EventNames.TrickEndedEvent:
            pass
        elif event.name == EventNames.PartyEndedEvent:
            pass
        else:
            print(f'GUI player not able to handle event {event.name}')
