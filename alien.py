import pygame
from alien_bullet import AlienBullet
from pygame.sprite import Sprite

class Alien(Sprite):
    """表示单个敌机的类"""

    def __init__(self, ai_game):
        """初始化敌机并设置起始位置"""
        super().__init__()
        self.screen=ai_game.screen

        #加载敌机图像并设置其rect属性
        self.image=pygame.image.load('image/alien.png')
        self.rect=self.image.get_rect()

        #存储敌机的精确位置
        self.x=float(self.rect.x)
        self.y=float(self.rect.y)

        #每个敌机最初都在屏幕左上角之外
        self.rect.x=self.rect.width
        self.rect.y=(-180)

        #敌机速度
        self.settings=ai_game.settings

        #敌机计时器
        self.timer=0

        #敌机开火计时器
        self.fire_timer=0

        #敌机意图控制
        self.state=self.ENTERING

        self.rect.y=self.y
        self.rect.x=self.x

        self.bullets=pygame.sprite.Group()

    def update(self):
        """敌机意图状态机"""
        #入场-射击-离场
        self.timer+=1
        if self.state==self.ENTERING:
            self._update_entering()

        if self.state==self.FIRERING:
            self._update_firering()

    def _update_entering(self):
        """敌机移动"""
        if self.y<(140):
            self.y += self.settings.alien_speed
            self.state=self.FIRERING

    def _update_firering(self):
        """敌机射击"""
        new_bullet=AlienBullet(self)
        self.bullets.add(new_bullet)

        
