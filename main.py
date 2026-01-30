import pygame
from data.config import SCREEN_WIDTH, SCREEN_HEIGHT, OPENGL_ENABLED

def main():
    pygame.init()
    gl_renderer = None

    if OPENGL_ENABLED:
        try:
            from core.gl_renderer import init_opengl_display, GLRenderer
            screen = init_opengl_display(SCREEN_WIDTH, SCREEN_HEIGHT)
            gl_renderer = GLRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.set_caption("Fruit Ninja 3D")
        except Exception as e:
            print(f"OpenGL fail: {e}")
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    from core.scene_manager import SceneManager
    # Importations des scènes
    from scenes.menu_scene import MenuScene
    from scenes.gameover_scene import GameOverScene
    from scenes.easy_mode_view import EasyGameScene
    from scenes.normal_mode_view import NormalGameScene
    from scenes.hard_mode_view import HardGameScene
    
    # Importation de la scène clavier avec un alias pour éviter les conflits
    try:
        from scenes.keyboard_mode_view import NormalGameScene as KeyboardGameScene
    except ModuleNotFoundError:
        from keyboard_mode_view import NormalGameScene as KeyboardGameScene

    manager = SceneManager(screen, gl_renderer=gl_renderer)

    # Enregistrement des scènes dans le manager
    manager.add_scene('menu', MenuScene(manager))
    manager.add_scene('easy_mode', EasyGameScene(manager))
    manager.add_scene('normal_mode', NormalGameScene(manager))
    manager.add_scene('hard_mode', HardGameScene(manager))
    manager.add_scene('game_over', GameOverScene(manager))
    
    # Enregistrement de la scène clavier (appelée par le bouton "Clavier" du menu)
    manager.add_scene('keyboard_mode', KeyboardGameScene(manager))

    # Définition de la scène de départ
    manager.change_scene('menu')

    # Vérification de sécurité pour éviter le NoneType AttributeError
    if manager.current_scene is None:
        print("ERREUR : La scène 'menu' n'a pas pu être chargée. Vérifie manager.add_scene")
        return

    # Lancement de la boucle de jeu
    manager.run()

    if gl_renderer:
        gl_renderer.cleanup()
    pygame.quit()

if __name__ == "__main__":
    main()