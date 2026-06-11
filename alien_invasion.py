import sys          # 用来安全退出程序
import pygame       # 导入 pygame 游戏库
from settings import Settings   #导入设置
from ship import Ship   #导入飞机
from bullet import Bullet   #导入子弹
import time
from alien import Alien

class AlienInvasion:
    """管理整个游戏的主类"""

    def __init__(self):
        """初始化游戏，并创建游戏窗口"""

        # 初始化 pygame 所有模块（必须做）
        pygame.init()

        # 创建游戏窗口
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # 注意：set_mode 需要用“双括号”传入宽高
        self.screen = pygame.display.set_mode((
            self.settings.screen_width,
            self.settings.screen_height
            ))

        # 设置窗口标题
        pygame.display.set_caption("Alien Invasion")

        self.ship=Ship(self)

        self.bullets=pygame.sprite.Group()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.aliens=pygame.sprite.Group()
        
        self._create_fleet()

    def run_game(self):
        """开始游戏主循环（游戏运行的核心）"""

        # 无限循环：游戏会一直运行，直到你手动退出
        while True:
            # 监听函数
            self._check_events()
            # 移动函数
            self.ship.update()
            # 按住空格时自动发射子弹
            self._update_auto_fire()
            #子弹删除函数
            self._update_bullets()
            #敌机移动函数
            self._update_aliens()
            #更新函数
            self._update_screen()
            #屏幕帧率
            self.clock.tick(self.settings.clock_tick)
            print(len(self.aliens))

    def _update_screen(self):
        """更新屏幕图像 切换至新屏幕"""
        # 背景色
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # 更新屏幕显示（让画面刷新）
        self.ship.blitme()
        #更新敌机
        self.aliens.draw(self.screen)
        # 每次循环时都重绘屏幕
        pygame.display.flip()

    def _check_events(self):
        """监听所有事件（键盘、鼠标、关闭窗口等）"""
        for event in pygame.event.get():
            # 如果用户点击了窗口右上角“关闭按钮”
            if event.type == pygame.QUIT:
                # 关闭 pygame 所有模块
                pygame.quit()
                # 退出 Python 程序
                sys.exit()

            elif event.type==pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type==pygame.KEYUP:
                self._check_keyup_event(event)
    
    def _check_keydown_events(self,event):
        """响应按下按键"""
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key==pygame.K_UP:
            self.ship.moving_up=True
        elif event.key==pygame.K_DOWN:
            self.ship.moving_down=True
        elif event.key==pygame.K_q:
            sys.exit()
        elif event.key==pygame.K_SPACE:
            self.fire_pressed = True
            self._fire_bullet()
            self.last_fire_time = time.time()

    def _check_keyup_event(self,event):
        """响应松开按键"""
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=False
        elif event.key==pygame.K_UP:
            self.ship.moving_up=False
        elif event.key==pygame.K_DOWN:
            self.ship.moving_down=False
        elif event.key==pygame.K_SPACE:
            self.fire_pressed = False

    def _update_auto_fire(self):
        """按住空格时持续发射子弹，避免卡死主循环。"""
        if self.fire_pressed and time.time() - self.last_fire_time >= 0.1:
            self._fire_bullet()
            self.last_fire_time = time.time()

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组了 bullets"""
        new_bullet=Bullet(self)
        self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹位置并删除已消失的子弹"""
        #更新子弹位置
        self.bullets.update()
        #删除已经消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <=0:
                self.bullets.remove(bullet)

    def _create_fleet(self):
        """创建一个敌机舰队"""
        #创建一个敌机
        #创建一个敌机，再不断添加，直到没有空间添加敌机为止
        #敌机的间距等于敌机的宽度
        alien=Alien(self)
        alien_width=alien.rect.width

        current_x=alien_width
        while current_x<(self.settings.screen_width -2 * alien_width):
            new_alien=Alien(self)
            new_alien.x=current_x
            new_alien.rect.x=current_x
            self.aliens.add(new_alien)
            current_x += 2 * alien_width

    def _update_aliens(self):
        """更新敌机舰队中所有敌机的位置"""
        #更新敌机位置
        self.aliens.update()
        #删除已经消失的敌机
        for alien in self.aliens.copy():
            if alien.rect.

# 如果这个文件是“直接运行”的，而不是被导入
if __name__ == "__main__":

    # 创建游戏对象
    ai = AlienInvasion()

    # 启动游戏
    ai.run_game()