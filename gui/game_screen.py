import pygame
from pygame.event import Event
from pygame import Surface

from game_logger import GameLogger
from gui.abstract_screen import Screen
from timer import Timer
from gui.game_gui_elements import TableCards, GUICardHand, PlayerInfo
from gui.gui_elements import Button, Text, GuiElementCollection
from app_state import AppState
from zole.game_events import GameEvent, EventNames, DiscardCardsEvent, SelectGameModeEvent, PlayCardEvent, \
    ContinueSessionEvent
from zole.game_modes import GameMode
from zole.game_session import GameSession
from zole.player import Player
from resource_manager import resources as res


class FogOfWar:
    def __init__(self):
        self.show = True
        self.text: Text = None
        self.button = Button(res.strings.ready, (200, 250), func=self._hide)

    def set_player(self, player: Player):
        text = res.strings.are_you_ready(player.name)
        self.text = Text(text, (200, 200), color=(0, 0, 0))

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.button.handle_event(event, m_pos)

    def draw_to(self, surface: Surface):
        surface.fill((125, 75, 75))
        self.text.draw_to(surface)
        self.button.draw_to(surface)

    def _hide(self):
        self.show = False


class GameModePicker:
    def __init__(self):
        self.show = False
        self.gui_elements = GuiElementCollection()
        self.gui_elements.add(Text(res.strings.game_mode, (300, 150), color=(0, 0, 0)))
        self.gui_elements.add(Button(res.strings.pass_, (300, 200), func=self._pick_pass))
        self.gui_elements.add(Button(res.strings.pick_up, (300, 250), func=self._pick_pacelt))
        self.gui_elements.add(Button(res.strings.zole, (300, 300), func=self._pick_zole))
        self.gui_elements.add(Button(res.strings.maza_zole, (300, 350), func=self._pick_mazazole))
        self.game_event: SelectGameModeEvent = None

    def set_game_action(self, game_event: SelectGameModeEvent):
        self.game_event = game_event
        self.show = True

    def _set_mode(self, mode):
        self.game_event.set_selected_game_mode(mode)
        self.show = False

    def _pick_pass(self):
        self._set_mode(GameMode.PASS)

    def _pick_pacelt(self):
        self._set_mode(GameMode.PACELT)

    def _pick_zole(self):
        self._set_mode(GameMode.ZOLE)

    def _pick_mazazole(self):
        self._set_mode(GameMode.MAZAZOLE)

    def draw_to(self, surface: Surface):
        self.gui_elements.draw_to(surface)

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)


class DiscardPicker:
    def __init__(self, hand: GUICardHand):
        self.show = False
        self.gui_elements = GuiElementCollection()
        self.gui_elements.add(Text(res.strings.discard_info, (200, 200), color=(0, 0, 0)))
        self.gui_elements.add(Button(res.strings.discard, (200, 250), func=self._pick_discard))
        self.game_event: DiscardCardsEvent = None
        self.hand = hand

    def set_game_action(self, game_event: DiscardCardsEvent):
        self.game_event = game_event
        self.show = True

    def _pick_discard(self):
        if self.hand.selected and self.hand.selected2:
            self.game_event.discard_cards(self.hand.selected.card, self.hand.selected2.card)
            self.show = False

    def draw_to(self, surface: Surface):
        self.gui_elements.draw_to(surface)

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)


class ContinuePrompt:
    def __init__(self):
        self.show = False
        self.gui_elements = GuiElementCollection()
        self.gui_elements.add(Button(res.strings.play_another, (300, 200), func=self._continue))
        self.gui_elements.add(Button(res.strings.end_game, (300, 250), func=self._quit))
        self.game_event: ContinueSessionEvent = None

    def set_game_action(self, game_event: ContinueSessionEvent):
        self.game_event = game_event
        self.show = True

    def _continue(self):
        self.game_event.set_continue(True)
        self.show = False

    def _quit(self):
        self.game_event.set_continue(False)
        self.show = False

    def draw_to(self, surface: Surface):
        self.gui_elements.draw_to(surface)

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)


class GameScreen(Screen):
    def __init__(self, app_state: AppState, game_session: GameSession, gui_players):
        super().__init__(app_state)
        self.game_session = game_session
        self.gui_players = gui_players  # TODO Do I need this?
        self.gui_player_count = len(gui_players)
        for gui_player in gui_players:
            gui_player.gui = self
        self.last_player = None  # Indicates the last player object for whom the GUI was drawn.
        # If there is only one GUI player, this will always be the same.
        self.fog_of_war = FogOfWar()
        self.card_Hand = GUICardHand()
        self.table_cards = TableCards((200, 150))
        self.player_left = PlayerInfo((20, 20))
        self.player_right = PlayerInfo((730, 20))
        self.player_info = PlayerInfo((5, 380))
        #Mutable info window
        self.game_mode_picker = GameModePicker()
        self.discard_picker = DiscardPicker(self.card_Hand)
        self.continue_prompt = ContinuePrompt()
        self.play_card_event: PlayCardEvent = None

        self.gui_elements.add(Button(res.strings.end_game, (400, 20), func=self.end_game))
        self.last_event = None
        self.timer = Timer()
        self.game_logger = None
        if self.app_state.settings.write_log:
            self.game_logger = GameLogger()

    def update(self):
        if self.timer.is_done():
            game_event = self.game_session.update()
            if game_event != self.last_event:
                self.last_event = game_event
                if self.game_logger:
                    self.game_logger.log(game_event)

                if game_event.name == EventNames.ContinueSessionEvent:
                    self.continue_prompt.set_game_action(game_event)
                elif game_event.name == EventNames.CardPlayedEvent:
                    self.timer.set_timer(1)
                elif game_event.name == EventNames.SessionEndedEvent:
                    self.end_game()

                gui_player = self.last_player or self.gui_players[0]
                self.set_player_view_for(gui_player, GameEvent('Stub', gui_player))

    def draw_to(self, surface: Surface):
        surface.fill((0, 0, 0))
        #if not self.last_player:
        #    return
        if not self.game_session.current_party:
            return
        self.gui_elements.draw_to(surface)
        if self.fog_of_war.show:
            self.fog_of_war.draw_to(surface)
            return
        self.player_left.draw_to(surface, self.game_session.current_party.active_player)
        self.player_right.draw_to(surface, self.game_session.current_party.active_player)
        self.player_info.draw_to(surface, self.game_session.current_party.active_player)
        self.card_Hand.draw_to(surface)
        if self.game_mode_picker.show:
            self.game_mode_picker.draw_to(surface)
        elif self.continue_prompt.show:
            self.continue_prompt.draw_to(surface)
        elif self.discard_picker.show:
            self.discard_picker.draw_to(surface)

        self.table_cards.draw_to(surface, self.game_session.current_party.table.trick, self.last_player)

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)
        if self.fog_of_war.show:
            self.fog_of_war.handle_event(event, m_pos)
            return
        last_card_clicked = self.card_Hand.handle_event(event.type == pygame.MOUSEBUTTONUP and event.button == 1, m_pos)
        if self.game_mode_picker.show:
            self.game_mode_picker.handle_event(event, m_pos)
        elif self.continue_prompt.show:
            self.continue_prompt.handle_event(event, m_pos)
        elif self.discard_picker.show:
            self.discard_picker.handle_event(event, m_pos)

        if self.play_card_event and last_card_clicked:
            first_card = self.play_card_event.trick.first_card()
            valid_cards = self.play_card_event.player.hand.get_valid_cards(first_card)
            if last_card_clicked in valid_cards:
                self.play_card_event.play_card(last_card_clicked)
                self.play_card_event = None
                self.card_Hand.set_selectable(0)
            else:
                pass
                # print(f'Card {last_card_clicked} not in valid cards {valid_cards}')

    def end_game(self):
        if self.game_logger:
            self.game_logger.close()
        self.app_state.set_screen(AppState.MAIN_SCREEN)

    def set_player_view_for(self, player: Player, game_event: GameEvent):
        if player != self.last_player:
            self.fog_of_war.set_player(player)
            self.fog_of_war.show = self.gui_player_count > 1
        self.last_player = player
        self.card_Hand.update_cards(player)  # TODO Move to update after new event
        player_left = player.next_player
        player_right = player_left.next_player
        self.player_left.set_player(player_left)
        self.player_right.set_player(player_right)
        self.player_info.set_player(player)
        if game_event.name == EventNames.SelectGameModeEvent:
            self.game_mode_picker.set_game_action(game_event)
        if game_event.name == EventNames.DiscardCardsEvent:
            self.discard_picker.set_game_action(game_event)
            self.card_Hand.set_selectable(2)
        if game_event.name == EventNames.PlayCardEvent:
            self.card_Hand.set_selectable(1)
            self.play_card_event = game_event
            first_card = game_event.trick.first_card()
            valid_cards = player.hand.get_valid_cards(first_card)
            self.card_Hand.set_valid_cards(valid_cards)
