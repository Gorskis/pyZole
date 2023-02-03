from pygame import Surface
from gui.abstract_screen import Screen
from gui.gui_elements import Button
from app_state import AppState


class Settings(Screen):
    def __init__(self, app_state: AppState):
        super().__init__(app_state)
        self.gui_elements.add(Button('Main menu', (50, 50), func=self.open_main_menu))

    def draw_to(self, surface: Surface):
        surface.fill((25, 25, 25))
        self.gui_elements.draw_to(surface)

    def open_main_menu(self):
        self.app_state.set_screen(AppState.MAIN_SCREEN)
