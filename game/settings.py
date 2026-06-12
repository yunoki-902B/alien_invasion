class Settings:
    """Game settings."""

    def __init__(self):
        # Screen settings
        self.screen_width = 600
        self.screen_height = 800
        self.bg_color = (130, 230, 230)

        # Framerate
        self.clock_tick = 60

        # Ship settings
        self.ship_speed = 5

        # Bullet settings
        self.bullet_speed = 7
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.max_bullets = 3

        # Alien settings
        self.alien_speed = 2

        # Enemy bullet settings (reserved for future use)
        self.alien_bullet_speed = 8
        self.alien_bullet_width = 3
        self.alien_bullet_height = 3
        self.alien_bullet_color = (200, 0, 0)
