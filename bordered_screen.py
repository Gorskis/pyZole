import pygame
from pygame import HWSURFACE, DOUBLEBUF, RESIZABLE
from resource_manager import resources


class BorderedScreen:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.base_size = screen_size
        self.sub_size = screen_size
        self.padding = (0, 0)
        self.screen = pygame.display.set_mode(self.base_size, HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.sub_screen = pygame.Surface(self.base_size)
        self.background_tile = resources.background_image
        self.background_tile_size = self.background_tile.get_size()

    def resize_screen(self, new_size):
        self.screen_size = new_size
        self.screen = pygame.display.set_mode(self.screen_size, HWSURFACE | DOUBLEBUF | RESIZABLE)
        if self.screen_size[0] * 0.562 <= self.screen_size[1]:
            self.sub_size = (self.screen_size[0], int(self.screen_size[0] * 0.562 + 0.5))
            self.padding = (0, (self.screen_size[1] - self.sub_size[1]) / 2)
        else:
            self.sub_size = (int(self.screen_size[1] * 1.779359431 + 0.5), self.screen_size[1])
            self.padding = ((self.screen_size[0] - self.sub_size[0]) / 2, 0)

    def get_mouse_sub_pos(self, m_pos):
        return ((m_pos[0]-self.padding[0]) / self.sub_size[0] * self.base_size[0],
                (m_pos[1]-self.padding[1]) / self.sub_size[1] * self.base_size[1])

    def draw_background(self):
        if self.padding[0] > 0:
            for x in range(1 + int(self.padding[0] / self.background_tile_size[0])):
                for y in range(1 + int(self.screen_size[1] / self.background_tile_size[1])):
                    self.screen.blit(self.background_tile, (x * self.background_tile_size[0],
                                                            y * self.background_tile_size[1]))
                    self.screen.blit(self.background_tile,
                                     (self.screen_size[0] - (1 + x) * self.background_tile_size[0],
                                      y * self.background_tile_size[1]))
        elif self.padding[1] > 0:
            for x in range(1 + int(self.screen_size[0] / self.background_tile_size[0])):
                for y in range(1 + int(self.padding[1] / self.background_tile_size[1])):
                    self.screen.blit(self.background_tile, (x * self.background_tile_size[0],
                                                            y * self.background_tile_size[1]))
                    self.screen.blit(self.background_tile,
                                     (x * self.background_tile_size[0],
                                      self.screen_size[1] - (1 + y) * self.background_tile_size[1]))

    def apply_sub_screen(self):
        if self.screen_size == self.base_size:
            self.screen.blit(self.sub_screen, (0, 0))
        elif self.screen_size[0] * 0.562 <= self.screen_size[1]:
            self.screen.blit(pygame.transform.scale(self.sub_screen, self.sub_size), self.padding)
        else:
            self.screen.blit(pygame.transform.scale(self.sub_screen, self.sub_size), self.padding)
