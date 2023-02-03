from app_state import AppState
from gui.abstract_screen import Screen
from gui.game_screen import GameScreen
from gui.main_menu import MainMenu
from gui.pregame_menu import PreGame
from gui.settings_screen import Settings


class ScreenManager:
    SCREENS = {
        AppState.MAIN_SCREEN: MainMenu,
        AppState.PRE_GAME_SCREEN: PreGame,
        AppState.GAME_SCREEN: GameScreen,
        AppState.SETTINGS: Settings
    }

    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.app_state.set_screen(AppState.MAIN_SCREEN)
        self.last_screen: int = AppState.MAIN_SCREEN
        self.current_screen = MainMenu(self.app_state)

    def get_screen(self) -> Screen:
        screen = self.app_state.current_screen
        if self.last_screen != screen:
            self.last_screen = screen
            if screen == AppState.GAME_SCREEN:
                self.current_screen = ScreenManager.SCREENS[screen](self.app_state, self.app_state.game_session,
                                                                    self.app_state.gui_players)
            else:
                self.current_screen = ScreenManager.SCREENS[screen](self.app_state)
        return self.current_screen
