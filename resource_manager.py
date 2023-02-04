import pygame
from zole.cards import all_cards, Card

_ctypes = {
    '♣': 'clb',
    '♦': 'dim',
    '♥': 'hrt',
    '♠': 'spd'
}


def get_alt_label(card: Card):
    ct = _ctypes[card.suit]
    return ct+card.rank


class Strings:
    def __init__(self):
        self.ready = 'Gatavs'
        self.game_mode = 'Spēles veids'
        self.pass_ = 'Garām'
        self.pick_up = 'Pacelt'
        self.zole = 'Zole'
        self.maza_zole = 'Mazā zole'
        self.discard_info = 'Jānorok divas kartis'
        self.discard = 'Norakt izvēlētās'
        self.play_another = 'Spēlēt vēl vienu partiju'
        self.end_game = 'Beigt spēli'
        self.new_game = 'Jaunā spēle'
        self.settings = 'Iestatījumi'
        self.exit = 'Iziet'
        self.back = 'Atpakaļ'
        self.write_log = 'rakstīt žurnālu'
        self.yes = 'Jā'
        self.no = 'Nē'
        self.start = 'Sākt'
        self.main_menu = 'Galvenā izvēlne'

    def are_you_ready(self, name):
        return f'{name} vei esi gatavs?'


class Resources:
    def __new__(cls):  # There can be only one
        if not hasattr(cls, 'instance'):
            cls.instance = super(Resources, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.window_icon = pygame.image.load(".\\Resources\\Images\\icon.png")
        self.background_image = pygame.image.load(".\\Resources\\Images\\bg.png")
        for card in all_cards:  # load card faces
            card.image = pygame.image.load(".\\Resources\\Images\\" + get_alt_label(card) + ".png")
        self.strings = Strings()

resources = Resources()
