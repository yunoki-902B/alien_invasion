import pygame
from pygame.sprite import Sprite
import math

class AlienBullet(Sprite):
    """管理敌机所发射子弹的类"""

    def __init__(self,ai_game):
        super().__init__()
        self.screen=ai_game.screen
        self.settings=ai_game.settings
        self.alien_color=self.settings.alien_bullet_color

        #在(0,0)处创建一个表示子弹的矩形，再设置正确的位置
        self.rect=pygame.Rect(0,0,self.settings.alien_bullet_width,
                              self.settings.alien_bullet_height)
        self.rect.midbottom=ai_game.alien.rect.midbottom

        #获取自机坐标
        self.player_x = ai_game.ship.rect.centerx
        self.player_y = ai_game.ship.rect.centery

        self.enemy_x = ai_game.alien.rect.centerx
        self.enemy_y = ai_game.alien.rect.centery

        #存储用浮点数表示子弹的位置
        self.y=float(self.rect.y)
        self.x=float(self.rect.x)

    def update(self):
        """向目标发射子弹"""
        #算出敌机和自机的向量
        #将向量转换为角度
        #角度乘以速度得出子弹飞行路径
        dy=self.enemy_y-self.player_x
        dx=self.enemy_x-self.player_x
        angle_radians=math.atan2(dy,dx)
        angle_degress=math.degrees(angle_radians)
        vx = math.cos(angle_degress) * self.settings.alien_bullet_speed
        vy = math.sin(angle_degress) * self.settings.alien_bullet_speed

        self.x += vx
        self.y += vy

        #更新表示子弹的rect的位置
        self.rect.y=self.y
        self.rect.x=self.x
    
    def draw_bullet(self):
        """在屏幕上绘制敌机子弹"""
        pygame.draw.rect(self.screen,self.alien_color,self.rect)