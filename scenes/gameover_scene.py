import pygame
import json
import os
from core.scene_manager import Scene
from ui.menu import Button

# Chemin vers le fichier de scores
HIGHSCORE_PATH = "data/highscores.json"

class GameOverScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        # Background
        self.background = pygame.image.load("asset/Background/Menu Background.png")
        self.background = pygame.transform.scale(self.background, (800, 600))

        # Son game over
        try:
            self.gameover_sound = pygame.mixer.Sound("asset/Sound Menu/Game-over.wav")
        except:
            self.gameover_sound = None

        self.sound_played = False
        self.highscore_processed = False
        
        # Variables de saisie et de mode
        self.is_typing = False
        self.player_name = ""
        self.current_mode = "normal"  # Valeur de secours

        btn_width, btn_height = 200, 60
        center_x = 800 // 2 - btn_width // 2

        self.buttons = {
            'replay': Button(center_x, 350, btn_width, btn_height, "Rejouer", (50, 150, 50), (70, 200, 70)),
            'menu': Button(center_x, 430, btn_width, btn_height, "Menu", (100, 100, 100), (150, 150, 150)),
            'quit': Button(center_x, 510, btn_width, btn_height, "Quitter", (150, 50, 50), (200, 70, 70))
        }

        self.title_font = pygame.font.Font(None, 70)
        self.score_font = pygame.font.Font(None, 50)
        self.high_font = pygame.font.Font(None, 35)
        self.input_font = pygame.font.Font(None, 60)

    def on_enter(self):
        # Récupérer les infos envoyées par la scène de jeu
        self.current_mode = self.manager.shared_data.get('mode', 'normal')
        
        if self.gameover_sound and not self.sound_played:
            self.gameover_sound.play()
            self.sound_played = True
        
        # On vérifie si c'est un record pour CE mode spécifique
        self.check_if_record()

    def on_exit(self):
        self.sound_played = False
        self.highscore_processed = False
        self.is_typing = False
        self.player_name = ""

    def check_if_record(self):
        score = self.manager.shared_data.get('score', 0)
        if score <= 0: return

        all_scores = self.load_scores()
        
        # On regarde uniquement la liste du mode actuel
        mode_scores = all_scores.get(self.current_mode, [])
        
        # Top 5 : Si moins de 5 scores OU score supérieur au plus petit du top 5
        is_high = len(mode_scores) < 5 or score > min([s['score'] for s in mode_scores], default=0)

        if is_high:
            self.is_typing = True

    def load_scores(self):
        """Charge le JSON et s'assure que la structure existe pour tous les modes."""
        data = {"easy": [], "normal": [], "hard": [], "clavier": []}
        if os.path.exists(HIGHSCORE_PATH):
            try:
                with open(HIGHSCORE_PATH, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Fusionner les données chargées dans notre structure de base
                    for key in data.keys():
                        if key in loaded_data:
                            data[key] = loaded_data[key]
                    # Garder le score absolu s'il existe
                    if "high_score" in loaded_data:
                        data["high_score"] = loaded_data["high_score"]
            except:
                pass
        return data

    def save_highscore(self):
        score = self.manager.shared_data.get('score', 0)
        all_scores = self.load_scores()

        # Sécurité : Création de la catégorie si elle n'existe pas (cas du mode clavier)
        if self.current_mode not in all_scores:
            all_scores[self.current_mode] = []

        # Ajouter le nouveau score
        all_scores[self.current_mode].append({"name": self.player_name, "score": score})
        
        # Trier par score décroissant et garder le top 5
        all_scores[self.current_mode] = sorted(
            all_scores[self.current_mode], 
            key=lambda x: x['score'], 
            reverse=True
        )[:5]

        # Mise à jour du Record Absolu Global
        current_abs_high = all_scores.get("high_score", 0)
        if score > current_abs_high:
            all_scores["high_score"] = score

        # Sauvegarde physique
        try:
            os.makedirs(os.path.dirname(HIGHSCORE_PATH), exist_ok=True)
            with open(HIGHSCORE_PATH, 'w', encoding='utf-8') as f:
                json.dump(all_scores, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde JSON: {e}")
        
        self.is_typing = False
        self.highscore_processed = True

    def handle_events(self, events):
        for event in events:
            if self.is_typing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                        self.save_highscore()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 5 and event.unicode.isalpha():
                        self.player_name += event.unicode.upper()
                return

            if self.buttons['replay'].is_clicked(event):
                # Relance dynamiquement le mode de jeu actuel
                scene_name = "keyboard_mode" if self.current_mode == "clavier" else f"{self.current_mode}_mode"
                self.manager.change_scene(scene_name)
            elif self.buttons['menu'].is_clicked(event):
                self.manager.change_scene('menu')
            elif self.buttons['quit'].is_clicked(event):
                self.manager.quit()

    def update(self, dt):
        if not self.is_typing:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons.values():
                button.update(mouse_pos)

    def render_background(self, surface):
        surface.blit(self.background, (0, 0))

    def render_overlay(self, surface):
        # Titre et Score
        title_color = (255, 50, 50)
        title = self.title_font.render("GAME OVER", True, title_color)
        surface.blit(title, title.get_rect(center=(400, 80)))

        score = self.manager.shared_data.get('score', 0)
        score_txt = self.score_font.render(f"Score ({self.current_mode.upper()}): {score}", True, (255, 255, 255))
        surface.blit(score_txt, score_txt.get_rect(center=(400, 170)))

        if self.is_typing:
            # Filtre sombre pour la saisie
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 230))
            
            prompt_txt = f"NOUVEAU RECORD {self.current_mode.upper()} ! NOM :"
            prompt = self.high_font.render(prompt_txt, True, (255, 215, 0))
            
            # Curseur clignotant
            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            name_surf = self.input_font.render(self.player_name + cursor, True, (255, 255, 255))
            info = self.high_font.render("Appuyez sur Entrée pour valider", True, (150, 150, 150))
            
            overlay.blit(prompt, prompt.get_rect(center=(400, 250)))
            overlay.blit(name_surf, name_surf.get_rect(center=(400, 320)))
            overlay.blit(info, info.get_rect(center=(400, 380)))
            surface.blit(overlay, (0, 0))
        else:
            # Affichage des boutons si on ne tape pas de nom
            for button in self.buttons.values():
                button.render(surface)

    def render(self, surface):
        self.render_background(surface)
        self.render_overlay(surface)