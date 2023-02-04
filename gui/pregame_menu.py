from bots.bot_manager import BotManager
from gui.game_screen import GameScreen
from gui_player import GUIPlayer

from app_state import AppState
from gui.abstract_screen import Screen
from gui.gui_elements import Button, InputField, Toggle, Text
from pygame.event import Event
from pygame import Surface

from zole.game_session_factory import GameSessionFactory
from resource_manager import resources as res


class PreGame(Screen):
    def __init__(self, app_state: AppState):
        super().__init__(app_state)
        self.gui_elements.add(Button(res.strings.back, (50, 50), func=self.go_back))
        self.input1 = InputField((50, 100), length=16, text='Player A')
        values = ('GUI',) + BotManager().get_bot_names()
        self.toggle1 = Toggle(values, (300, 100))
        self.gui_elements.add(self.input1)
        self.gui_elements.add(self.toggle1)
        self.input2 = InputField((50, 150), length=16, text='Player B')
        self.toggle2 = Toggle(values, (300, 150))
        self.gui_elements.add(self.input2)
        self.gui_elements.add(self.toggle2)
        self.input3 = InputField((50, 200), length=16, text='Player C')
        self.toggle3 = Toggle(values, (300, 200))
        self.gui_elements.add(self.input3)
        self.gui_elements.add(self.toggle3)
        self.gui_elements.add(Text(res.strings.write_log, (250, 250)))
        self.toggle_log = self.gui_elements.add(Toggle((res.strings.yes, res.strings.no), (470, 250)))
        self.gui_elements.add(Button(res.strings.start, (550, 300), func=self.start_game))


    def handle_event(self, event: Event, m_pos=(0, 0)):
        self.gui_elements.handle_event(event, m_pos)
        # TODO test if all values in toggles are set to bots
        # TODO if so, display game count input

    def draw_to(self, surface: Surface):
        surface.fill((25, 25, 25))
        self.gui_elements.draw_to(surface)

    def start_game(self):
        self.app_state.settings.write_log = self.toggle_log.get_value() == res.strings.yes
        bm = BotManager()
        gahc1 = bm.get_bot_class_by_name(self.toggle1.get_value()) or GUIPlayer
        gahc2 = bm.get_bot_class_by_name(self.toggle2.get_value()) or GUIPlayer
        gahc3 = bm.get_bot_class_by_name(self.toggle3.get_value()) or GUIPlayer

        gsf = GameSessionFactory()
        gui_players = []
        gahs = [None, None, None]
        gahs[0] = gsf.add_player(gahc1(self.input1.text))
        gahs[1] = gsf.add_player(gahc2(self.input2.text))
        gahs[2] = gsf.add_player(gahc3(self.input3.text))
        for gah in gahs:
            if isinstance(gah, GUIPlayer):
                gui_players.append(gah)
        game_session = gsf.make_session()
        if len(gui_players) > 0:
            self.app_state.game_session = game_session
            self.app_state.gui_players = gui_players
            self.app_state.set_screen(AppState.GAME_SCREEN)
        else:
            # TODO run a non-gui game with n parties
            self.go_back()

    def go_back(self):
        self.app_state.set_screen(AppState.MAIN_SCREEN)
