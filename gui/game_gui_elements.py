import pygame
from pygame import Surface

from zole.cards import Card, no_card, Cards
from zole.trick import Trick
from gui.gui_elements import Text
from zole.player import Player


class GameGuiElement:
    def __init__(self, pos=(0, 0)):
        self.pos = pos

    def draw_to(self, surface: Surface):
        pass


class PlayerInfo(GameGuiElement):
    def __init__(self, pos=(0, 0)):
        super().__init__(pos)
        self.rect = [self.pos[0]-5, self.pos[1]-10, 280, 55]
        self.player: Player = None
        self.name: Text = None
        self.score: Text = None

    def set_player(self, player):
        self.player = player
        self.name = Text(player.name, self.pos)
        tricks: int = player.tricks_taken
        text = f'↨{tricks} A:{str(player.tricks_score)} P:{str(player.points)} {player.role}'
        self.score = Text(text, (self.pos[0], self.pos[1] + 20))

    def update(self):
        self.set_player(self.player)

    def draw_to(self, surface: Surface, active_player: Player):
        self.name.draw_to(surface)
        self.score.draw_to(surface)
        if self.player == active_player:
            pygame.draw.rect(surface, (55, 255, 155), self.rect, 2, border_radius=3)



class TableCards(GameGuiElement):
    def __init__(self, pos=(0, 0)):
        super().__init__(pos)

    def draw_to(self, surface: Surface, cards: Trick, player: Player):
        for ci in range(len(cards)):
            card, played_by = cards[ci]
            if played_by == player:
                surface.blit(card.image, (self.pos[0]+40, self.pos[1]+50))
            elif played_by == player.next_player:
                surface.blit(card.image, (self.pos[0], self.pos[1]))
            else:
                surface.blit(card.image, (self.pos[0]+80, self.pos[1]))


class GUICard(GameGuiElement):
    def __init__(self, card: Card = no_card, pos=(0, 0)):
        super().__init__(pos)
        self.card = card
        #self.size = ()# self.card.image.get_size()
        self.rect = [self.pos[0], self.pos[1], 100, 136]

    def draw_to(self, surface: Surface, is_selected=False, is_hover=False, is_valid=False):
        #print('Drawing card: '+str(self.card) + ' at '+str(self.pos))
        if not self.card == no_card:
            surface.blit(self.card.image, self.pos)
        if is_selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 3, border_radius=3)
        elif is_hover:
            pygame.draw.rect(surface, (255, 255, 100), self.rect, 3, border_radius=3)
        elif is_valid:
            pygame.draw.rect(surface, (0, 75, 75), self.rect, 3, border_radius=3)

    def hit(self, m_pos=(0, 0)) -> bool:
        return self.card != no_card and self.rect[0] < m_pos[0] < self.rect[2]+self.rect[0] and self.rect[1] < m_pos[1] < self.rect[3] + self.rect[1]


class GUICardHand(GameGuiElement):
    def __init__(self, pos=(0, 0)):
        super().__init__(pos)
        self.player = None
        self.gui_cards = [None]*10
        self.is_valid = [False]*10
        for ci in range(10):
            self.gui_cards[ci] = GUICard(pos=(ci*100, 562 - 136))
        self.selectable = 0  # 0 - not selectable, 1 - select 1, 2 - select 2
        self.selected: GUICard = None
        self.selected2: GUICard = None
        self.hover: GUICard = None

    def set_selectable(self, v: int):
        self.selectable = v
        self.selected = None
        self.selected2 = None
        self.hover = None

    def update_cards(self, player: Player):
        self.player = player
        gci = 0
        for card in player.hand:
            self.gui_cards[gci].card = card
            gci += 1
        for ci in range(gci, 10):
            self.gui_cards[ci].card = no_card

    def update(self):
        self.update_cards(self.player)

    def handle_event(self, click=False, m_pos=(0, 0)) -> Card:
        last_card_clicked: Card = None
        if self.selectable > 0:
            #print(f'event(click={click}, m_pos=({m_pos})')
            self.hover = None
            if m_pos[1] > 562 - 136:
                for gui_card in self.gui_cards:
                    if gui_card.hit(m_pos):
                        #print(f'hit on {gui_card.card}')
                        if click:
                            last_card_clicked = gui_card.card
                            if self.selectable > 1:
                                if not self.selected:
                                    self.selected = gui_card
                                elif gui_card == self.selected:
                                    self.selected = self.selected2
                                    self.selected2 = None
                                elif not self.selected2:
                                    self.selected2 = gui_card
                                elif gui_card == self.selected2:
                                    self.selected2 = None
                        else:
                            self.hover = gui_card
                            break
        else:
            self.selected = None
            self.selected2 = None
            self.hover = None
        return last_card_clicked

    def draw_to(self, surface: Surface):
        for gci in range(10):
            gui_card = self.gui_cards[gci]
            if gui_card.card == no_card:
                break
            if gui_card == self.selected or gui_card == self.selected2:
                gui_card.draw_to(surface, is_selected=True)
            elif gui_card == self.hover:
                gui_card.draw_to(surface, is_hover=True)
            else:
                gui_card.draw_to(surface, is_valid=self.is_valid[gci])

    def set_valid_cards(self, valid_cards: Cards):
        for gci in range(10):
            gui_card = self.gui_cards[gci] 
            if gui_card.card == no_card:
                break
            self.is_valid[gci] = gui_card.card in valid_cards
