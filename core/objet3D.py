"""
Objets 3D avec rendu OpenGL (Fruits, Bombes, etc).
"""
import random
import math
from OpenGL.GL import *
from data.config import (
    SCREEN_WIDTH, GRAVITY,
    FRUIT_VELOCITY_X, FRUIT_VELOCITY_Y, FRUIT_ROTATION_SPEED,
    BOMB_VELOCITY_X, BOMB_VELOCITY_Y, BOMB_ROTATION_SPEED,
    CUT_VELOCITY_X, CUT_VELOCITY_Y, CUT_ROTATION_SPEED_X, CUT_ROTATION_SPEED_YZ,
    BORDER_VELOCITY_DAMPING
)

# Bordures latérales
BORDER_LEFT = 0
BORDER_RIGHT = SCREEN_WIDTH


# Couleurs de fallback pour chaque type (sans texture)
COLORS = {
    'apple': (1.0, 1.0, 1.0),
    'orange': (1.0, 1.0, 1.0),
    'watermelon': (1.0, 1.0, 1.0),
    'banana': (1.0, 1.0, 1.0),
    'chili': (1.0, 1.0, 1.0),
    'coconut': (1.0, 1.0, 1.0),
    'ice': (1.0, 1.0, 1.0),
    'bomb': (1.0, 1.0, 1.0),
}

# Rayon de collision (pixels)
RADIUS = {
    'apple': 30,
    'orange': 30,
    'watermelon': 40,
    'banana': 30,
    'chili': 25,
    'coconut': 35,
    'ice': 30,
    'bomb': 25,
}

# Échelle 3D pour le rendu
SCALE_3D = {
    'apple': 1.0,
    'orange': 1.0,
    'watermelon': 1.0,
    'banana': 1.0,
    'chili': 0.8,
    'coconut': 1.0,
    'ice': 1.0,
    'bomb': 1.3,
}

# Fruits qui ont un modèle -C2 séparé
FRUITS_WITH_C2 = ['banana', 'chili']

# Couleurs de splash pour chaque fruit (RGB 0-255)
SPLASH_COLORS = {
    'apple': (180, 230, 100),     # Vert clair
    'orange': (255, 165, 0),      # Orange
    'watermelon': (255, 100, 100), # Rouge clair
    'banana': (255, 225, 50),     # Jaune
    'chili': (180, 20, 20),       # Rouge foncé
    'coconut': (255, 255, 255),   # Blanc
    'ice': (150, 200, 255),       # Bleu clair
}


def screen_to_gl(x, y, screen_width, screen_height):
    """Convertit coordonnées écran (pixels) vers OpenGL."""
    fov_rad = math.radians(45.0)
    camera_distance = 10.0
    visible_height = 2.0 * camera_distance * math.tan(fov_rad / 2.0)
    visible_width = visible_height * (screen_width / screen_height)

    gl_x = (x / screen_width - 0.5) * visible_width
    gl_y = -(y / screen_height - 0.5) * visible_height
    return gl_x, gl_y


class CutFruitHalf:
    """Moitié d'un fruit coupé avec physique et rendu 3D."""

    def __init__(self, x, y, fruit_type, direction, model_cache, rotation, color, is_second_half=False):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        self.model_cache = model_cache
        self.color = color
        self.is_second_half = is_second_half

        # Direction: -1 = gauche, 1 = droite
        self.velocity_x = direction * random.uniform(*CUT_VELOCITY_X)
        self.velocity_y = random.uniform(*CUT_VELOCITY_Y)
        self.gravity = GRAVITY

        # Copier la rotation du fruit original
        self.rotation_x = rotation[0]
        self.rotation_y = rotation[1]
        self.rotation_z = rotation[2]

        # Rotation plus rapide après la coupe
        self.rotation_speed_x = direction * random.uniform(*CUT_ROTATION_SPEED_X)
        self.rotation_speed_y = random.uniform(*CUT_ROTATION_SPEED_YZ)
        self.rotation_speed_z = random.uniform(*CUT_ROTATION_SPEED_YZ)

        self.radius = RADIUS.get(fruit_type, 25)
        self.scale_3d = SCALE_3D.get(fruit_type, 1.0)
        self.offset_x = direction * 0.3

    def update(self, dt):
        # Facteur de temps (60 FPS de base)
        time_factor = dt * 60

        self.velocity_y += self.gravity * time_factor
        self.x += self.velocity_x * time_factor
        self.y += self.velocity_y * time_factor

        # Collision bordures gauche/droite
        if self.x - self.radius < BORDER_LEFT:
            self.x = BORDER_LEFT + self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING
        elif self.x + self.radius > BORDER_RIGHT:
            self.x = BORDER_RIGHT - self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING

        self.rotation_x += self.rotation_speed_x * time_factor
        self.rotation_y += self.rotation_speed_y * time_factor
        self.rotation_z += self.rotation_speed_z * time_factor

    def render(self, screen):
        import pygame
        color_255 = tuple(int(c * 255) for c in self.color)
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color_255, 150), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))

    def render_3d(self, screen_width, screen_height):
        gl_x, gl_y = screen_to_gl(self.x, self.y, screen_width, screen_height)

        glPushMatrix()
        glTranslatef(gl_x, gl_y, 0)

        glScalef(self.scale_3d, self.scale_3d, self.scale_3d)
        glTranslatef(self.offset_x, 0, 0)

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)

        glColor3f(*self.color)

        # Utiliser -C ou -C2
        if self.is_second_half and self.fruit_type in FRUITS_WITH_C2:
            model_name = f"{self.fruit_type.capitalize()}-C2"
        else:
            model_name = f"{self.fruit_type.capitalize()}-C"

        if self.model_cache and self.model_cache.has_model(model_name):
            glCallList(self.model_cache.get_display_list(model_name))
        else:
            self._render_sphere()

        glPopMatrix()

    def _render_sphere(self):
        from OpenGL.GLU import gluNewQuadric, gluSphere, gluDeleteQuadric
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.4, 12, 12)
        gluDeleteQuadric(quadric)

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 100


class Fruit3D:
    """Fruit avec rendu 3D et physique 2D pour collision."""

    TYPES = ['apple', 'orange', 'watermelon', 'banana']

    def __init__(self, x, y, fruit_type=None, model_cache=None):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type if fruit_type else random.choice(self.TYPES)
        self.model_cache = model_cache

        # Physique
        self.velocity_x = random.uniform(*FRUIT_VELOCITY_X)
        self.velocity_y = random.uniform(*FRUIT_VELOCITY_Y)
        self.gravity = GRAVITY

        # Rotation 3D
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rotation_z = random.uniform(0, 360)
        self.rotation_speed_x = random.uniform(*FRUIT_ROTATION_SPEED)
        self.rotation_speed_y = random.uniform(*FRUIT_ROTATION_SPEED)
        self.rotation_speed_z = random.uniform(*FRUIT_ROTATION_SPEED)

        # État
        self.is_cut = False
        self.radius = RADIUS.get(self.fruit_type, 30)
        self.scale_3d = SCALE_3D.get(self.fruit_type, 1.0)
        self.color = COLORS.get(self.fruit_type, (1.0, 1.0, 1.0))

    def update(self, dt):
        # Facteur de temps (60 FPS de base)
        time_factor = dt * 60

        self.velocity_y += self.gravity * time_factor
        self.x += self.velocity_x * time_factor
        self.y += self.velocity_y * time_factor

        # Collision bordures gauche/droite
        if self.x - self.radius < BORDER_LEFT:
            self.x = BORDER_LEFT + self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING
        elif self.x + self.radius > BORDER_RIGHT:
            self.x = BORDER_RIGHT - self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING

        self.rotation_x += self.rotation_speed_x * time_factor
        self.rotation_y += self.rotation_speed_y * time_factor
        self.rotation_z += self.rotation_speed_z * time_factor

        self.rotation_x %= 360
        self.rotation_y %= 360
        self.rotation_z %= 360

    def render(self, screen):
        import pygame
        color_255 = tuple(int(c * 255) for c in self.color)

        if not self.is_cut:
            pygame.draw.circle(screen, color_255, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x) - 8, int(self.y) - 8), 8)

    def render_3d(self, screen_width, screen_height):
        if self.is_cut:
            return

        gl_x, gl_y = screen_to_gl(self.x, self.y, screen_width, screen_height)

        glPushMatrix()
        glTranslatef(gl_x, gl_y, 0)

        glScalef(self.scale_3d, self.scale_3d, self.scale_3d)

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)

        glColor3f(*self.color)

        model_name = self.fruit_type.capitalize()
        if self.model_cache and self.model_cache.has_model(model_name):
            glCallList(self.model_cache.get_display_list(model_name))
        else:
            self._render_sphere()

        glPopMatrix()

    def _render_sphere(self):
        from OpenGL.GLU import gluNewQuadric, gluSphere, gluDeleteQuadric
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.5, 16, 16)
        gluDeleteQuadric(quadric)

    def cut(self):
        self.is_cut = True
        rotation = (self.rotation_x, self.rotation_y, self.rotation_z)

        left_half = CutFruitHalf(
            self.x, self.y, self.fruit_type,
            direction=-1,
            model_cache=self.model_cache,
            rotation=rotation,
            color=self.color,
            is_second_half=False
        )

        right_half = CutFruitHalf(
            self.x, self.y, self.fruit_type,
            direction=1,
            model_cache=self.model_cache,
            rotation=rotation,
            color=self.color,
            is_second_half=True
        )

        return [left_half, right_half]

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 100


class Bomb3D:
    """Bombe avec rendu 3D OpenGL."""

    fuse_sound = None

    def __init__(self, x, y, model_cache=None):
        import pygame

        self.x = x
        self.y = y
        self.model_cache = model_cache

        # Physique
        self.velocity_x = random.uniform(*BOMB_VELOCITY_X)
        self.velocity_y = random.uniform(*BOMB_VELOCITY_Y)
        self.gravity = GRAVITY

        # Rotation 3D
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rotation_z = random.uniform(0, 360)
        self.rotation_speed_x = random.uniform(*BOMB_ROTATION_SPEED)
        self.rotation_speed_y = random.uniform(*BOMB_ROTATION_SPEED)
        self.rotation_speed_z = random.uniform(*BOMB_ROTATION_SPEED)

        self.is_exploded = False
        self.radius = RADIUS.get('bomb', 25)
        self.scale_3d = SCALE_3D.get('bomb', 1.0)
        self.color = COLORS.get('bomb', (1.0, 1.0, 1.0))
        self.channel = None

        # Son de mèche
        if Bomb3D.fuse_sound is None:
            try:
                Bomb3D.fuse_sound = pygame.mixer.Sound("asset/Sound object/Bomb-Fuse.wav")
            except:
                pass

        if Bomb3D.fuse_sound:
            self.channel = Bomb3D.fuse_sound.play(-1)

    def update(self, dt):
        # Facteur de temps (60 FPS de base)
        time_factor = dt * 60

        self.velocity_y += self.gravity * time_factor
        self.x += self.velocity_x * time_factor
        self.y += self.velocity_y * time_factor

        # Collision bordures gauche/droite
        if self.x - self.radius < BORDER_LEFT:
            self.x = BORDER_LEFT + self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING
        elif self.x + self.radius > BORDER_RIGHT:
            self.x = BORDER_RIGHT - self.radius
            self.velocity_x = -self.velocity_x * BORDER_VELOCITY_DAMPING

        self.rotation_x += self.rotation_speed_x * time_factor
        self.rotation_y += self.rotation_speed_y * time_factor
        self.rotation_z += self.rotation_speed_z * time_factor

    def render(self, screen):
        import pygame

        if self.is_exploded:
            pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), self.radius + 20)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius + 10)
        else:
            pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), self.radius)
            pygame.draw.line(screen, (139, 69, 19),
                           (int(self.x), int(self.y) - self.radius),
                           (int(self.x) + 10, int(self.y) - self.radius - 15), 3)
            pygame.draw.circle(screen, (255, 200, 0),
                             (int(self.x) + 10, int(self.y) - self.radius - 15), 5)

    def render_3d(self, screen_width, screen_height):
        if self.is_exploded:
            return

        gl_x, gl_y = screen_to_gl(self.x, self.y, screen_width, screen_height)

        glPushMatrix()
        glTranslatef(gl_x, gl_y, 0)

        glScalef(self.scale_3d, self.scale_3d, self.scale_3d)

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)

        glColor3f(*self.color)

        if self.model_cache and self.model_cache.has_model('Bomb'):
            glCallList(self.model_cache.get_display_list('Bomb'))
        else:
            self._render_sphere()

        glPopMatrix()

    def _render_sphere(self):
        from OpenGL.GLU import gluNewQuadric, gluSphere, gluDeleteQuadric
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.5, 16, 16)
        gluDeleteQuadric(quadric)

    def explode(self):
        self.is_exploded = True
        self.stop_fuse()

    def stop_fuse(self):
        if self.channel:
            self.channel.stop()
            self.channel = None

    def is_off_screen(self, screen_height):
        off = self.y > screen_height + 100
        if off:
            self.stop_fuse()
        return off
