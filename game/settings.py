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
        # Ship speed in pixels per second.
        self.ship_speed = 300

        # Bullet settings
        # Speed in pixels per second.
        self.bullet_speed = 480
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.shot_damage = 20

        # Player health settings
        self.player_max_health = 100
        self.player_lives = 3
        self.player_level_max = 10
        self.level_exp_requirements = [50, 70, 80, 120, 100, 100, 100, 100, 150]
        # Level 10 is max, no further requirement is needed.

        # Reward granted when an alien is destroyed.
        self.alien_exp_reward = 10

        # Alien settings
        # Speed in pixels per second.
        self.alien_speed = 240
        self.alien_name = "Drifter"
        self.alien_max_health = 40

        # Enemy bullet settings.
        # Speeds are pixels per second.
        self.alien_bullet_speed = 240
        self.alien_bullet_width = 3
        self.alien_bullet_height = 3
        self.alien_bullet_color = (200, 0, 0)
        self.alien_fire_interval = 1.0
