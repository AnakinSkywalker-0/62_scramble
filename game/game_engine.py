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
        self.hint_letters = {}
        self.timer_remaining = self.ROUND_TIME
        self.timeout_pending = False
        self.tile_letters = list(self.scrambled_word)
        self.selected_tile = None
        self.tile_letters = []
        self.selected_tile = None
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
        self.hint_letters = {}
        self.timer_remaining = self.ROUND_TIME
        self.timeout_pending = False

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

    def get_tile_rects(self):
        tile_size = 48
        gap = 8
        total_width = len(self.tile_letters) * tile_size + (len(self.tile_letters) - 1) * gap
        start_x = self.width // 2 - total_width // 2
        y = 135
        return [pygame.Rect(start_x + i * (tile_size + gap), y, tile_size, tile_size) for i in range(len(self.tile_letters))]

    def handle_tile_click(self, pos):
        rects = self.get_tile_rects()
        for i, rect in enumerate(rects):
            if rect.collidepoint(pos):
                if self.selected_tile is None:
                    self.selected_tile = i
                elif self.selected_tile == i:
                    self.selected_tile = None
                else:
                    self.tile_letters[self.selected_tile], self.tile_letters[i] = self.tile_letters[i], self.tile_letters[self.selected_tile]
                    self.selected_tile = None
                    self.input_box.text = ''.join(self.tile_letters)
                return

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
        if event.type == pygame.USEREVENT + 1 and self.timeout_pending:
            self.next_round()
            return

        if self.timeout_pending:
            return

        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()
            else:
                self.handle_tile_click(event.pos)
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()

    def update(self):
        if self.timeout_pending:
            return

        self.timer_remaining -= 1 / 60
        if self.timer_remaining <= 0:
            self.timer_remaining = 0
            self.feedback_msg = f"TIME'S UP! The word was {self.secret_word}."
            self.feedback_color = (240, 170, 50)
            self.timeout_pending = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 1200, loops=1)

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))

        for i, (letter, rect) in enumerate(zip(self.tile_letters, self.get_tile_rects())):
            tile_color = (70, 110, 170) if i != self.selected_tile else (220, 150, 50)
            pygame.draw.rect(screen, tile_color, rect, border_radius=6)
            pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=6)
            letter_surf = self.font_word.render(letter, True, (255, 255, 255))
            screen.blit(letter_surf, (rect.centerx - letter_surf.get_width() // 2, rect.centery - letter_surf.get_height() // 2))

        hint_y = 195
        hint_parts = []
        for i in range(len(self.secret_word)):
            hint_parts.append(self.hint_letters.get(i, '_'))
        hint_text = ' '.join(hint_parts)
        hint_surf = self.font_msg.render(hint_text, True, (245, 245, 245))
        screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, hint_y))

        timer_ratio = max(0, self.timer_remaining / self.ROUND_TIME)
        timer_x, timer_y, timer_w, timer_h = self.width // 2 - 150, 105, 300, 16
        pygame.draw.rect(screen, (55, 60, 70), (timer_x, timer_y, timer_w, timer_h), border_radius=8)
        pygame.draw.rect(screen, (90, 200, 120), (timer_x, timer_y, int(timer_w * timer_ratio), timer_h), border_radius=8)
        timer_label = self.font_msg.render(f"Time: {max(0, int(self.timer_remaining))}s", True, (255, 220, 80))
        screen.blit(timer_label, (self.width // 2 - timer_label.get_width() // 2, 82))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 85), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_text, (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2))

        pygame.draw.rect(screen, (70, 100, 180), self.hint_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.hint_btn, width=2, border_radius=6)
        hint_text = self.font_btn.render("HINT (-1)", True, (255, 255, 255))
        screen.blit(hint_text, (self.hint_btn.centerx - hint_text.get_width() // 2, self.hint_btn.centery - hint_text.get_height() // 2))

        timer_text = self.font_msg.render(f"Time: {max(0, int(self.timer_remaining))}s", True, (255, 220, 80))
        screen.blit(timer_text, (self.width // 2 - timer_text.get_width() // 2, 105))

        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 285))