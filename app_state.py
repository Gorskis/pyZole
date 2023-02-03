
class AppState:
    MAIN_SCREEN = 0
    PRE_GAME_SCREEN = 1
    GAME_SCREEN = 2
    SETTINGS = 3

    def __init__(self):
        self.exit_app = False
        self.current_screen = None
        self.game_session = None
        self.gui_players = None
        self.settings = None

    def set_screen(self, screen: int):
        self.current_screen = screen
