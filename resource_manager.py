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

class Resources:
    def __init__(self):
        self.window_icon = pygame.image.load(".\\Resources\\Images\\icon.png")
        self.background_image = pygame.image.load(".\\Resources\\Images\\bg.png")
        for card in all_cards:  # load card faces
            card.image = pygame.image.load(".\\Resources\\Images\\" + get_alt_label(card) + ".png")


resources = Resources()
