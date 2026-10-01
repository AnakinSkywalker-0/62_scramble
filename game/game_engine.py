import random
import pygame
from game.text_box import TextBox
 
class GameEngine:
    HINT_PENALTY = 1

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = ["PYTHON", "PYGAME", "PLANET", "ROCKET", "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"]
        self.secret_word = ""
        self.scrambled_word = ""

        self.score = 0
        self.revealed_positions = set()
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(width // 2 - 130, 210, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, 210, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 - 130, 275, 95, 40)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.next_round()

    def scramble_string(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)
            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)
        self.input_box.clear()
        self.revealed_positions.clear()

    def use_hint(self):
        for position, letter in enumerate(self.secret_word):
            if position not in self.revealed_positions:
                self.revealed_positions.add(position)
                self.score = max(0, self.score - self.HINT_PENALTY)
                self.feedback_msg = f"HINT: letter {position + 1} is {letter} (-{self.HINT_PENALTY} point)."
                self.feedback_color = (100, 200, 255)
                return
        self.feedback_msg = "All letters have already been revealed!"
        self.feedback_color = (240, 170, 50)

    def submit_guess(self):
        guess = self.input_box.text.strip().upper()
        if not guess:
            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)
            return

        # BUG SYMPTON: 
        # Player's guess is validated against the scrambled text instead of the original solution.
        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += 1
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)
            self.next_round()
        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()

    def update(self):
        pass

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))

        spaced_letters = "  ".join(self.scrambled_word)
        scramble_surf = self.font_word.render(spaced_letters, True, (100, 200, 255))
        screen.blit(scramble_surf, (self.width // 2 - scramble_surf.get_width() // 2, 130))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 85), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_text, (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2))

        pygame.draw.rect(screen, (70, 100, 180), self.hint_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.hint_btn, width=2, border_radius=6)
        hint_text = self.font_btn.render("HINT (-1)", True, (255, 255, 255))
        screen.blit(hint_text, (self.hint_btn.centerx - hint_text.get_width() // 2, self.hint_btn.centery - hint_text.get_height() // 2))

        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 285))