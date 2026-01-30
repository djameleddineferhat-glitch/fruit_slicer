import pygame


class ComboSystem:
    def __init__(self):
        self.combo = 0
        self.stack = 0
        self.ultra_stack = 0
        self.combo_timer = 0
        self.combo_timeout = 1.0  # Temps avant reset du combo

        # Charger les sons
        self.combo_sounds = {}
        self.stack_sounds = {}
        self.ultra_sounds = {}

        self.load_sounds()

    def load_sounds(self):
        # Sons combo 2-8 (pas de son pour combo 1)
        for i in range(1, 9):
            if i <= 5:
                path = f"asset/Sound Combo/combo-{i}.wav"
            else:
                path = f"asset/Sound Combo/Combo-{i}.wav"
            try:
                self.combo_sounds[i] = pygame.mixer.Sound(path)
            except:
                pass

        # Sons stack 1-5
        stack_paths = {
            1: "asset/Sound Combo/Stack-combo-1.wav",
            2: "asset/Sound Combo/Strack-combo-2.wav",
            3: "asset/Sound Combo/Stack-combo-3.wav",
            4: "asset/Sound Combo/Stack-combo-4.wav",
            5: "asset/Sound Combo/Stack-comb-5.wav"
        }
        for i, path in stack_paths.items():
            try:
                self.stack_sounds[i] = pygame.mixer.Sound(path)
            except:
                pass

        # Sons ultra stack 1-6
        for i in range(1, 7):
            path = f"asset/Sound Combo/Ultra-Stack-combo-{i}.wav"
            try:
                self.ultra_sounds[i] = pygame.mixer.Sound(path)
            except:
                pass

    def add_hit(self):
        """Appelé quand un fruit est coupé."""
        self.combo += 1
        self.combo_timer = self.combo_timeout

        # Vérifier si on atteint 8 combos = 1 stack
        if self.combo >= 8:
            self.combo = 0
            self.stack += 1

            # Vérifier si on atteint 5 stacks = 1 ultra stack
            if self.stack >= 5:
                self.stack = 0
                self.ultra_stack += 1
                self.play_ultra_sound()
            else:
                self.play_stack_sound()
        elif self.combo >= 2:
            # Joue le son seulement à partir du combo 2
            self.play_combo_sound()

    def play_combo_sound(self):
        if self.combo in self.combo_sounds:
            self.combo_sounds[self.combo].play()

    def play_stack_sound(self):
        if self.stack in self.stack_sounds:
            self.stack_sounds[self.stack].play()

    def play_ultra_sound(self):
        # Ultra stack 1-5, puis ultra stack 2 (6)
        level = min(self.ultra_stack, 6)
        if level in self.ultra_sounds:
            self.ultra_sounds[level].play()

    def update(self, dt):
        """Met à jour le timer du combo."""
        if self.combo > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.reset_combo()

    def reset_combo(self):
        """Reset le combo (pas les stacks)."""
        self.combo = 0
        self.combo_timer = 0

    def reset_all(self):
        """Reset tout."""
        self.combo = 0
        self.stack = 0
        self.ultra_stack = 0
        self.combo_timer = 0

    def get_progress(self):
        """Retourne la progression du timer (1 = plein, 0 = expiré)."""
        if self.combo_timeout > 0:
            return max(0, self.combo_timer / self.combo_timeout)
        return 0

    def get_display_text(self):
        """Retourne le texte à afficher (à partir de combo 2)."""
        if self.ultra_stack > 0:
            return f"ULTRA STACK {self.ultra_stack}!"
        elif self.stack > 0:
            if self.combo >= 2:
                return f"STACK {self.stack} - Combo {self.combo}"
            else:
                return f"STACK {self.stack}"
        elif self.combo >= 2:
            return f"Combo {self.combo}"
        return ""
