import sys          # 用来安全退出程序
import pygame       # 导入 pygame 游戏库
from settings import Settings   #导入设置
from ship import Ship   #导入飞机
from bullet import Bullet   #导入子弹
import time
from time import sleep
from alien import Alien
from alien_bullet import AlienBullet
from game_stats import GameStats
from button import Button

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
        self.ship_group = pygame.sprite.GroupSingle(self.ship)

        self.bullets=pygame.sprite.Group()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.aliens=pygame.sprite.Group()

        self.alien_bullets=pygame.sprite.Group()
        
        self._create_fleet()

        #创建一个用于存储游戏统计信息的实例
        self.stats=GameStats(self)

        #游戏启动后处于活动状态
        self.game_active=False

        #创建一个play按钮
        self.play_button=Button(self,"play")
        self.paused=False

    def run_game(self):
        """开始游戏主循环（游戏运行的核心）"""

        # 无限循环：游戏会一直运行，直到你手动退出
        while True:
            # 监听函数
            self._check_events()
            if self.paused==True:
                # 移动函数
                self.ship.update()
                # 按住空格时自动发射子弹
                self._update_auto_fire()
                #子弹删除函数
                self._update_bullets()
                #敌机移动与开火函数
                self._update_aliens()
                #敌机子弹删除函数
                self._update_alien_bullets()
            #更新函数
            self._update_screen()
            #屏幕帧率
            self.clock.tick(self.settings.clock_tick)

    def _update_screen(self):
        """更新屏幕图像 切换至新屏幕"""
        # 背景色
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for alien_bullet in self.alien_bullets.sprites():
            alien_bullet.draw_alien_bullet()
        # 更新屏幕显示（让画面刷新）
        self.ship_group.draw(self.screen)
        #更新敌机
        self.aliens.draw(self.screen)
        #如果游戏处于非活动状态，就绘制play按钮
        if not self.game_active:
            self.play_button.draw_button()
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

            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
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
        elif event.key==pygame.K_LSHIFT:
            self.settings.ship_speed=2
        elif event.key==pygame.K_p:
            if self.paused==False:
                self.paused=True
            elif self.paused==True:
                self.paused=False

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
        elif event.key==pygame.K_LSHIFT:
            self.settings.ship_speed=5

    def _update_auto_fire(self):
        """按住空格时持续发射子弹，避免卡死主循环"""
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
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        """响应子弹和敌机的碰撞"""
        #删除发生碰撞的子弹和敌机
        collisions=pygame.sprite.groupcollide(
            self.bullets,self.aliens,True,True)

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
        """更新敌机舰队并在条件满足时发射子弹"""
        # 逐个敌机更新，避免 Group.update 把返回值吞掉
        for alien in self.aliens.sprites():
            fire_signal = alien.update()
            if fire_signal == "FIRE":
                self.alien_bullets.add(AlienBullet(self, alien))

        # 删除已经离开屏幕的敌机
        for alien in self.aliens.copy():
            if alien.rect.right < 0 or alien.rect.left > self.settings.screen_width:
                self.aliens.remove(alien)
        
        #如果敌机和自机发生碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()

    def _update_alien_bullets(self):
        """更新敌机子弹位置并删除已消失的子弹"""
        #更新子弹位置
        self.alien_bullets.update()
        #删除已经消失的子弹
        for bullet in self.alien_bullets.copy():
            if bullet.rect.bottom <=0 :
                self.alien_bullets.remove(bullet)
        self._check_bullet_player_collisions()

    def _check_bullet_player_collisions(self):
        """响应敌机子弹和自机的碰撞"""
        if pygame.sprite.spritecollideany(self.ship,self.alien_bullets):
            self._ship_hit()
        
    def _ship_hit(self):
        """响应自机和敌机的碰撞"""
        if self.stats.ships_left>0:
            #将 ship_left 减1
            self.stats.ships_left -= 1

            #清空敌机子弹和自机子弹列表
            self.bullets.empty()
            self.alien_bullets.empty()

            #创建一个新的自机，并将自机放在屏幕底部中央
            self.ship.center_ship()

            #暂停
            sleep(0.5)
        else:
            self.game_active=False
            pygame.mouse.set_visible(True)
            self.paused=False

    def _check_play_button(self,mouse_pos):
        """在玩家单击play按钮时开始新游戏"""
        if self.play_button.rect.collidepoint(mouse_pos):
            button_clicked=self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.game_active:
                #重置游戏的统计信息
                self.stats.reset_stats()
                self.game_active=True
                #清空列表：敌机，子弹，敌机子弹
                self.alien_bullets.empty()
                self.aliens.empty()
                self.bullets.empty()
                #创建一个新的敌机舰队，并使自机放置在屏幕底部的中央
                self._create_fleet()
                self.ship.center_ship()
                #隐藏光标
                pygame.mouse.set_visible(False)
                self.paused=True

# 如果这个文件是“直接运行”的，而不是被导入
if __name__ == "__main__":

    # 创建游戏对象
    ai = AlienInvasion()

    # 启动游戏
    ai.run_game()