import pygame
import random

background_color = (255, 229, 236)

width = 1060
height = 750
fps = 60

#sprites
sprite_sheet = pygame.image.load("Cards.png")
card_width = 100
sprite_sheet_height = sprite_sheet.get_height()
card_height = sprite_sheet_height // 4
card_image = sprite_sheet.subsurface((0, 0, card_width, card_height))
card_back_red = sprite_sheet.subsurface((card_width*14, card_height*2, card_width, card_height))
card_back_black = sprite_sheet.subsurface((card_width*14, card_height*3, card_width, card_height))

class Card:
    def __init__(self, value, suit, rank, suit_index, value_index):
        self.value = value
        self.suit = suit
        self.rank = rank
        self.suit_index = suit_index
        self.value_index = value_index
        self.sprite = None
        self.rect = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_played = False
        self.animation_progress = 0
        self.animation_start_x = 0
        self.animation_start_y = 0
        self.animation_target_x = 0
        self.animation_target_y = 0
        self.animation_duration = 0
        self.animation_start_time = 0
        self.scale = 1.0
        self.scale_target = 1.0
        self.scale_start = 1.0
        self.scale_animation_start = 0
        self.center_x = None
        self.center_y = None
        self.is_face_up = True
    
    def set_sprite(self, sprite_sheet, card_width, card_height):
        x = self.value_index * card_width
        y = self.suit_index * card_height
        self.sprite = sprite_sheet.subsurface((x, y, card_width, card_height))
        self.rect = self.sprite.get_rect()
    
    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def start_animation(self, target_x, target_y, duration_ms):
        self.animation_start_x = self.rect.x
        self.animation_start_y = self.rect.y
        self.animation_target_x = target_x
        self.animation_target_y = target_y
        self.animation_duration = duration_ms
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_progress = 0
    
    def update_animation(self):
        if self.animation_duration > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.animation_start_time
            self.animation_progress = min(1.0, elapsed / self.animation_duration)
            ease_progress = 1 - (1 - self.animation_progress) ** 2
            
            self.rect.x = self.animation_start_x + (self.animation_target_x - self.animation_start_x) * ease_progress
            self.rect.y = self.animation_start_y + (self.animation_target_y - self.animation_start_y) * ease_progress
            
            if self.animation_progress >= 1.0:
                self.animation_duration = 0
        
        if self.scale_animation_start > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.scale_animation_start
            scale_progress = min(1.0, elapsed / 300)
            ease_progress = 1 - (1 - scale_progress) ** 2
            
            old_center_x = self.rect.centerx
            old_center_y = self.rect.centery
            
            self.scale = self.scale_start + (self.scale_target - self.scale_start) * ease_progress
            
            new_width = int(card_width * self.scale)
            new_height = int(card_height * self.scale)
            self.rect.width = new_width
            self.rect.height = new_height
            
            if hasattr(self, 'center_x') and self.center_x is not None and scale_progress < 1.0:
                self.rect.centerx = self.center_x
                self.rect.centery = self.center_y
            else:
                self.rect.centerx = old_center_x
                self.rect.centery = old_center_y
            
            if scale_progress >= 1.0:
                self.scale_animation_start = 0
                self.center_x = None
                self.center_y = None
    
    def start_scale_animation(self, target_scale):
        self.scale_start = self.scale
        self.scale_target = target_scale
        self.scale_animation_start = pygame.time.get_ticks()
    
    def get_scaled_sprite(self):
        if self.scale != 1.0:
            new_width = int(card_width * self.scale)
            new_height = int(card_height * self.scale)
            scaled_sprite = pygame.transform.scale(self.sprite, (new_width, new_height))
            return scaled_sprite
        return self.sprite
    
    def get_sprite_back(self):
        return card_back_black

    def draw(self, screen, show_back=False):
        self.update_animation()
        if show_back or not self.is_face_up:
            back_sprite = self.get_sprite_back()
            if self.scale != 1.0:
                back_sprite = pygame.transform.scale(back_sprite, (self.rect.width, self.rect.height))
            screen.blit(back_sprite, self.rect)
        else:
            sprite_to_draw = self.get_scaled_sprite()
            screen.blit(sprite_to_draw, self.rect)
    
    def __str__(self) -> str:
        return f"{self.value}{self.suit}"

class Deck:
    def __init__(self):
        self.sprite_sheet = sprite_sheet
        self.card_width = card_width
        self.card_height = card_height
        self.deck = []
        self.suits = ["spades", "diamonds", "club", "hearts"]
        self.suit_indices = {"spades": 0, "diamonds": 1, "club": 2, "hearts": 3}
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.value_indices = {"2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7, "9": 8, "10": 9, "J": 10, "Q": 11, "K": 12, "A": 0}
        
        self.create_deck_objects()
    
    def create_deck_objects(self):
        for suit in self.suits:
            suit_idx = self.suit_indices[suit]
            for value in self.values:
                rank = self.ranks[self.values.index(value)]
                value_idx = self.value_indices[value]
                card = Card(value, suit, rank, suit_idx, value_idx)
                card.set_sprite(sprite_sheet, card_width, card_height)
                self.deck.append(card)
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.deck)

    def divide(self):
        half_deck = len(self.deck) // 2
        player_deck = self.deck[:half_deck].copy()
        computer_deck = self.deck[half_deck:].copy()
        return player_deck, computer_deck

class Table:
    def __init__(self, player_deck, computer_deck):
        self.player_deck = player_deck
        self.computer_deck = computer_deck
        self.computer_cards = []
        self.player_cards = []
        self.overlap_offset = 30
        self.player_played_card = None
        self.computer_played_card = None
        self.waiting_for_computer = False
        self.comparison_done = False
        self.comparison_timer = 0
        self.animation_phase = 0
        self.current_turn = "player"
        self.winner = None
        self.collecting_cards = False
        self.collect_timer = 0
        self.refresh_animation = False
        
        self.total_computer_cards = min(9, len(self.computer_deck))
        self.start_x_computer = (width - (card_width + (self.total_computer_cards - 1) * 30)) // 2
        self.computer_y = 50

        self.total_player_cards = min(9, len(self.player_deck))
        self.start_x_player = (width - (card_width + (self.total_player_cards - 1) * 30)) // 2
        self.player_y = height - card_height - 50

    def refresh_player_cards_with_animation(self):
        self.player_cards.clear()
        start_index = max(0, len(self.player_deck) - 9)
        self.total_player_cards = len(self.player_deck) - start_index
        self.total_player_cards = min(9, self.total_player_cards)
        self.start_x_player = (width - (card_width + (self.total_player_cards - 1) * 30)) // 2
        
        for i in range(self.total_player_cards):
            card = self.player_deck[start_index + i]
            card.is_played = False
            card.scale = 1.0
            card.is_face_up = False
            card.set_position(self.start_x_player + i * self.overlap_offset, self.player_y)
            self.player_cards.append(card)
        
        if self.player_cards:
            self.player_cards[-1].is_face_up = True
    
    def refresh_computer_cards_with_animation(self):
        self.computer_cards.clear()
        start_index = max(0, len(self.computer_deck) - 9)
        self.total_computer_cards = len(self.computer_deck) - start_index
        self.total_computer_cards = min(9, self.total_computer_cards)
        self.start_x_computer = (width - (card_width + (self.total_computer_cards - 1) * 30)) // 2
        
        for i in range(self.total_computer_cards):
            card = self.computer_deck[start_index + i]
            card.is_played = False
            card.scale = 1.0
            card.is_face_up = False
            card.set_position(self.start_x_computer + i * self.overlap_offset, self.computer_y)
            self.computer_cards.append(card)

    def drawable_computer_cards(self):
        self.computer_cards.clear()
        start_index = max(0, len(self.computer_deck) - 9)
        self.total_computer_cards = len(self.computer_deck) - start_index
        self.total_computer_cards = min(9, self.total_computer_cards)
        self.start_x_computer = (width - (card_width + (self.total_computer_cards - 1) * 30)) // 2
        
        for i in range(self.total_computer_cards):
            card = self.computer_deck[start_index + i]
            card.is_face_up = False
            card.set_position(self.start_x_computer + i * self.overlap_offset, self.computer_y)
            self.computer_cards.append(card)
        
        return self.computer_cards
    
    def show_computer_cards(self):
        for card in self.computer_cards:
            if not card.is_played:
                card.draw(screen, show_back=False)
        computer_remaining = len(self.computer_deck) - self.total_computer_cards
        computer_text = f"x{computer_remaining}"
        computer_text_surface = font.render(computer_text, True, (0, 0, 0))
        computer_text_x = self.start_x_computer - 60
        computer_text_y = self.computer_y + card_height // 2 + 35
        screen.blit(computer_text_surface, (computer_text_x, computer_text_y))
    
    def drawable_player_cards(self):
        self.player_cards.clear()
        start_index = max(0, len(self.player_deck) - 9)
        self.total_player_cards = len(self.player_deck) - start_index
        self.total_player_cards = min(9, self.total_player_cards)
        self.start_x_player = (width - (card_width + (self.total_player_cards - 1) * 30)) // 2
        
        for i in range(self.total_player_cards):
            card = self.player_deck[start_index + i]
            card.is_face_up = False
            card.set_position(self.start_x_player + i * self.overlap_offset, self.player_y)
            self.player_cards.append(card)
        
        if self.player_cards:
            self.player_cards[-1].is_face_up = True
        return self.player_cards
    
    def show_player_cards(self):
        for card in self.player_cards:
            if not card.is_played:
                card.draw(screen, show_back=False)
        player_remaining = len(self.player_deck) - self.total_player_cards
        player_text = f"x{player_remaining}"
        player_text_surface = font.render(player_text, True, (0, 0, 0))
        player_text_x = self.start_x_player + 360
        player_text_y = self.player_y + card_height // 2 + 35
        screen.blit(player_text_surface, (player_text_x, player_text_y))
    
    def play_player_card(self, card):
        card.is_played = True
        card.dragging = False
        card.is_face_up = True
        
        # Карта игрока всегда слева
        card.start_animation(
            (width - card_width) // 2 - 100,
            (height - card_height) // 2,
            300
        )
        self.player_played_card = card
        
        if card in self.player_cards:
            self.player_cards.remove(card)
            self.total_player_cards = len(self.player_cards)
        
        # Передаем ход компьютеру
        self.current_turn = "computer"
        self.waiting_for_computer = True
    
    def play_computer_card(self):
        if self.computer_cards:
            computer_card = self.computer_cards[-1]
            computer_card.is_played = True
            computer_card.is_face_up = True
            
            # Карта компьютера всегда справа
            computer_card.start_animation(
                (width - card_width) // 2 + 100,
                (height - card_height) // 2,
                300
            )
            self.computer_played_card = computer_card
            
            if computer_card in self.computer_cards:
                self.computer_cards.remove(computer_card)
                self.total_computer_cards = len(self.computer_cards)
            
            # После хода компьютера начинаем сравнение
            self.waiting_for_computer = False
            self.comparison_done = True
            self.comparison_timer = pygame.time.get_ticks()
    
    def start_scale_cards(self):
        if self.player_played_card and self.computer_played_card:
            player_center_x = self.player_played_card.rect.centerx
            player_center_y = self.player_played_card.rect.centery
            computer_center_x = self.computer_played_card.rect.centerx
            computer_center_y = self.computer_played_card.rect.centery
            
            if self.player_played_card.rank > self.computer_played_card.rank:
                self.player_played_card.start_scale_animation(1.15)
                self.computer_played_card.start_scale_animation(0.85)
                self.winner = "player"
            elif self.player_played_card.rank < self.computer_played_card.rank:
                self.player_played_card.start_scale_animation(0.85)
                self.computer_played_card.start_scale_animation(1.15)
                self.winner = "computer"
            else:
                self.player_played_card.start_scale_animation(1.08)
                self.computer_played_card.start_scale_animation(1.08)
                self.winner = None
            
            self.player_played_card.center_x = player_center_x
            self.player_played_card.center_y = player_center_y
            self.computer_played_card.center_x = computer_center_x
            self.computer_played_card.center_y = computer_center_y
    
    def collect_winner_cards(self):
        if self.winner == "player":
            target_x = self.start_x_player + len(self.player_cards) * self.overlap_offset
            target_y = self.player_y
            if self.player_played_card:
                self.player_played_card.is_face_up = False
                self.player_played_card.start_animation(target_x, target_y, 400)
                self.player_deck.append(self.player_played_card)
            if self.computer_played_card:
                self.computer_played_card.is_face_up = False
                self.computer_played_card.start_animation(target_x, target_y, 400)
                self.player_deck.append(self.computer_played_card)
            self.current_turn = "player"
        elif self.winner == "computer":
            target_x = self.start_x_computer + len(self.computer_cards) * self.overlap_offset
            target_y = self.computer_y
            if self.player_played_card:
                self.player_played_card.is_face_up = False
                self.player_played_card.start_animation(target_x, target_y, 400)
                self.computer_deck.append(self.player_played_card)
            if self.computer_played_card:
                self.computer_played_card.is_face_up = False
                self.computer_played_card.start_animation(target_x, target_y, 400)
                self.computer_deck.append(self.computer_played_card)
            self.current_turn = "computer"
        
        self.collecting_cards = True
        self.collect_timer = pygame.time.get_ticks()
    
    def finish_collecting(self):
        self.player_played_card = None
        self.computer_played_card = None
        self.comparison_done = False
        self.animation_phase = 0
        self.winner = None
        self.collecting_cards = False
        self.waiting_for_computer = False
        self.refresh_player_cards_with_animation()
        self.refresh_computer_cards_with_animation()
    
    def show_played_cards(self):
        if self.player_played_card:
            self.player_played_card.draw(screen, show_back=False)
        if self.computer_played_card:
            self.computer_played_card.draw(screen, show_back=False)
    
    def can_player_move(self):
        return (not self.waiting_for_computer and not self.comparison_done and 
                not self.collecting_cards and self.current_turn == "player" and 
                len(self.player_cards) > 0)

my_deck = Deck()
player_deck, computer_deck = my_deck.divide()
game_table = Table(player_deck, computer_deck)
game_table.drawable_computer_cards()
game_table.drawable_player_cards()

pygame.font.init()
font = pygame.font.SysFont(None, 36)

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drunkard")
clock = pygame.time.Clock()

running = True
dragged_card = None
computer_timer = 0
scale_timer = 0
collect_timer = 0

while running:
    current_time = pygame.time.get_ticks()
    
    # Ход компьютера - компьютер сам вытягивает карту
    if game_table.waiting_for_computer and not game_table.comparison_done and not game_table.collecting_cards:
        if computer_timer == 0:
            computer_timer = current_time
        elif current_time - computer_timer > 800:
            game_table.play_computer_card()
            computer_timer = 0
    
    # Анимация масштабирования
    if game_table.comparison_done and game_table.animation_phase == 0 and not game_table.collecting_cards:
        if scale_timer == 0:
            scale_timer = current_time
        elif current_time - scale_timer > 1000:
            game_table.start_scale_cards()
            game_table.animation_phase = 3
            scale_timer = 0
    
    # Сбор карт победителем
    if game_table.animation_phase == 3 and not game_table.collecting_cards:
        if collect_timer == 0:
            collect_timer = current_time
        elif current_time - collect_timer > 600:
            game_table.collect_winner_cards()
            collect_timer = 0
            game_table.animation_phase = 4
    
    # Завершение сбора и обновление колод с анимацией
    if game_table.collecting_cards:
        if current_time - game_table.collect_timer > 500:
            game_table.finish_collecting()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            if game_table.can_player_move() and game_table.player_cards:
                last_card = game_table.player_cards[-1]
                if not last_card.is_played and last_card.rect.collidepoint(mouse_x, mouse_y):
                    last_card.dragging = True
                    last_card.drag_offset_x = last_card.rect.x - mouse_x
                    last_card.drag_offset_y = last_card.rect.y - mouse_y
                    dragged_card = last_card
        
        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_card:
                game_table.play_player_card(dragged_card)
                dragged_card = None
        
        if event.type == pygame.MOUSEMOTION:
            if dragged_card and dragged_card.dragging:
                mouse_x, mouse_y = event.pos
                dragged_card.rect.x = mouse_x + dragged_card.drag_offset_x
                dragged_card.rect.y = mouse_y + dragged_card.drag_offset_y
                
                if dragged_card.rect.x > width - 100:
                    dragged_card.rect.x = width - 100
                if dragged_card.rect.x < 0:
                    dragged_card.rect.x = 0
                if dragged_card.rect.y < 0:
                    dragged_card.rect.y = 0
                if dragged_card.rect.y > height - 145:
                    dragged_card.rect.y = height - 145
    
    screen.fill(background_color)
    game_table.show_computer_cards()
    game_table.show_player_cards()
    game_table.show_played_cards()
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
