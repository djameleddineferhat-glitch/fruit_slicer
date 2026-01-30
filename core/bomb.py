import pygame
import random


class Bomb:
    # Son de mèche partagé
    fuse_sound = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-24, -14)
        self.gravity = 0.5
        self.rotation = 0
        self.is_exploded = False
        self.radius = 25
        self.channel = None

        # Charger et jouer le son de mèche
        if Bomb.fuse_sound is None:
            try:
                Bomb.fuse_sound = pygame.mixer.Sound("asset/Sound object/Bomb-Fuse.wav")
            except:
                pass

        if Bomb.fuse_sound:
            self.channel = Bomb.fuse_sound.play(-1)  # Loop infini

    def update(self, dt):
        # Facteur de temps (60 FPS de base)
        time_factor = dt * 60

        self.velocity_y += self.gravity * time_factor
        self.x += self.velocity_x * time_factor
        self.y += self.velocity_y * time_factor
        self.rotation += 3 * time_factor

    def render(self, screen):
        if self.is_exploded:
            # Explosion
            pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), self.radius + 20)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius + 10)
        else:
            # Bombe noire
            pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), self.radius)
            # Mèche
            pygame.draw.line(screen, (139, 69, 19),
                           (int(self.x), int(self.y) - self.radius),
                           (int(self.x) + 10, int(self.y) - self.radius - 15), 3)
            # Étincelle
            pygame.draw.circle(screen, (255, 200, 0),
                             (int(self.x) + 10, int(self.y) - self.radius - 15), 5)

    def explode(self):
        self.is_exploded = True
        self.stop_fuse()

    def stop_fuse(self):
        """Arrête le son de mèche."""
        if self.channel:
            self.channel.stop()
            self.channel = None

    def is_off_screen(self, screen_height):
        off = self.y > screen_height + 100
        if off:
            self.stop_fuse()
        return off
