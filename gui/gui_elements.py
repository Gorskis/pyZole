import pygame
from pygame import Surface
from pygame.event import Event


class Clickable:
    def __init__(self, pos=(0, 0)):
        self.pos = pos

    def draw_to(self, surface: Surface):
        pass

    def handle_event(self, event: Event, m_pos=(0, 0)):
        pass


class GuiElementCollection(Clickable):
    def __init__(self):
        self.collection = {}

    def add(self, clickable: Clickable) -> Clickable:
        if clickable not in self.collection:
            self.collection[clickable] = clickable
        return clickable

    def handle_event(self, event: Event, m_pos=(0, 0)):
        for element in self.collection:
            element.handle_event(event, m_pos)

    def draw_to(self, surface: Surface):
        for element in self.collection:
            element.draw_to(surface)


class Button(Clickable):
    def __init__(self, label: str, pos=(0, 0), func = None, color=(125, 125, 125), fontsize = 24, background=(75, 75, 75)):
        super().__init__(pos)
        font = pygame.font.SysFont('consolas', fontsize)
        self.label = label
        self.text = font.render(label, True, color)
        self.size = self.text.get_size()
        self.rect = [self.pos[0]-3, self.pos[1]-3, self.size[0]+6, self.size[1]+6]
        self.background = background
        self.selected = False
        #text.get_size()
        if func:
           self.func = func
        else:
            self.func = self.__empty_func

    def draw_to(self, surface: Surface):
        pygame.draw.rect(surface, self.background, self.rect, border_radius=3)
        surface.blit(self.text, self.pos)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2, border_radius=3)

    def handle_event(self, event: Event, mpos: (0, 0)):
        if event.type == pygame.MOUSEMOTION:
            #mpos = pygame.mouse.get_pos()
            if self.__hit(mpos):
                self.selected = True
            else:
                self.selected = False
        elif event.type == pygame.MOUSEBUTTONUP:
            #mpos = pygame.mouse.get_pos()
            if self.__hit(mpos):
                self.func()

    def __hit(self, mpos=(0, 0)) -> bool:
        if mpos[0] > self.rect[0] and \
                mpos[0] - self.rect[0] < self.rect[2] and \
                mpos[1] > self.rect[1] and \
                mpos[1] - self.rect[1] < self.rect[3]:
            return True
        else:
            return False

    def __empty_func(self):
        print('Button "' + self.label + '" empty function')


class InputField(Clickable):
    def __init__(self, pos=(0, 0), length=8, text='', color=(75, 75, 75), fontsize = 24, background=(200, 200, 200)):
        super().__init__(pos)
        if len(text) > length:
            self.length = len(text)
        else:
            self.length = length
        self.text = 'W' * length
        self.font = pygame.font.SysFont('consolas', fontsize)
        self.color = color
        self.selected = False
        self.reading = False
        self.__render_text()
        size = self.r_text.get_size()
        self.rect = [self.pos[0]-3, self.pos[1]-3, size[0]+6, size[1]+6]
        self.background = background
        self.text = text
        self.__render_text()

    def __render_text(self):
        if self.reading and len(self.text) < self.length:
            self.r_text = self.font.render(self.text+'_', True, self.color)
        else:
            self.r_text = self.font.render(self.text, True, self.color)

    def draw_to(self, surface: Surface):
        pygame.draw.rect(surface, self.background, self.rect, border_radius=3)
        surface.blit(self.r_text, self.pos)
        if self.selected or self.reading:
            pygame.draw.rect(surface, (25, 200, 25), self.rect, 2, border_radius=3)

    def handle_event(self, event: Event, mpos: (0, 0)):
        if event.type == pygame.MOUSEMOTION:
            if self.__hit(mpos):
                self.selected = True
            else:
                self.selected = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.__hit(mpos):
                self.__set_reading(True)
            else:
                self.__set_reading(False)
        elif event.type == pygame.KEYDOWN and self.reading:
            k = event.key
            c = event.unicode
            #print(f'k: {k} c:{c} len:{len(c)}')
            if k == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif k == pygame.K_RETURN:
                self.__set_reading(False)
                self.selected = False
            elif k > 31 and len(c) == 1 and len(self.text) < self.length:
                self.text += c
            self.__render_text()

    def __set_reading(self, b):
        self.reading = b
        self.__render_text()

    def __hit(self, mpos=(0, 0)) -> bool:
        if mpos[0] > self.rect[0] and \
                mpos[0] - self.rect[0] < self.rect[2] and \
                mpos[1] > self.rect[1] and \
                mpos[1] - self.rect[1] < self.rect[3]:
            return True
        else:
            return False


class Toggle(Clickable):
    def __init__(self, values, pos=(0, 0), color=(125, 125, 125), fontsize = 24, background=(75, 75, 75)):
        super().__init__(pos)
        self.values = tuple(values)
        self.selected_value = 0
        font = pygame.font.SysFont('consolas', fontsize)
        self.values_r = [None]*len(self.values)
        self.size = [0, 0]
        for v_i in range(len(self.values)):
            render = font.render(str(self.values[v_i]), True, color)
            size = render.get_size()
            self.size[0] = max(self.size[0], size[0])
            self.size[1] = max(self.size[1], size[1])
            self.values_r[v_i] = render
        self.values_r = tuple(self.values_r)
        self.size = tuple(self.size)
        self.rect = [self.pos[0]-3, self.pos[1]-3, self.size[0]+6, self.size[1]+6]
        self.background = background
        self.selected = False

    def get_value(self):
        return self.values[self.selected_value]

    def draw_to(self, surface: Surface):
        pygame.draw.rect(surface, self.background, self.rect, border_radius=3)
        surface.blit(self.values_r[self.selected_value], self.pos)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2, border_radius=3)

    def handle_event(self, event: Event, mpos: (0, 0)):
        if event.type == pygame.MOUSEMOTION:
            if self.__hit(mpos):
                self.selected = True
            else:
                self.selected = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.__hit(mpos):
                self.toggle()

    def __hit(self, mpos=(0, 0)) -> bool:
        if mpos[0] > self.rect[0] and \
                mpos[0] - self.rect[0] < self.rect[2] and \
                mpos[1] > self.rect[1] and \
                mpos[1] - self.rect[1] < self.rect[3]:
            return True
        else:
            return False

    def toggle(self):
        self.selected_value += 1
        if self.selected_value == len(self.values):
            self.selected_value = 0


class Text(Clickable):
    def __init__(self, label: str, pos=(0, 0), color=(125, 125, 125), fontsize = 24, background=None):
        font = pygame.font.SysFont('consolas', fontsize)
        self.render = font.render(label, True, color, background)
        self.pos = pos

    def draw_to(self, surface: Surface):
        #pygame.draw.rect(surface, self.background, self.rect, border_radius=3)
        surface.blit(self.render, self.pos)
