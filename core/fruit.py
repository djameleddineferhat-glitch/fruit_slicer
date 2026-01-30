import pygame
import random


FRUIT_COLORS = {
    'apple': (255, 0, 0),
    'orange': (255, 165, 0),
    'watermelon': (0, 255, 0),
    'banana': (255, 255, 0),
    'ice': (173, 216, 230),
    'chili': (139, 0, 0)
}


class Fruit:
    TYPES = ['apple', 'orange', 'watermelon', 'banana', 'ice', 'chili']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fruit_type = random.choice(self.TYPES)
        self.velocity_x = random.uniform(-8, 8)
        self.velocity_y = random.uniform(-20, -24)
        self.gravity = 0.5
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.is_cut = False
        self.radius = 30
        self.color = FRUIT_COLORS.get(self.fruit_type, (255, 255, 255))

    def update(self, dt):
        # Facteur de temps (60 FPS de base)
        time_factor = dt * 60

        self.velocity_y += self.gravity * time_factor
        self.x += self.velocity_x * time_factor
        self.y += self.velocity_y * time_factor
        self.rotation += self.rotation_speed * time_factor

    def render(self, screen):
        if self.is_cut:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 100), (self.radius, self.radius), self.radius)
            screen.blit(s, (self.x - self.radius, self.y - self.radius))
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x) - 8, int(self.y) - 8), 8)

    def cut(self):
        self.is_cut = True
        return []  # Pas de moitiés en mode 2D

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 100