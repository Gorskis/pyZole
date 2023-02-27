from random import Random
from zole.cards import all_cards
from zole.trick import Trick
from zole.game_events import GameEvent, StartSessionEvent, EventNames, SessionStartedEvent, PartyStartedEvent, \
    SelectGameModeEvent, GameModeSelectedEvent, DiscardCardsEvent, TrickStartedEvent, CardsDiscardedEvent, \
    PlayCardEvent, CardPickUpEvent, CardPlayedEvent, TrickEndedEvent, PartyEndedEvent, ContinueSessionEvent, \
    SessionEndedEvent
from zole.game_modes import GameMode
from zole.party import Party
from zole.player import PlayerCircle, Player


class GameSession:
    def __init__(self, players: PlayerCircle, seed=None):
        self.rand = Random(seed)
        self.players = players.shifts(self.rand.randint(0, 2))
        self.current_party: Party = None
        self.current_event: GameEvent = StartSessionEvent()

    def update(self) -> GameEvent:
        if not self.current_event.is_done():
            return self.current_event
        next_event = None
        handler: Player = None
        if self.current_event.name == EventNames.StartSessionEvent:  # <<< StartSessionEvent
            next_event = SessionStartedEvent()
        elif self.current_event.name == EventNames.SessionStartedEvent:  # <<< SessionStartedEvent
            self.current_party = Party(self.players)
            self._shuffle_and_deal()
            next_event = PartyStartedEvent(self.current_party)
        elif self.current_event.name == EventNames.PartyStartedEvent:  # <<< PartyStartedEvent
            next_event = SelectGameModeEvent(self.current_event.party.first_hand, 0)
            handler = next_event.player
        elif self.current_event.name == EventNames.SelectGameModeEvent:  # <<< SelectGameModeEvent
            player: Player = self.current_event.player
            game_mode: GameMode = self.current_event.selected_game_mode
            prev_selectors: int = self.current_event.prev_selectors
            if game_mode == GameMode.PASS:
                next_player = player.next_player
                if next_player == self.current_party.first_hand:
                    self.current_party.resolve_game_mode(None, GameMode.GALDINS)
                    next_event = GameModeSelectedEvent(player, GameMode.GALDINS, self.current_party)
                else:
                    next_event = SelectGameModeEvent(next_player, prev_selectors + 1)
                    handler = next_player
            else:
                self.current_party.resolve_game_mode(player, game_mode)
                next_event = GameModeSelectedEvent(player, game_mode, self.current_party)
        elif self.current_event.name == EventNames.GameModeSelectedEvent:  # <<< GameModeSelectedEvent
            if self.current_event.selected_game_mode == GameMode.PACELT:
                next_event = CardPickUpEvent(self.current_event.player, self.current_party.table.community_cards)
                handler = self.current_event.player
            else:
                next_event = TrickStartedEvent(self.current_party.active_player)
        elif self.current_event.name == EventNames.CardPickUpEvent:  # <<< CardPickUpEvent
            next_event = DiscardCardsEvent(self.current_event.player, self.current_event.community_cards)
            handler = self.current_event.player
        elif self.current_event.name == EventNames.DiscardCardsEvent:  # <<< DiscardCardsEvent
            self.current_event.player.hand.sort()
            next_event = CardsDiscardedEvent(self.current_event.player, self.current_event.community_cards)
        elif self.current_event.name == EventNames.CardsDiscardedEvent:  # <<< CardsDiscardedEvent
            next_event = TrickStartedEvent(self.current_party.active_player)
        elif self.current_event.name == EventNames.TrickStartedEvent:  # <<< TrickStartedEvent
            next_event = PlayCardEvent(self.current_event.player, self.current_party.table.trick)
            handler = self.current_event.player
        elif self.current_event.name == EventNames.PlayCardEvent:  # <<< PlayCardEvent
            next_event = CardPlayedEvent(self.current_event.player, self.current_event.trick, self.current_event.card)
        elif self.current_event.name == EventNames.CardPlayedEvent:  # <<< CardPlayedEvent
            trick: Trick = self.current_event.trick
            if trick.is_done():
                last_trick = self.current_party.resolve_trick()
                next_event = TrickEndedEvent(last_trick)
            else:
                next_player = self.current_event.player.next_player
                next_event = PlayCardEvent(next_player, trick)
                handler = next_player
        elif self.current_event.name == EventNames.TrickEndedEvent:  # <<< TrickEndedEvent
            if self.current_party.active_player.hand.has_cards():
                next_event = TrickStartedEvent(self.current_party.active_player)
            else:
                results = self.current_party.score_party()
                next_event = PartyEndedEvent(results)
        elif self.current_event.name == EventNames.PartyEndedEvent:  # <<< PartyEndedEvent
            next_event = ContinueSessionEvent()
        elif self.current_event.name == EventNames.ContinueSessionEvent:  # <<< ContinueSessionEvent
            if self.current_event.keep_going:
                self.current_party = self.current_party.next_party()
                for player in self.players:
                    player.clear_party_data()
                self._shuffle_and_deal()
                next_event = PartyStartedEvent(self.current_party)
            else:
                next_event = SessionEndedEvent()
        elif self.current_event.name == EventNames.SessionEndedEvent:   # <<< SessionEndedEvent
            pass
        else:
            print(f'Unknown event {self.current_event}')

        if handler:
            handler.handle_game_event(next_event)
        elif next_event.name in (EventNames.PartyStartedEvent, EventNames.TrickEndedEvent, EventNames.PartyEndedEvent):
            for player in self.players:
                player.handle_game_event(next_event)
        self.current_event = next_event
        return next_event

    def _shuffle_and_deal(self):
        new_cards = list(all_cards)
        for i in range(len(new_cards)):
            p = self.rand.randint(0, len(new_cards)-1)
            c = new_cards[p]
            new_cards[p] = new_cards[i]
            new_cards[i] = c

        for p in self.players:
            p.hand.clear()

        c_i = 0
        t_c = 0
        while c_i < len(new_cards):
            for p in self.players:
                for t in range(2):
                    p.hand.add_card(new_cards[c_i])
                    c_i += 1
            if t_c < 2:
                self.current_party.table.community_cards.add_card(new_cards[c_i])
                t_c += 1
                c_i += 1
        for p in self.players:
            p.hand.sort()
