"""
Effet de splash quand un fruit est coupé.
"""
import pygame
import random

# Taille du splash en pixels
SPLASH_SIZE = 150


class Splash:
    """Splash coloré qui apparaît quand un fruit est coupé."""

    # Images de splash chargées une seule fois
    images = None

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color  # RGB tuple (0-255)
        self.alpha = 255
        self.fade_speed = 255 / 5.0  # Disparaît en 5 secondes
        self.is_done = False

        # Charger les images si pas encore fait
        if Splash.images is None:
            Splash.images = []
            for i in [1, 2, 3, 4, 5, 6]:
                try:
                    if i == 4:
                        img = pygame.image.load(f"asset/Splash/Slash-4.png").convert_alpha()
                    else:
                        img = pygame.image.load(f"asset/Splash/Splash-{i}.png").convert_alpha()
                    # Redimensionner l'image
                    img = pygame.transform.scale(img, (SPLASH_SIZE, SPLASH_SIZE))
                    Splash.images.append(img)
                except:
                    pass

        # Choisir une image au hasard
        if Splash.images:
            self.original_image = random.choice(Splash.images)
            self.image = self._tint_image(self.original_image, self.color)
            # Centrer l'image sur la position
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image = None
            self.is_done = True

    def _tint_image(self, image, color):
        """Teinte une image blanche avec la couleur donnée."""
        # Créer une copie
        tinted = image.copy()

        # Créer une surface de couleur
        color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        color_surface.fill((*color, 255))

        # Appliquer la teinte avec BLEND_MULT
        tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return tinted

    def update(self, dt):
        """Met à jour l'alpha du splash."""
        self.alpha -= self.fade_speed * dt
        if self.alpha <= 0:
            self.alpha = 0
            self.is_done = True

    def render(self, surface):
        """Dessine le splash sur la surface."""
        if self.image and not self.is_done:
            # Appliquer l'alpha
            temp_image = self.image.copy()
            temp_image.set_alpha(int(self.alpha))
            surface.blit(temp_image, self.rect)
