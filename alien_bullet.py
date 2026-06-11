import pygame
from pygame.sprite import Sprite

class AlienShip(Sprite):
    """管理敌机所发射子弹的类"""

    def __init__(self,ai_game):
        super().__init__()
        self.screen=ai_game.screen
        self.settings=ai_game.settings
        self.alien_color=self.settings.alien_bullet_color

        #在(0,0)处创建一个表示子弹的矩形，再设置正确的位置
        self.rect=pygame.Rect(0,0,self.settings.alien_bullet_width,
                              self.settings.alien_bullet_height)
        self.rect.midtop=ai_game.alien.rect.midbottom

        #存储用浮点数表示子弹的位置
        self.y=float(self.rect.y)
        self.x=float(self.rect.x)

    def update(self):
        """向目标发射子弹"""
        self.y