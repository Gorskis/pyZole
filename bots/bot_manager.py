from typing import Tuple

from bots.Rando_Calrissian import RandoCalrissian
from bots.Sequential import Sequential
from bots.Experiment1 import Experiment1
from bots.Experiment3 import Experiment3
from bots.Experiment4_1 import Experiment4_1
from bots.Experiment4_2 import Experiment4_2
from bots.Experiment5 import Experiment5

all_bots = (RandoCalrissian,
            Sequential,
            Experiment1,
            Experiment3,
            Experiment4_1,
            Experiment4_2,
            Experiment5)
class BotManager:
    def __new__(cls):  # There can be only one
        if not hasattr(cls, 'instance'):
            cls.instance = super(BotManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.bots = all_bots
        self.names = [None] * len(self.bots)
        _ = 0
        for bot in self.bots:
            self.names[_] = bot.bot_name
            _ += 1

    def get_bot_names(self) -> Tuple[str]:
        return tuple(self.names)

    def get_bot_class_by_name(self, name: str):
        if name not in self.names:
            return None
        for bot in self.bots:
            if bot.bot_name == name:
                return bot
