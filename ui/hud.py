import pygame


def render_hud(screen, score, lives, combo_text="", combo_progress=0, timer_text="00:00"):
    """Affiche le score à gauche, le timer en haut au centre, les vies à gauche et le combo."""
    font = pygame.font.Font(None, 40)

    # 1. Score en haut à gauche
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # 2. Timer en haut au centre (Modifié pour être au centre)
    timer_surf = font.render(timer_text, True, (255, 255, 255))
    timer_rect = timer_surf.get_rect(center=(screen.get_width() // 2, 30))
    screen.blit(timer_surf, timer_rect)

    # 3. Vies à gauche (en dessous du score)
    heart_size = 25
    for i in range(lives):
        # Position X fixe à gauche, décalée par i
        x = 35 + (i * 35)
        y = 70 # Remonté un peu puisque le timer n'est plus là
        pygame.draw.polygon(screen, (255, 50, 50), [
            (x, y),
            (x - heart_size // 2, y - 10),
            (x - heart_size // 2 - 5, y),
            (x - heart_size // 2, y + 15),
            (x, y + 25),
            (x + heart_size // 2, y + 15),
            (x + heart_size // 2 + 5, y),
            (x + heart_size // 2, y - 10)
        ])

    # 4. Combo text au centre (en dessous du timer)
    if combo_text:
        combo_font = pygame.font.Font(None, 50)
        combo_surface = combo_font.render(combo_text, True, (255, 200, 0))
        combo_rect = combo_surface.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(combo_surface, combo_rect)

        # Barre de temps du combo
        if combo_progress > 0:
            bar_width = 150
            bar_height = 8
            bar_x = screen.get_width() // 2 - bar_width // 2
            bar_y = 105

            # Fond de la barre (gris)
            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

            # Barre de progression (jaune -> rouge selon le temps restant)
            fill_width = int(bar_width * combo_progress)
            if fill_width > 0:
                # Couleur qui passe de vert à rouge
                if combo_progress > 0.5:
                    color = (int(255 * (1 - combo_progress) * 2), 255, 0)
                else:
                    color = (255, int(255 * combo_progress * 2), 0)
                pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)