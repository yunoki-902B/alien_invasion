import pygame
from alien_bullet import AlienBullet
from pygame.sprite import Sprite
import time

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
        self.rect.y=-180

        #敌机速度
        self.settings=ai_game.settings

        #敌机计时器
        self.timer=0

        #敌机开火计时器
        self.fire_timer=0.0

        #敌机意图控制
        self.state="ENTERING"
        self.fire=False

    def update(self):
        """敌机意图状态机"""
        #入场-射击-离场
        self.timer += 1
        fire_signal = None

        if self.state == "ENTERING":
            self._update_entering()
        elif self.state == "FIRERING":
            fire_signal = self._update_firering()
        elif self.state == "EXITING":
            self._update_exiting()

        self.rect.y = self.y
        self.rect.x = self.x
        return fire_signal

    def _update_entering(self):
        """敌机移动"""
        if self.y<140:
            self.y += self.settings.alien_speed
        else:
            self.state = "FIRERING"
            self.fire_timer = time.time()

    def _update_firering(self):
        """敌机射击"""
        self.fire = True
        if self.timer <= 450:
            if time.time() - self.fire_timer >= 0.5:
                self.fire_timer = time.time()
                return "FIRE"
        else:
            self.state="EXITING"

    def _update_exiting(self):
        self.rect.y=self.y
        if self.timer>600:
            if self.x<=300:
                self.x-=self.settings.alien_speed
                self.rect.x=self.x
            else:
                self.x+=self.settings.alien_speed
                self.rect.x=self.x