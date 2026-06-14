class Settings:
    """存储游戏中所有设置的类"""

    def __init__(self):
        """初始化游戏的设置"""
        #屏幕设置
        self.screen_width = 600
        self.screen_height = 800
        self.bg_color = (130,230,230)
        #帧率设置
        self.clock_tick=60
        #飞机速度设置
        self.ship_speed=5
        #自机子弹设置
        self.bullet_speed=7
        self.bullet_width=3
        self.bullet_height=15
        self.bullet_color=(60,60,60)
        #敌机移动速度设置
        self.alien_speed=2
        #敌机子弹设置
        self.alien_bullet_speed=8
        self.alien_bullet_width=9
        self.alien_bullet_height=9
        self.alien_bullet_color=(200,0,0)