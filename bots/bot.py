from zole.party import Party
from zole.player import Player


class Bot(Player):
    bot_name = 'Abstract bot'

    def __init__(self, player_name:str):
        super().__init__(player_name)

