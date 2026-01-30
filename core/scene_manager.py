import pygame
from OpenGL.GL import *


class Scene:
    """Classe de base pour toutes les scènes."""

    def __init__(self, manager):
        self.manager = manager
        self.screen = manager.screen

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def render_background(self, surface):
        """Rendu du background 2D."""
        pass

    def render_3d(self):
        """Rendu 3D OpenGL."""
        pass

    def render_overlay(self, surface):
        """Rendu des éléments 2D au-dessus (HUD, blade, etc)."""
        pass

    def render(self, surface):
        """Rendu 2D complet (pour mode sans OpenGL)."""
        self.render_background(surface)
        self.render_overlay(surface)

    def on_enter(self):
        pass

    def on_exit(self):
        pass


class SceneManager:
    """Gère les scènes avec rendu hybride OpenGL/Pygame."""

    def __init__(self, screen, gl_renderer=None):
        self.screen = screen
        self.gl_renderer = gl_renderer
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = None
        self.scenes = {}
        self.shared_data = {}

        # Surfaces pour le rendu 2D
        self.bg_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def change_scene(self, name):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = self.scenes.get(name)
        if self.current_scene:
            self.current_scene.on_enter()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update(dt)

                if self.gl_renderer:
                    self._render_hybrid()
                else:
                    self.bg_surface.fill((0, 0, 0))
                    self.current_scene.render(self.bg_surface)
                    self.screen.blit(self.bg_surface, (0, 0))
                    pygame.display.flip()

    def _render_hybrid(self):
        """Rendu: Background 2D -> Fruits 3D -> Overlay 2D."""
        # 1. Clear
        self.gl_renderer.begin_frame()

        # 2. Background 2D
        self.bg_surface.fill((0, 0, 0, 0))
        self.current_scene.render_background(self.bg_surface)
        self.gl_renderer.setup_2d()
        self.gl_renderer.draw_surface(self.bg_surface)

        # 3. Fruits 3D
        self.gl_renderer.setup_3d()
        self.current_scene.render_3d()

        # 4. Overlay 2D (blade, HUD)
        self.overlay_surface.fill((0, 0, 0, 0))
        self.current_scene.render_overlay(self.overlay_surface)
        self.gl_renderer.setup_2d()
        self.gl_renderer.draw_surface(self.overlay_surface)

        pygame.display.flip()

    def quit(self):
        self.running = False
