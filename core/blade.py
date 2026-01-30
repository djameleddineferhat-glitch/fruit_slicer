import pygame
import math
from collections import deque


class Blade:
    def __init__(self):
        self.points = deque(maxlen=20)
        self.last_pos = None
        self.is_moving = False

        # Sons
        self.swipe_sounds = []
        self.impact_sounds = []
        self.swipe_index = 0
        self.impact_index = 0
        self.swipe_cooldown = 1
        self.min_swipe_distance = 500  # Distance min pour jouer un son
        self.last_sound_pos = None

        self.load_sounds()

    def load_sounds(self):
        for i in range(1, 5):
            try:
                swipe = pygame.mixer.Sound(f"asset/Blade/bamboo-swipe-{i}.wav")
                self.swipe_sounds.append(swipe)
            except:
                pass
            try:
                impact = pygame.mixer.Sound(f"asset/Blade/bamboo-impact-{i}.wav")
                self.impact_sounds.append(impact)
            except:
                pass

    def update(self, pos):
        """Ajoute un point si la souris a bougé."""
        if self.last_pos != pos:
            self.points.append(pos)

            # Vérifier si on a bougé assez pour jouer un son de swipe
            if self.last_sound_pos:
                dist = math.sqrt((pos[0] - self.last_sound_pos[0])**2 +
                               (pos[1] - self.last_sound_pos[1])**2)
                if dist >= self.min_swipe_distance:
                    self.play_swipe_sound()
                    self.last_sound_pos = pos
            else:
                self.last_sound_pos = pos

            self.last_pos = pos
            self.is_moving = True
        else:
            self.is_moving = False

    def play_swipe_sound(self):
        """Joue le prochain son de swipe."""
        if self.swipe_sounds:
            self.swipe_sounds[self.swipe_index].play()
            self.swipe_index = (self.swipe_index + 1) % len(self.swipe_sounds)

    def play_impact_sound(self):
        """Joue le prochain son d'impact."""
        if self.impact_sounds:
            self.impact_sounds[self.impact_index].play()
            self.impact_index = (self.impact_index + 1) % len(self.impact_sounds)

    def fade(self):
        """Retire les vieux points progressivement."""
        if len(self.points) > 0:
            self.points.popleft()
        # Reset la position du dernier son quand on arrête
        self.last_sound_pos = None

    def render(self, screen):
        if len(self.points) < 2:
            return

        points_list = list(self.points)
        for i in range(1, len(points_list)):
            thickness = max(1, int(5 * (i / len(points_list))))

            # Lueur bleue (dessous)
            if thickness > 2:
                pygame.draw.line(screen, (100, 150, 255),
                               points_list[i - 1], points_list[i], thickness + 2)

            # Ligne blanche (dessus)
            pygame.draw.line(screen, (255, 255, 255),
                           points_list[i - 1], points_list[i], thickness)

    def collides_with(self, x, y, radius):
        """Vérifie si la lame touche un cercle."""
        if not self.is_moving or len(self.points) < 2:
            return False

        points_list = list(self.points)
        for i in range(max(0, len(points_list) - 5), len(points_list) - 1):
            if self._line_circle_collision(points_list[i], points_list[i + 1], (x, y), radius):
                return True
        return False

    def _line_circle_collision(self, p1, p2, center, radius):
        """Vérifie collision ligne-cercle."""
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = center

        dx = x2 - x1
        dy = y2 - y1
        fx = x1 - cx
        fy = y1 - cy

        a = dx * dx + dy * dy
        if a == 0:
            return False

        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - radius * radius
        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False

        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        return (0 <= t1 <= 1) or (0 <= t2 <= 1)
