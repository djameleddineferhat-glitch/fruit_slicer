"""
Cache des modèles 3D et textures pour optimiser le rendu.
"""
import pygame
from OpenGL.GL import *
from core.obj_loader import parse_obj, get_model_center, get_model_scale


class ModelCache:
    """Cache et compile les modèles OBJ en Display Lists OpenGL."""

    def __init__(self):
        self.models = {}           # OBJModel par nom
        self.display_lists = {}    # Display list ID par nom
        self.texture_id = None     # Texture atlas partagée
        self.texture_loaded = False

    def load_texture(self, texture_path):
        """Charge la texture atlas."""
        if self.texture_loaded:
            return

        try:
            # Charger avec Pygame
            surface = pygame.image.load(texture_path)
            # Convertir en RGBA
            surface = surface.convert_alpha()

            # Obtenir les données
            width, height = surface.get_size()
            data = pygame.image.tostring(surface, 'RGBA', True)

            # Créer la texture OpenGL
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

            # Paramètres de texture
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Upload texture
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                        GL_RGBA, GL_UNSIGNED_BYTE, data)

            # Générer mipmaps
            glGenerateMipmap(GL_TEXTURE_2D)

            glBindTexture(GL_TEXTURE_2D, 0)
            self.texture_loaded = True

        except Exception as e:
            print(f"Warning: Could not load texture {texture_path}: {e}")
            self.texture_id = None

    def load_model(self, name, filepath, custom_scale=None, use_texture=True):
        """Charge un modèle OBJ et le compile en Display List."""
        if name in self.models:
            return

        try:
            model = parse_obj(filepath)
            self.models[name] = model

            # Compiler en Display List
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE)

            self._render_model(model, custom_scale, use_texture)

            glEndList()
            self.display_lists[name] = display_list

        except Exception as e:
            print(f"Warning: Could not load model {filepath}: {e}")

    def _render_model(self, model, custom_scale=None, use_texture=True):
        """Rend le modèle dans la Display List courante."""
        # Calculer la transformation pour centrer et normaliser
        center = get_model_center(model)
        scale = get_model_scale(model)

        if custom_scale:
            scale *= custom_scale

        glPushMatrix()

        # Centrer le modèle
        glScalef(scale, scale, scale)
        glTranslatef(-center[0], -center[1], -center[2])

        # Activer les textures si disponibles et demandées
        has_textures = use_texture and len(model.tex_coords) > 0 and self.texture_id is not None

        if has_textures:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Rendre les faces
        for face in model.faces:
            vertices = face['vertices']

            # Triangulate si nécessaire (fans pour polygones convexes)
            if len(vertices) == 3:
                glBegin(GL_TRIANGLES)
                for v_idx, vt_idx, vn_idx in vertices:
                    self._emit_vertex(model, v_idx, vt_idx, vn_idx, has_textures)
                glEnd()
            elif len(vertices) == 4:
                glBegin(GL_QUADS)
                for v_idx, vt_idx, vn_idx in vertices:
                    self._emit_vertex(model, v_idx, vt_idx, vn_idx, has_textures)
                glEnd()
            else:
                # Triangle fan pour polygones > 4 vertices
                glBegin(GL_TRIANGLE_FAN)
                for v_idx, vt_idx, vn_idx in vertices:
                    self._emit_vertex(model, v_idx, vt_idx, vn_idx, has_textures)
                glEnd()

        if has_textures:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()

    def _emit_vertex(self, model, v_idx, vt_idx, vn_idx, has_textures):
        """Émet un vertex avec ses attributs."""
        # Normale
        if vn_idx is not None and vn_idx < len(model.normals):
            n = model.normals[vn_idx]
            glNormal3f(n[0], n[1], n[2])

        # Coordonnées de texture
        if has_textures and vt_idx is not None and vt_idx < len(model.tex_coords):
            t = model.tex_coords[vt_idx]
            glTexCoord2f(t[0], t[1])

        # Position
        if v_idx is not None and v_idx < len(model.vertices):
            v = model.vertices[v_idx]
            glVertex3f(v[0], v[1], v[2])

    def get_display_list(self, name):
        """Retourne l'ID de la Display List pour un modèle."""
        return self.display_lists.get(name)

    def has_model(self, name):
        """Vérifie si un modèle est chargé."""
        return name in self.display_lists

    def cleanup(self):
        """Libère les ressources OpenGL."""
        for dl in self.display_lists.values():
            glDeleteLists(dl, 1)
        self.display_lists.clear()

        if self.texture_id:
            glDeleteTextures([self.texture_id])
            self.texture_id = None

        self.models.clear()
        self.texture_loaded = False
