import pygame
from core.scene_manager import Scene
from ui.menu import Button


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        # Background
        self.background = pygame.image.load("asset/Background/Menu Background.png")
        self.background = pygame.transform.scale(self.background, (800, 600))

        # Son de démarrage
        try:
            self.start_sound = pygame.mixer.Sound("asset/Sound Menu/Game-start.wav")
        except:
            self.start_sound = None

        # Boutons centrés
        btn_width, btn_height = 200, 60
        center_x = 800 // 2 - btn_width // 2

        self.buttons = {
            'easy': Button(center_x, 220, btn_width, btn_height, "Facile", (50, 150, 50), (70, 200, 70)),
            'normal': Button(center_x, 300, btn_width, btn_height, "Normal", (50, 100, 150), (70, 130, 200)),
            'hard': Button(center_x, 380, btn_width, btn_height, "Difficile", (150, 100, 50), (200, 130, 70)),
            'quit': Button(center_x, 480, btn_width, btn_height, "Quitter", (150, 50, 50), (200, 70, 70))
        }

        self.title_font = pygame.font.Font(None, 80)

    def handle_events(self, events):
        for event in events:
            # Mode Facile
            if self.buttons['easy'].is_clicked(event):
                if self.start_sound:
                    self.start_sound.play()
                self.manager.change_scene('easy_mode')
            
            # Mode Normal
            elif self.buttons['normal'].is_clicked(event):
                if self.start_sound:
                    self.start_sound.play()
                self.manager.change_scene('normal_mode')
            
            # Mode Hard
            elif self.buttons['hard'].is_clicked(event):
                if self.start_sound:
                    self.start_sound.play()
                self.manager.change_scene('hard_mode')
                
            # Quitter
            elif self.buttons['quit'].is_clicked(event):
                self.manager.quit()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos)

    def render_background(self, surface):
        surface.blit(self.background, (0, 0))

    def render_overlay(self, surface):
        title = self.title_font.render("FRUIT NINJA", True, (255, 100, 50))
        title_rect = title.get_rect(center=(400, 100))
        surface.blit(title, title_rect)

        for button in self.buttons.values():
            button.render(surface)

    def render(self, surface):
        self.render_background(surface)
        self.render_overlay(surface)