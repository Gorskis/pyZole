from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode


class RandoCalrissian(Bot):
    bot_name = 'Rando Calrissian'
    def __init__(self, player_name:str):
        super().__init__(player_name)
        self.rand = Random()

    def handle_game_event(self, event: GameEvent):
        if event.name == EventNames.PartyStartedEvent:
            # my_cards = self.hand
            # party = event.party
            # TODO get my position in seating
            pass
        elif event.name == EventNames.SelectGameModeEvent:
            modes = [GameMode.PASS, GameMode.PACELT, GameMode.ZOLE, GameMode.MAZAZOLE]
            selected_game_mode = self.rand.choices(modes, [0.3, 0.4, 0.2, 0.1])[0]
            event.set_selected_game_mode(selected_game_mode)
        elif event.name == EventNames.GameModeSelectedEvent:
            # game_mode = event.selected_game_mode
            # role = self.role
            pass
        elif event.name == EventNames.CardPickUpEvent:
            # self.hand is still the same
            event.take_cards()
            # self.hand now has 2 more cards: event.new_card1 and event.new_card2
        elif event.name == EventNames.DiscardCardsEvent:
            c1i = c2i = self.rand.randint(0, 9)
            while c1i == c2i:
                c2i = self.rand.randint(0, 9)
            discard_card1 = self.hand[c1i]
            discard_card2 = self.hand[c2i]
            event.discard_cards(discard_card1, discard_card2)
        elif event.name == EventNames.PlayCardEvent:
            trick = event.trick
            first_card = trick.first_card()
            valid_cards = self.hand.get_valid_cards(first_card)
            card_to_play = valid_cards[self.rand.randint(0, len(valid_cards) - 1)]
            event.play_card(card_to_play)
        elif event.name == EventNames.TrickEndedEvent:
            trick = event.trick
            taker_of_the_trick = trick.tacker()
            trick_score = trick.score()
        elif event.name == EventNames.PartyEndedEvent:
            party_results = event.party_results
        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')
