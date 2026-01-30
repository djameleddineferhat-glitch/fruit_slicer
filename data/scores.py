import json
import os

SCORES_FILE = "data/highscores.json"


class Score:
    def __init__(self):
        self.current = 0
        self.high_score = self.load_high_score()

    def add(self, points):
        """Ajoute des points au score."""
        self.current += points

    def reset(self):
        """Remet le score à zéro."""
        self.current = 0

    def save_if_high(self):
        """Sauvegarde si c'est un nouveau high score."""
        if self.current > self.high_score:
            self.high_score = self.current
            self.save_high_score()
            return True
        return False

    def load_high_score(self):
        """Charge le meilleur score."""
        try:
            if os.path.exists(SCORES_FILE):
                with open(SCORES_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0

    def save_high_score(self):
        """Sauvegarde le meilleur score."""
        try:
            os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
            with open(SCORES_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
