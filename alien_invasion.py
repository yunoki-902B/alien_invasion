import sys          # 用来安全退出程序
import pygame       # 导入 pygame 游戏库
from settings import Settings

class AlienInvasion:
    """管理整个游戏的主类"""

    def __init__(self):
        """初始化游戏，并创建游戏窗口"""

        # 初始化 pygame 所有模块（必须做）
        pygame.init()

        # 创建游戏窗口
        # 注意：set_mode 需要用“双括号”传入宽高

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(self.settings.screen_width,
                                              self.settings.screen_height)

        # 设置窗口标题
        pygame.display.set_caption("Alien Invasion")
        # 设置背景色
        self.bg_color = (230,230,230)

    def run_game(self):
        """开始游戏主循环（游戏运行的核心）"""

        # 无限循环：游戏会一直运行，直到你手动退出
        while True:

            # 监听所有事件（键盘、鼠标、关闭窗口等）
            for event in pygame.event.get():

                # 如果用户点击了窗口右上角“关闭按钮”
                if event.type == pygame.QUIT:

                    # 关闭 pygame 所有模块
                    pygame.quit()

                    # 退出 Python 程序
                    sys.exit()

            # 每次循环时都重绘屏幕
            self.screen.fill(self.settings.bg_color)

            # 更新屏幕显示（让画面刷新）
            pygame.display.flip()
            self.clock.tick(self.settings.clock_tick)


# 如果这个文件是“直接运行”的，而不是被导入
if __name__ == "__main__":

    # 创建游戏对象
    ai = AlienInvasion()

    # 启动游戏
    ai.run_game()