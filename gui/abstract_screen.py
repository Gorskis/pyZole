from app_state import AppState
from gui.gui_elements import GuiElementCollection
from pygame.event import Event
from pygame import Surface


class Screen:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.gui_elements = GuiElementCollection()

    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)

    def update(self):
        pass

    def draw_to(self, surface: Surface):
        pass
