from typing import Tuple
from bots.Rando_Calrissian import RandoCalrissian
from bots.Sequential import Sequential
from bots.Experiment1 import Experiment1
from bots.Experiment1_mask import Experiment1_mask
from bots.Experiment3 import Experiment3
from bots.Experiment3_mask import Experiment3_mask
from bots.Experiment4_1 import Experiment4_1
from bots.Experiment4_2 import Experiment4_2
from bots.Experiment5 import Experiment5
from bots.Experiment9 import Experiment9
from bots.Experiment10 import Experiment10
from bots.Experiment11 import Experiment11
from bots.Experiment12 import Experiment12
from bots.Experiment15 import Experiment15
from bots.Experiment16 import Experiment16
from bots.Experiment17 import Experiment17
from bots.Experiment18 import Experiment18
from bots.Experiment19 import Experiment19
from bots.Experiment20 import Experiment20
from bots.Experiment21 import Experiment21
from bots.Experiment22 import Experiment22
from bots.Experiment25 import Experiment25
from bots.Experiment26 import Experiment26
from bots.Experiment41 import Experiment41
from bots.Experiment42 import Experiment42

import bots

all_bots = (RandoCalrissian,
            Sequential,
            # Experiment1,
            # Experiment1_mask,
            # Experiment3,
            # Experiment3_mask,
            # Experiment4_1,
            # Experiment4_2,
            # Experiment5,
            # Experiment9,
            # Experiment10,
            # Experiment11,
            #Experiment12,
            # Experiment15,
            # Experiment16,
            # Experiment17,
            # Experiment18,
            # Experiment19,
            # Experiment20,
            # Experiment21,
            Experiment22,
            Experiment25,
            Experiment26,
            Experiment41,
            Experiment42)

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
