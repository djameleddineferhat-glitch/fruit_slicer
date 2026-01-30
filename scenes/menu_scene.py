import pygame
import json
import os
from core.scene_manager import Scene
from ui.menu import Button

class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        # Background
        self.background = pygame.image.load("asset/Background/Menu Background.png")
        self.background = pygame.transform.scale(self.background, (800, 600))
        
        # Logo (Taille diminuée à 300px)
        try:
            self.logo = pygame.image.load("asset/Background/logo.png")
            logo_w, logo_h = self.logo.get_size()
            target_width = 300
            ratio = target_width / logo_w
            self.logo = pygame.transform.smoothscale(self.logo, (target_width, int(logo_h * ratio)))
        except:
            self.logo = None

        # Musique et Sons
        self.ost_path = "asset/Sound Menu/main_background_ost.ogg"
        try:
            pygame.mixer.music.load(self.ost_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1) # Boucle infinie
        except Exception as e:
            print(f"Erreur chargement OST: {e}")

        try:
            self.start_sound = pygame.mixer.Sound("asset/Sound Menu/Game-start.wav")
        except:
            self.start_sound = None

        # Boutons centrés (Descendus un peu)
        btn_width, btn_height = 200, 60
        center_x = 800 // 2 - btn_width // 2

        self.buttons = {
            'easy': Button(center_x, 260, btn_width, btn_height, "Facile", (50, 150, 50), (70, 200, 70)),
            'normal': Button(center_x, 340, btn_width, btn_height, "Normal", (50, 100, 150), (70, 130, 200)),
            'hard': Button(center_x, 420, btn_width, btn_height, "Difficile", (150, 100, 50), (200, 130, 70)),
            'quit': Button(center_x, 500, btn_width, btn_height, "Quitter", (150, 50, 50), (200, 70, 70))
        }

        # Bouton Clavier en bas à gauche
        self.keyboard_button = Button(20, 530, 130, 50, "Clavier", (70, 70, 180), (100, 100, 255))
        
        # Bouton Score en bas à droite
        self.score_button = Button(650, 530, 130, 50, "Scores", (100, 100, 100), (150, 150, 150))
        
        # État du tableau des scores
        self.show_scores = False
        self.scores_data = {}
        self.json_path = "data/highscores.json"

        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.score_title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.score_text_font = pygame.font.SysFont("Arial", 18, bold=False)
        self.category_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.high_score_font = pygame.font.SysFont("Arial", 25, bold=True)

    def load_scores(self):
        """Charge les scores depuis le fichier JSON et les trie par score décroissant."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key in ["easy", "normal", "hard", "clavier"]:
                        if key in data and isinstance(data[key], list):
                            data[key] = sorted(data[key], key=lambda x: x.get('score', 0), reverse=True)
                    self.scores_data = data
            except:
                self.scores_data = {}
        else:
            self.scores_data = {}

    def handle_events(self, events):
        for event in events:
            if self.show_scores:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.show_scores = False
                continue

            # Bouton Clavier
            if self.keyboard_button.is_clicked(event):
                if self.start_sound: self.start_sound.play()
                pygame.mixer.music.stop()
                self.manager.change_scene('keyboard_mode')
                return

            # Bouton Score
            if self.score_button.is_clicked(event):
                self.load_scores()
                self.show_scores = True
                return

            # Navigation
            if self.buttons['easy'].is_clicked(event):
                if self.start_sound: self.start_sound.play()
                pygame.mixer.music.stop()
                self.manager.change_scene('easy_mode')
            elif self.buttons['normal'].is_clicked(event):
                if self.start_sound: self.start_sound.play()
                pygame.mixer.music.stop()
                self.manager.change_scene('normal_mode')
            elif self.buttons['hard'].is_clicked(event):
                if self.start_sound: self.start_sound.play()
                pygame.mixer.music.stop()
                self.manager.change_scene('hard_mode')
            elif self.buttons['quit'].is_clicked(event):
                self.manager.quit()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        if not self.show_scores:
            for button in self.buttons.values():
                button.update(mouse_pos)
            self.score_button.update(mouse_pos)
            self.keyboard_button.update(mouse_pos)

    def render_background(self, surface):
        surface.blit(self.background, (0, 0))

    def render_scores_overlay(self, surface):
        """Affiche le tableau des scores avec rectangles en colonnes."""
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 225))
        surface.blit(overlay, (0, 0))

        title_surf = self.score_title_font.render("TABLEAU DES SCORES", True, (255, 255, 255))
        surface.blit(title_surf, (400 - title_surf.get_width() // 2, 40))

        categories = [("easy", "FACILE"), ("normal", "NORMAL"), ("hard", "DIFFICILE"), ("clavier", "CLAVIER")]
        panel_margin = 30
        panel_area_w = 800 - (panel_margin * 2)
        col_width = (panel_area_w // 4) - 15
        y_top = 110
        rect_height = 400

        for i, (key, display_name) in enumerate(categories):
            x = panel_margin + i * (col_width + 15)
            rect = pygame.Rect(x, y_top, col_width, rect_height)
            pygame.draw.rect(surface, (40, 40, 40), rect, border_radius=8)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1, border_radius=8)

            cat_surf = self.category_font.render(display_name, True, (255, 235, 59))
            surface.blit(cat_surf, (x + col_width//2 - cat_surf.get_width()//2, y_top + 12))
            
            pygame.draw.line(surface, (200, 200, 200), (x + 10, y_top + 45), (x + col_width - 10, y_top + 45), 1)

            entries = self.scores_data.get(key, [])
            entry_y = y_top + 60

            if isinstance(entries, list):
                for entry in entries[:12]:
                    name = str(entry.get("name", "---"))
                    score = str(entry.get("score", "0"))
                    if len(name) > 8: name = name[:7] + "."
                    n_txt = self.score_text_font.render(name, True, (255, 255, 255))
                    s_txt = self.score_text_font.render(score, True, (0, 255, 150))
                    surface.blit(n_txt, (x + 10, entry_y))
                    surface.blit(s_txt, (x + col_width - s_txt.get_width() - 10, entry_y))
                    entry_y += 26
            else:
                val_surf = self.score_text_font.render(str(entries), True, (255, 255, 255))
                surface.blit(val_surf, (x + col_width//2 - val_surf.get_width()//2, entry_y))

        close_surf = self.score_text_font.render("Cliquez pour fermer", True, (150, 150, 150))
        surface.blit(close_surf, (400 - close_surf.get_width() // 2, 545))

    def render_overlay(self, surface):
        # Rendu du logo (taille réduite)
        if self.logo:
            logo_rect = self.logo.get_rect(center=(400, 130))
            surface.blit(self.logo, logo_rect)

        for button in self.buttons.values():
            button.render(surface)
        self.score_button.render(surface)
        self.keyboard_button.render(surface)

        if self.show_scores:
            self.render_scores_overlay(surface)

    def render(self, surface):
        self.render_background(surface)
        self.render_overlay(surface)