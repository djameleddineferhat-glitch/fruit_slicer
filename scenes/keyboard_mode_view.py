import pygame
import random
import time
import string
import math
from core.scene_manager import Scene
from core.fruit import Fruit
from core.bomb import Bomb
from core.objet3D import Fruit3D, Bomb3D, SPLASH_COLORS
from core.splash import Splash
from core.blade import Blade
from core.combo import ComboSystem
from core.model_cache import ModelCache
from data.scores import Score
from ui.hud import render_hud
from data.config import (
    SCREEN_HEIGHT, SCREEN_WIDTH, STARTING_LIVES, BOMB_CHANCE, POINTS_PER_FRUIT,
    get_spawn_interval, OPENGL_ENABLED, FRUIT_MODELS, FRUIT_MODELS_CUT, FRUIT_MODELS_CUT2,
    FRUIT_SCALES, TEXTURE_ATLAS_PATH, BOMB_MODEL, NORMAL_SPEED
)


class NormalGameScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        # Background
        self.background = pygame.image.load("asset/Background/Game Background.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Musique de fond (Keyboard Mode)
        self.ost_path = "asset/Sound Menu/keyboard_background_ost.ogg"

        # Sons
        try:
            self.throw_fruit_sound = pygame.mixer.Sound("asset/Sound object/Throw-fruit.wav")
        except:
            self.throw_fruit_sound = None
        try:
            self.throw_bomb_sound = pygame.mixer.Sound("asset/Sound object/Throw-bomb.wav")
        except:
            self.throw_bomb_sound = None
        try:
            self.bomb_explode_sound = pygame.mixer.Sound("asset/Sound object/Bomb-explode.wav")
        except:
            self.bomb_explode_sound = None

        # Sons d'impact
        self.impact_sounds = {}
        impact_files = {
            'apple': 'asset/Impact/Impact-Apple.wav',
            'orange': 'asset/Impact/Impact-Orange.wav',
            'watermelon': 'asset/Impact/Impact-Watermelon.wav',
            'banana': 'asset/Impact/Impact-Banana-Chili.wav', 
            'chili': 'asset/Impact/Impact-Banana-Chili.wav',  
            'coconut': 'asset/Impact/Impact-Coconut.wav',
            'ice': 'asset/Impact/Impact-Ice.mp3',
        }
        for fruit_type, path in impact_files.items():
            try:
                self.impact_sounds[fruit_type] = pygame.mixer.Sound(path)
            except:
                self.impact_sounds[fruit_type] = None

        self.model_cache = None
        self.use_3d = OPENGL_ENABLED and manager.gl_renderer is not None

        if self.use_3d:
            self._init_model_cache()

        self.paused = False
        self.game_time = 0
        self.freeze_timer = 0
        self.frenzy_timer = 0
        self.pause_font = pygame.font.SysFont("Arial", 80, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 40)
        self.key_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 60, 20, 40, 40)
        
        self.reset()

    def _init_model_cache(self):
        self.model_cache = ModelCache()
        self.model_cache.load_texture(TEXTURE_ATLAS_PATH)
        for fruit_type, model_path in FRUIT_MODELS.items():
            scale = FRUIT_SCALES.get(fruit_type, 1.0)
            self.model_cache.load_model(fruit_type.capitalize(), model_path, custom_scale=scale)
        for fruit_type, model_path in FRUIT_MODELS_CUT.items():
            scale = FRUIT_SCALES.get(fruit_type, 1.0)
            self.model_cache.load_model(f"{fruit_type.capitalize()}-C", model_path, custom_scale=scale)
        for fruit_type, model_path in FRUIT_MODELS_CUT2.items():
            scale = FRUIT_SCALES.get(fruit_type, 1.0)
            self.model_cache.load_model(f"{fruit_type.capitalize()}-C2", model_path, custom_scale=scale)
        self.model_cache.load_model('Bomb', BOMB_MODEL, custom_scale=1.0)

    def reset(self):
        self.score = Score()
        self.lives = STARTING_LIVES
        self.fruits = []
        self.cut_halves = []
        self.bombs = []
        self.splashes = []
        self.blade = Blade()
        self.combo_system = ComboSystem()
        self.spawn_timer = 0
        self.explosion_delay = 0
        self.game_time = 0
        self.freeze_timer = 0
        self.frenzy_timer = 0
        self.paused = False
        self.game_over = False

    def on_enter(self):
        self.reset()
        try:
            pygame.mixer.music.load(self.ost_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1, start=5.0)
        except:
            print(f"Erreur : Impossible de lire {self.ost_path}")

    def on_exit(self):
        pygame.mixer.music.stop()
        for bomb in self.bombs:
            bomb.stop_fuse()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.game_over:
                        self.paused = not self.paused
                        if self.paused: pygame.mixer.music.pause()
                        else: pygame.mixer.music.unpause()
                    continue
                
                if not self.paused and not self.game_over:
                    char_pressed = event.unicode.upper()
                    if char_pressed in string.ascii_uppercase:
                        self.check_keyboard_cut(char_pressed)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.game_over:
                    self.handle_game_over_click(mouse_pos)
                    return
                if not self.paused and self.pause_button_rect.collidepoint(mouse_pos):
                    self.paused = True
                    pygame.mixer.music.pause()
                    return
                if self.paused:
                    self.handle_pause_click(mouse_pos)

    def check_keyboard_cut(self, char):
        for fruit in self.fruits:
            if not fruit.is_cut and hasattr(fruit, 'key_char') and fruit.key_char == char:
                self.apply_fruit_cut(fruit)
                return

        for bomb in self.bombs:
            if not bomb.is_exploded and hasattr(bomb, 'key_char') and bomb.key_char == char:
                self.apply_bomb_explosion(bomb)
                return

    def apply_fruit_cut(self, fruit):
        if fruit.fruit_type == 'ice':
            self.freeze_timer = 5.0
            self.frenzy_timer = 0
        elif fruit.fruit_type == 'chili':
            self.frenzy_timer = 5.0
            self.freeze_timer = 0

        halves = fruit.cut()
        if halves: self.cut_halves.extend(halves)
        self.score.add(POINTS_PER_FRUIT)
        self.combo_system.add_hit()
        splash_color = SPLASH_COLORS.get(fruit.fruit_type, (255, 255, 255))
        self.splashes.append(Splash(fruit.x, fruit.y, splash_color))
        
        impact_sound = self.impact_sounds.get(fruit.fruit_type)
        if impact_sound: impact_sound.play()

    def apply_bomb_explosion(self, bomb):
        bomb.explode()
        if self.bomb_explode_sound: self.bomb_explode_sound.play()
        self.lives = 0
        self.explosion_delay = 0.5

    def handle_pause_click(self, pos):
        center_x = SCREEN_WIDTH // 2
        btn_continue = pygame.Rect(center_x - 100, 300, 200, 50)
        btn_restart = pygame.Rect(center_x - 100, 370, 200, 50)
        btn_menu = pygame.Rect(center_x - 100, 440, 200, 50)
        if btn_continue.collidepoint(pos):
            self.paused = False
            pygame.mixer.music.unpause()
        elif btn_restart.collidepoint(pos):
            self.reset()
            pygame.mixer.music.play(-1, start=5.0)
        elif btn_menu.collidepoint(pos):
            pygame.mixer.music.stop()
            self.manager.change_scene('menu')

    def handle_game_over_click(self, pos):
        center_x = SCREEN_WIDTH // 2
        btn_retry = pygame.Rect(center_x - 100, 350, 200, 50)
        btn_menu = pygame.Rect(center_x - 100, 420, 200, 50)
        if btn_retry.collidepoint(pos):
            self.reset()
            pygame.mixer.music.play(-1, start=5.0)
        elif btn_menu.collidepoint(pos):
            pygame.mixer.music.stop()
            self.manager.change_scene('menu')

    def update(self, dt):
        if self.paused: return
        
        if self.lives <= 0:
            if not self.game_over:
                self.game_over = True
                pygame.mixer.music.stop()
                self.manager.shared_data['score'] = self.score.current
                self.manager.shared_data['mode'] = 'clavier'
                self.manager.change_scene('game_over')
            return

        time_mult = 1.0
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            time_mult = 0.2
        if self.frenzy_timer > 0:
            self.frenzy_timer -= dt
            time_mult = 1.1

        self.game_time += dt
        
        if hasattr(self.blade, 'points') and len(self.blade.points) > 0:
            try:
                self.blade.fade()
            except AttributeError:
                if isinstance(self.blade.points, list):
                    if len(self.blade.points) > 0: self.blade.points.pop(0)
                else:
                    self.blade.points.clear()
        
        self.combo_system.update(dt)
        
        self.spawn_timer += dt
        spawn_interval = get_spawn_interval(self.score.current)
        if self.frenzy_timer > 0: spawn_interval *= 0.4

        if self.spawn_timer >= spawn_interval:
            self.spawn_objects()
            self.spawn_timer = 0

        effective_dt = dt * time_mult * NORMAL_SPEED

        for fruit in self.fruits[:]:
            fruit.update(effective_dt)
            if fruit.is_off_screen(SCREEN_HEIGHT):
                if not fruit.is_cut and fruit.fruit_type not in ['ice', 'chili']:
                    self.lives -= 1
                    self.combo_system.reset_combo()
                self.fruits.remove(fruit)
        for half in self.cut_halves[:]:
            half.update(effective_dt)
            if half.is_off_screen(SCREEN_HEIGHT): self.cut_halves.remove(half)
        for bomb in self.bombs[:]:
            bomb.update(effective_dt)
            if bomb.is_off_screen(SCREEN_HEIGHT): self.bombs.remove(bomb)
        for splash in self.splashes[:]:
            splash.update(dt)
            if splash.is_done: self.splashes.remove(splash)

    def render_background(self, surface):
        surface.blit(self.background, (0, 0))
        for splash in self.splashes: splash.render(surface)

    def render_overlay(self, surface):
        if not self.use_3d:
            for fruit in self.fruits: fruit.render(surface)
            for bomb in self.bombs: bomb.render(surface)
        
        ticks = pygame.time.get_ticks()
        for obj in self.fruits + self.bombs:
            if hasattr(obj, 'key_char') and not getattr(obj, 'is_cut', False) and not getattr(obj, 'is_exploded', False):
                circle_color = (0, 0, 0, 180)
                text_color = (255, 255, 0)
                radius = 22
                offset_x = 0
                offset_y = 0

                is_bomb = isinstance(obj, (Bomb, Bomb3D))
                
                if is_bomb:
                    circle_color = (150, 0, 0, 200)
                    text_color = (255, 255, 255)
                    radius = 22 + int(math.sin(ticks * 0.01) * 4)
                    offset_x = random.randint(-2, 2)
                    offset_y = random.randint(-2, 2)
                elif hasattr(obj, 'fruit_type'):
                    if obj.fruit_type == 'ice':
                        circle_color = (0, 150, 255, 200)
                        text_color = (255, 255, 255)
                        radius = 22 + int(math.sin(ticks * 0.005) * 2)
                    elif obj.fruit_type == 'chili':
                        circle_color = (255, 60, 0, 200)
                        text_color = (255, 255, 0)
                        radius = 22 + int(math.sin(ticks * 0.015) * 3)

                indicator_pos = (int(obj.x) + offset_x, int(obj.y - 65) + offset_y)
                temp_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, circle_color, (radius, radius), radius)
                surface.blit(temp_surface, (indicator_pos[0]-radius, indicator_pos[1]-radius))
                pygame.draw.circle(surface, (255, 255, 255), indicator_pos, radius, 2)
                
                char_surf = self.key_font.render(obj.key_char, True, text_color)
                surface.blit(char_surf, (indicator_pos[0] - char_surf.get_width()//2, indicator_pos[1] - char_surf.get_height()//2))

        self.blade.render(surface)
        mins, secs = int(self.game_time // 60), int(self.game_time % 60)
        timer_text = f"{mins:02d}:{secs:02d}"
        
        status_text = self.combo_system.get_display_text()
        if self.freeze_timer > 0: status_text = "FREEZE !"
        if self.frenzy_timer > 0: status_text = "FRENZY !"

        render_hud(surface, self.score.current, self.lives, status_text, self.combo_system.get_progress(), timer_text)
        
        if not self.game_over:
            pygame.draw.rect(surface, (200, 200, 200), self.pause_button_rect, border_radius=5)
            pygame.draw.rect(surface, (50, 50, 50), (SCREEN_WIDTH - 50, 28, 5, 24))
            pygame.draw.rect(surface, (50, 50, 50), (SCREEN_WIDTH - 38, 28, 5, 24))

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            pause_txt = self.pause_font.render("PAUSE - CLAVIER", True, (255, 255, 255))
            surface.blit(pause_txt, (SCREEN_WIDTH // 2 - pause_txt.get_width() // 2, 150))
            self.draw_button(surface, "Continuer", 300)
            self.draw_button(surface, "Recommencer", 370)
            self.draw_button(surface, "Retour", 440)

    def draw_button(self, surface, text, y):
        center_x = SCREEN_WIDTH // 2
        rect = pygame.Rect(center_x - 100, y, 200, 50)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10)
        txt_surf = self.button_font.render(text, True, (255, 255, 255))
        surface.blit(txt_surf, (center_x - txt_surf.get_width() // 2, y + 5))

    def render(self, surface):
        self.render_background(surface)
        self.render_overlay(surface)

    def render_3d(self):
        if not self.use_3d or self.paused: return
        width, height = SCREEN_WIDTH, SCREEN_HEIGHT
        for fruit in self.fruits:
            if not fruit.is_cut: fruit.render_3d(width, height)
        for half in self.cut_halves: half.render_3d(width, height)
        for bomb in self.bombs:
            if not bomb.is_exploded: bomb.render_3d(width, height)

    def spawn_objects(self):
        used_keys = [f.key_char for f in self.fruits if hasattr(f, 'key_char')]
        used_keys += [b.key_char for b in self.bombs if hasattr(b, 'key_char')]

        for _ in range(2):
            x = random.randint(100, SCREEN_WIDTH - 100)
            rand_val = random.random()

            available_keys = [c for c in string.ascii_uppercase if c not in used_keys]
            if not available_keys: break
            chosen_key = random.choice(available_keys)
            used_keys.append(chosen_key)

            if rand_val < BOMB_CHANCE:
                obj = Bomb3D(x, SCREEN_HEIGHT + 50, model_cache=self.model_cache) if self.use_3d else Bomb(x, SCREEN_HEIGHT + 50)
                obj.key_char = chosen_key
                self.bombs.append(obj)
                if self.throw_bomb_sound: self.throw_bomb_sound.play()
            elif rand_val < (BOMB_CHANCE * 2):
                obj = Fruit3D(x, SCREEN_HEIGHT + 50, model_cache=self.model_cache) if self.use_3d else Fruit(x, SCREEN_HEIGHT + 50)
                obj.fruit_type = random.choice(['ice', 'chili'])
                obj.key_char = chosen_key
                self.fruits.append(obj)
                if self.throw_fruit_sound: self.throw_fruit_sound.play()
            else:
                obj = Fruit3D(x, SCREEN_HEIGHT + 50, model_cache=self.model_cache) if self.use_3d else Fruit(x, SCREEN_HEIGHT + 50)
                obj.key_char = chosen_key
                self.fruits.append(obj)
                if self.throw_fruit_sound: self.throw_fruit_sound.play()

    def check_cuts(self):
        pass