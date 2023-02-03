from app_state import AppState
from gui.abstract_screen import Screen
from gui.gui_elements import Button
from pygame.event import Event
from pygame import Surface

from gui.pregame_menu import PreGame
from gui.settings_screen import Settings


class MainMenu(Screen):
    def __init__(self, app_state: AppState):
        super().__init__(app_state)
        self.gui_elements.add(Button('New Game', (50, 50), func=self.start_new_game))
        self.gui_elements.add(Button('Settings', (50, 100), func=self.open_settings))
        self.gui_elements.add(Button('Exit', (50, 150), func=self.exit_app))

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)

    def draw_to(self, surface: Surface):
        surface.fill((25, 25, 25))
        self.gui_elements.draw_to(surface)

    def start_new_game(self):
        self.app_state.set_screen(AppState.PRE_GAME_SCREEN)

    def open_settings(self):
        self.app_state.set_gui(Settings(self.app_state))
        self.app_state.set_screen(AppState.SETTINGS)

    def exit_app(self):
        self.app_state.exit_app = True
