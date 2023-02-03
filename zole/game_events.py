from zole.cards import Card, Cards
from zole.game_modes import GameMode
from zole.party import Party, PartyResults
from zole.player import Player
from zole.trick import Trick


class EventNames:
    StartSessionEvent = 'Start session'
    SessionStartedEvent = 'Session started'
    PartyStartedEvent = 'Party started'
    SelectGameModeEvent = 'Select game mode'
    GameModeSelectedEvent = 'Game mode selected'
    CardPickUpEvent = 'Cards picked up'
    DiscardCardsEvent = 'Discard cards'
    CardsDiscardedEvent = 'Cards discarded'
    TrickStartedEvent = 'Trick started'
    PlayCardEvent = 'Play card'
    CardPlayedEvent = 'Card played'
    TrickEndedEvent = 'Trick ended'
    PartyEndedEvent = 'Party ended'
    ContinueSessionEvent = 'Continue session'
    SessionEndedEvent = 'Session ended'


class GameEvent:
    def __init__(self, name: str, player: Player = None):
        self.name = name
        self.player = player
        self._is_done = False

    def is_done(self):
        return self._is_done

    def __repr__(self):
        return self.name


class StartSessionEvent(GameEvent):
    def __init__(self):
        super().__init__(EventNames.StartSessionEvent)
        self._is_done = True


class SessionStartedEvent(GameEvent):
    def __init__(self):
        super().__init__(EventNames.SessionStartedEvent)
        self._is_done = True


class PartyStartedEvent(GameEvent):
    def __init__(self, party: Party):
        super().__init__(EventNames.PartyStartedEvent)
        # player is party.first_hand
        self.party = party
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player}'


class SelectGameModeEvent(GameEvent):
    def __init__(self, player: Player):
        super().__init__(EventNames.SelectGameModeEvent, player)
        # player is selector
        self.selected_game_mode: GameMode = None

    def set_selected_game_mode(self, mode: GameMode):
        self.selected_game_mode = mode
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.selected_game_mode}'


class GameModeSelectedEvent(GameEvent):
    def __init__(self, player: Player, selected_game_mode: GameMode, party: Party):
        super().__init__(EventNames.GameModeSelectedEvent, player)
        # player is selector
        self.selected_game_mode = selected_game_mode
        self.party = party
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.selected_game_mode}'


class CardPickUpEvent(GameEvent):
    def __init__(self, player: Player, community_cards: Cards):
        super().__init__(EventNames.CardPickUpEvent, player)
        self.community_cards = community_cards
        self.new_card1: Card = self.community_cards[0]
        self.new_card2: Card = self.community_cards[1]

    def take_cards(self):
        self.player.hand.take_all_cards_from(self.community_cards)
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.new_card1} & {self.new_card2}'


class DiscardCardsEvent(GameEvent):
    def __init__(self, player: Player, community_cards: Cards):
        super().__init__(EventNames.DiscardCardsEvent, player)
        # player is lielais
        self.community_cards = community_cards
        self.card1: Card = None
        self.card2: Card = None

    def discard_cards(self, card1: Card, card2: Card):
        self.card1 = card1
        self.card2 = card2
        self.player.hand.remove_card(self.card1)
        self.player.hand.remove_card(self.card2)
        self.community_cards.add_card(self.card1)
        self.community_cards.add_card(self.card2)
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.card1} & {self.card2}'


class CardsDiscardedEvent(GameEvent):
    def __init__(self, player: Player, community_cards: Cards):
        super().__init__(EventNames.CardsDiscardedEvent, player)
        # player is lielais
        self.community_cards = community_cards
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.community_cards}'


class TrickStartedEvent(GameEvent):
    def __init__(self, player: Player):
        super().__init__(EventNames.TrickStartedEvent, player)
        # player is first hand
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player}'


class PlayCardEvent(GameEvent):
    def __init__(self, player: Player, trick: Trick):
        super().__init__(EventNames.PlayCardEvent, player)
        # player is active player
        self.trick = trick
        self.card: Card = None

    def play_card(self, card: Card):
        self.card = card
        self.player.hand.remove_card(self.card)
        self.trick.play_card(self.card, self.player)
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.card} in {self.trick}'


class CardPlayedEvent(GameEvent):
    def __init__(self, player: Player, trick: Trick, card: Card):
        super().__init__(EventNames.CardPlayedEvent, player)
        # player is active player
        self.trick = trick
        self.card: Card = card
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.player} > {self.card} in {self.trick}'


class TrickEndedEvent(GameEvent):
    def __init__(self, trick: Trick):
        super().__init__(EventNames.TrickEndedEvent)
        self.trick = trick
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.trick}'


class PartyEndedEvent(GameEvent):
    def __init__(self, party_results: PartyResults):
        super().__init__(EventNames.PartyEndedEvent)
        self.party_results = party_results
        self._is_done = True

    def __repr__(self):
        return f'{self.name} > {self.party_results}'


class ContinueSessionEvent(GameEvent):
    def __init__(self):
        super().__init__(EventNames.ContinueSessionEvent)
        self.keep_going: bool = None

    def set_continue(self, choice: bool):
        self.keep_going = choice
        self._is_done = True


class SessionEndedEvent(GameEvent):
    def __init__(self):
        super().__init__(EventNames.SessionEndedEvent)
        # Never and always done
