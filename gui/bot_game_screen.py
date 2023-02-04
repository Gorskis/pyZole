import threading

from app_state import AppState
from game_logger import GameLogger
from gui.abstract_screen import Screen
from gui.gui_elements import Button, Text, InputField
from gui.log_window import LogWindow
from zole.game_events import GameEvent, EventNames, StartSessionEvent
from zole.game_session import GameSession
from resource_manager import resources as res
from pygame.event import Event
from pygame import Surface

from zole.party import PartyResults


class BotGameScreen(Screen):
    def __init__(self, app_state: AppState, game_session: GameSession):
        super().__init__(app_state)
        self.game_session = game_session
        self.gui_elements.add(Button(res.strings.back, (400, 20), func=self.end_game))
        self.gui_elements.add(Text('Number of games', (50, 100)))
        self.num_input = self.gui_elements.add(InputField((300, 100), length=7, text='10'))
        self.gui_elements.add(Button(res.strings.start, (400, 100), func=self.start_game))
        self.log_window = self.gui_elements.add(LogWindow((50, 150)))
        self.game_started = False
        self.games_to_run = 0
        self.last_event: GameEvent = None
        self.game_logger = None
        if self.app_state.settings.write_log:
            self.game_logger = GameLogger()

    def log_result(self, party_results: PartyResults):
        first = party_results.party.players.first()
        second = party_results.party.players.second()
        third = party_results.party.players.third()
        self.log_window.add_text(f'{first}:{first.role}:{first.points} / {second}:{second.role}:{second.points} / {third}:{third.role}:{third.points}')

    def thread_update(self):
        self.game_session.current_event = StartSessionEvent()
        while True:
            game_event = self.game_session.update()
            if game_event != self.last_event:
                self.last_event = game_event
                if self.game_logger:
                    self.game_logger.log(game_event)
                if game_event.name == EventNames.ContinueSessionEvent:
                    self.games_to_run -= 1
                    game_event.set_continue(self.games_to_run > 0)
                elif game_event.name == EventNames.SessionEndedEvent:
                    self.game_started = False
                    break
                elif game_event.name == EventNames.PartyEndedEvent:
                    party_results = game_event.party_results
                    self.log_result(party_results)

    def update(self):
        pass

    def start_game(self):
        if self.game_started:
            return
        games_num = 0
        try:
            games_num = int(self.num_input.text)
        except ValueError:
            pass
        if games_num > 0:
            self.games_to_run = games_num
            self.game_started = True
            t = threading.Thread(target=self.thread_update)
            t.start()

    def end_game(self):
        if self.game_started:
            self.game_started = False
        if self.game_logger:
            self.game_logger.close()
        self.app_state.set_screen(AppState.MAIN_SCREEN)

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)

    def draw_to(self, surface: Surface):
        surface.fill((0, 0, 0))
        self.gui_elements.draw_to(surface)
