# Configuration du jeu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Gameplay
STARTING_LIVES = 3
POINTS_PER_FRUIT = 10
BOMB_CHANCE = 0.15

# Spawn interval (diminue avec le score)
SPAWN_INTERVAL_MAX = 1.5  # Au début
SPAWN_INTERVAL_MIN = 0.4  # Minimum

# Physique - Gravité
GRAVITY = 0.5

# Vélocités des fruits
FRUIT_VELOCITY_X = (-8, 8)
FRUIT_VELOCITY_Y = (-15, -26)
FRUIT_ROTATION_SPEED = (-3, 3)

# Vélocités des bombes
BOMB_VELOCITY_X = (-2, 2)
BOMB_VELOCITY_Y = (-15, -26)
BOMB_ROTATION_SPEED = (-2, 2)

# Vélocités des morceaux coupés
CUT_VELOCITY_X = (3, 6)
CUT_VELOCITY_Y = (-8, -4)
CUT_ROTATION_SPEED_X = (5, 10)
CUT_ROTATION_SPEED_YZ = (-5, 5)

# ===========================================
# MULTIPLICATEUR DE VITESSE PAR MODE
# ===========================================
EASY_SPEED = 0.8     # 20% plus lent
NORMAL_SPEED = 0.9    # Vitesse de base
HARD_SPEED = 1      # 20% plus rapide

# Réduction de vélocité sur collision bordure
BORDER_VELOCITY_DAMPING = 0.5

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Configuration OpenGL
OPENGL_ENABLED = True
OPENGL_FOV = 45.0
OPENGL_NEAR = 0.1
OPENGL_FAR = 100.0

# Éclairage
LIGHT_POSITION = (1.0, 1.0, 1.0, 0.0)
LIGHT_AMBIENT = (0.3, 0.3, 0.3, 1.0)
LIGHT_DIFFUSE = (0.8, 0.8, 0.8, 1.0)
LIGHT_SPECULAR = (0.5, 0.5, 0.5, 1.0)

# Mapping types de fruits -> fichiers OBJ
FRUIT_MODELS = {
    'apple': 'Fruit/Apple.obj',
    'orange': 'Fruit/Orange.obj',
    'watermelon': 'Fruit/Watermelon.obj',
    'banana': 'Fruit/Banana.obj',
    'chili': 'Fruit/Chili.obj',
    'coconut': 'Fruit/Coconut.obj',
    'ice': 'Fruit/Ice.obj',
}

# Modèle de la bombe
BOMB_MODEL = 'Fruit/Bomb.obj'

# Modèles coupés - moitié 1 (-C)
FRUIT_MODELS_CUT = {
    'apple': 'Fruit/Apple-C.obj',
    'orange': 'Fruit/Orange-C.obj',
    'watermelon': 'Fruit/Watermelon-C.obj',
    'banana': 'Fruit/Banana-C.obj',
    'chili': 'Fruit/Chili-C.obj',
    'coconut': 'Fruit/Coconut-C.obj',
    'ice': 'Fruit/Ice-C.obj',
}

# Modèles coupés - moitié 2 (-C2) pour les fruits qui en ont
FRUIT_MODELS_CUT2 = {
    'banana': 'Fruit/Banana-C2.obj',
    'chili': 'Fruit/Chili-C2.obj',
}

# Échelles par type de fruit (ajustable)
FRUIT_SCALES = {
    'apple': 1.0,
    'orange': 1.0,
    'watermelon': 1.3,
    'banana': 1.2,
    'chili': 0.8,
    'coconut': 1.1,
    'ice': 1.0,
}

# Chemin vers la texture atlas
TEXTURE_ATLAS_PATH = 'asset/Textures/Fruits.png'


def get_spawn_interval(score):
    """Retourne l'intervalle de spawn basé sur le score.
    Plus le score augmente, plus les fruits apparaissent vite.
    """
    # Tous les 50 points, l'intervalle diminue de 0.1
    reduction = (score // 50) * 0.1
    interval = SPAWN_INTERVAL_MAX - reduction
    return max(interval, SPAWN_INTERVAL_MIN)