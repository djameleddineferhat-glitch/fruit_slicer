"""
Gestionnaire du contexte OpenGL pour le rendu.
"""
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *


class GLRenderer:
    """Gère le rendu OpenGL directement à l'écran."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._init_opengl()

    def _init_opengl(self):
        """Initialise le contexte OpenGL."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        self._setup_lighting()

    def _setup_lighting(self):
        """Configure l'éclairage."""
        light_position = [1.0, 1.0, 2.0, 0.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [0.5, 0.5, 0.5, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    def begin_frame(self):
        """Début du rendu d'une frame."""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def setup_3d(self):
        """Configure pour le rendu 3D."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_CULL_FACE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / self.height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 10,  # Caméra plus loin
                  0, 0, 0,
                  0, 1, 0)

    def setup_2d(self):
        """Configure pour le rendu 2D (textures Pygame)."""
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw_surface(self, surface):
        """Dessine une surface Pygame comme texture OpenGL."""
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, 'RGBA', True)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, data)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(width, 0)
        glTexCoord2f(1, 0); glVertex2f(width, height)
        glTexCoord2f(0, 0); glVertex2f(0, height)
        glEnd()

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([texture_id])

    def cleanup(self):
        """Libère les ressources."""
        pass


def init_opengl_display(width, height):
    """Initialise l'affichage Pygame avec support OpenGL."""
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    return screen
