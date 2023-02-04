import pygame

from gui.gui_elements import Clickable
from pygame import Surface
from pygame.event import Event


class LogWindowText:
    def __init__(self, text: str, prev_text: 'LogWindowText' = None):
        font = pygame.font.SysFont('consolas', 18)
        self.render = font.render(text, True, (125, 125, 125))
        self.pev_text = prev_text
        self.next_text = None

    def draw_to(self, surface: Surface, pos):
        surface.blit(self.render, pos)


class LogWindow(Clickable):
    def __init__(self, pos=(0, 0), view_size: int = 10, max_size: int = -1):
        super().__init__(pos)
        self.size = 0
        self.max_size = max_size
        self.view_size = view_size
        self.newest: LogWindowText = None
        self.oldest: LogWindowText = None

    def add_text(self, text: str):
        new_text = LogWindowText(text, self.newest)
        if self.newest:
            self.newest.next_text = new_text
        self.newest = new_text
        if not self.oldest:
            self.oldest = new_text
        if self.size == self.max_size:
            to_del = self.oldest
            self.oldest = to_del.next_text
            self.oldest.pev_text = None
            to_del.next_text = None
        else:
            self.size += 1

    def draw_to(self, surface: Surface):
        c_pos = (self.pos[0], self.pos[1]+20*self.view_size)
        text = self.newest
        for i in range(self.view_size):
            if not text:
                break
            text.draw_to(surface, c_pos)
            c_pos = (c_pos[0], c_pos[1]-20)
            text = text.pev_text
