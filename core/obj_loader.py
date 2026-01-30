"""
Parser de fichiers Wavefront OBJ/MTL pour le rendu OpenGL.
"""


class Material:
    """Représente un matériau MTL."""

    def __init__(self, name):
        self.name = name
        self.Ka = (1.0, 1.0, 1.0)  # Ambient
        self.Kd = (0.8, 0.8, 0.8)  # Diffuse
        self.Ks = (0.5, 0.5, 0.5)  # Specular
        self.Ns = 100.0            # Shininess
        self.d = 1.0               # Transparency (1 = opaque)
        self.map_Kd = None         # Diffuse texture path


class OBJModel:
    """Modèle 3D chargé depuis un fichier OBJ."""

    def __init__(self):
        self.vertices = []      # Liste de (x, y, z)
        self.tex_coords = []    # Liste de (u, v)
        self.normals = []       # Liste de (nx, ny, nz)
        self.faces = []         # Liste de faces, chaque face = [(v, vt, vn), ...]
        self.materials = {}     # Dictionnaire de Material
        self.current_material = None

        # Bounding box pour normalisation
        self.min_bounds = [float('inf')] * 3
        self.max_bounds = [float('-inf')] * 3


def parse_mtl(filepath):
    """Parse un fichier MTL et retourne un dictionnaire de matériaux."""
    materials = {}
    current_material = None

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                keyword = parts[0]

                if keyword == 'newmtl':
                    name = parts[1] if len(parts) > 1 else 'default'
                    current_material = Material(name)
                    materials[name] = current_material

                elif current_material:
                    if keyword == 'Ka' and len(parts) >= 4:
                        current_material.Ka = (
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3])
                        )
                    elif keyword == 'Kd' and len(parts) >= 4:
                        current_material.Kd = (
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3])
                        )
                    elif keyword == 'Ks' and len(parts) >= 4:
                        current_material.Ks = (
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3])
                        )
                    elif keyword == 'Ns' and len(parts) >= 2:
                        current_material.Ns = float(parts[1])
                    elif keyword == 'd' and len(parts) >= 2:
                        current_material.d = float(parts[1])
                    elif keyword == 'map_Kd' and len(parts) >= 2:
                        # Le chemin peut contenir des espaces
                        current_material.map_Kd = ' '.join(parts[1:])

    except FileNotFoundError:
        pass

    return materials


def parse_obj(filepath):
    """Parse un fichier OBJ et retourne un OBJModel."""
    import os

    model = OBJModel()
    current_material_name = None

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if not parts:
                continue

            keyword = parts[0]

            if keyword == 'mtllib' and len(parts) >= 2:
                # Charger le fichier MTL
                mtl_name = ' '.join(parts[1:])
                mtl_path = os.path.join(os.path.dirname(filepath), mtl_name)
                model.materials = parse_mtl(mtl_path)

            elif keyword == 'usemtl' and len(parts) >= 2:
                current_material_name = parts[1]

            elif keyword == 'v' and len(parts) >= 4:
                # Vertex position
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                model.vertices.append((x, y, z))

                # Update bounding box
                model.min_bounds[0] = min(model.min_bounds[0], x)
                model.min_bounds[1] = min(model.min_bounds[1], y)
                model.min_bounds[2] = min(model.min_bounds[2], z)
                model.max_bounds[0] = max(model.max_bounds[0], x)
                model.max_bounds[1] = max(model.max_bounds[1], y)
                model.max_bounds[2] = max(model.max_bounds[2], z)

            elif keyword == 'vt' and len(parts) >= 3:
                # Texture coordinate
                u, v = float(parts[1]), float(parts[2])
                model.tex_coords.append((u, v))

            elif keyword == 'vn' and len(parts) >= 4:
                # Normal
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                model.normals.append((nx, ny, nz))

            elif keyword == 'f' and len(parts) >= 4:
                # Face - indices sont 1-based dans OBJ
                face_vertices = []
                for vertex_data in parts[1:]:
                    indices = vertex_data.split('/')

                    v_idx = int(indices[0]) - 1 if indices[0] else None
                    vt_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None
                    vn_idx = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else None

                    face_vertices.append((v_idx, vt_idx, vn_idx))

                model.faces.append({
                    'vertices': face_vertices,
                    'material': current_material_name
                })

    return model


def get_model_center(model):
    """Calcule le centre du modèle."""
    cx = (model.min_bounds[0] + model.max_bounds[0]) / 2
    cy = (model.min_bounds[1] + model.max_bounds[1]) / 2
    cz = (model.min_bounds[2] + model.max_bounds[2]) / 2
    return (cx, cy, cz)


def get_model_scale(model):
    """Calcule l'échelle pour normaliser le modèle à une taille de 1."""
    dx = model.max_bounds[0] - model.min_bounds[0]
    dy = model.max_bounds[1] - model.min_bounds[1]
    dz = model.max_bounds[2] - model.min_bounds[2]
    max_dim = max(dx, dy, dz)
    return 1.0 / max_dim if max_dim > 0 else 1.0
