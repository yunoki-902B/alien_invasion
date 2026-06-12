import pygame

class Ship:
    """管理飞船的类"""

    def __init__(self,ai_game):
        """初始化飞船并设置初始位置"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings=ai_game.settings

        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load('image/ship.png')
        self.rect = self.image.get_rect()

        # 每艘新飞船都放在屏幕底部中央
        self.rect.midbottom = self.screen_rect.midbottom

        # 在飞船属性x里存储浮点数
        self.x=float(self.rect.x)
        self.y=float(self.rect.y)

        #移动标志
        self.moving_right=False
        self.moving_left=False
        self.moving_up=False
        self.moving_down=False

    def update(self):
        """根据移动标志调整飞船位置"""
        # 更新飞船属性的值，而不是外接矩形的属性值
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed

        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y+=self.settings.ship_speed
            
        if self.moving_up and self.rect.top > 0:
            self.y-=self.settings.ship_speed

        # 根据 self.x / self.y 更新 rect 对象
        self.rect.x = self.x
        self.rect.y = self.y

    def blitme(self):
        """在指定位置放置飞船"""
        self.screen.blit(self.image,self.rect)