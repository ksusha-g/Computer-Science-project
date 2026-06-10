import pygame
from typing import List, Tuple

import random

background_color = (255, 229, 236)
width = 1060
height = 750
fps = 60

sprite_sheet = pygame.image.load("Cards.png")
card_width = 100
sprite_sheet_height = sprite_sheet.get_height()
card_height = sprite_sheet_height // 4
card_image = sprite_sheet.subsurface((0, 0, card_width, card_height))
card_back_red = sprite_sheet.subsurface((card_width * 14, card_height * 2, card_width, card_height))
card_back_black = sprite_sheet.subsurface((card_width * 14, card_height * 3, card_width, card_height))

class Card:
    def __init__(self, value: str, suit: str, rank: int, suit_index: int, value_index: int) -> None:
        self.value = value
        self.suit = suit
        self.rank = rank
        self.suit_index = suit_index
        self.value_index = value_index

        self.sprite = None
        self.rect = None
        self.is_face_up = True

        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.is_played = False
        self.animation_progress = 0.0
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

    def set_sprite(self, sprite_sheet: pygame.Surface, card_width: int, card_height: int) -> None:
        x = self.value_index * card_width
        y = self.suit_index * card_height
        self.sprite = sprite_sheet.subsurface((x, y, card_width, card_height))
        self.rect = self.sprite.get_rect()

    def set_position(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y

    def start_animation(self, target_x: int, target_y: int, duration_ms: int) -> None:
        self.animation_start_x = self.rect.x
        self.animation_start_y = self.rect.y
        self.animation_target_x = target_x
        self.animation_target_y = target_y
        self.animation_duration = duration_ms
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_progress = 0.0
        self.is_played = False

    def start_scale_animation(self, target_scale: float) -> None:
        self.scale_start = self.scale
        self.scale_target = target_scale
        self.scale_animation_start = pygame.time.get_ticks()

    def is_scale_animation_finished(self) -> bool:
        return self.scale_animation_start == 0

    def update_animation(self) -> None:
        if self.animation_duration > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.animation_start_time
            self.animation_progress = min(1.0, elapsed / self.animation_duration)
            ease_progress = 1 - (1 - self.animation_progress) ** 2

            self.rect.x = self.animation_start_x + (self.animation_target_x - self.animation_start_x) * ease_progress
            self.rect.y = self.animation_start_y + (self.animation_target_y - self.animation_start_y) * ease_progress

            if self.animation_progress >= 1.0:
                self.animation_duration = 0
                self.is_played = True

        if self.scale_animation_start > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.scale_animation_start
            scale_progress = min(1.0, elapsed / 500)
            ease_progress = 1 - (1 - scale_progress) ** 2

            old_center_x = self.rect.centerx
            old_center_y = self.rect.centery

            self.scale = self.scale_start + (self.scale_target - self.scale_start) * ease_progress

            new_width = int(card_width * self.scale)
            new_height = int(card_height * self.scale)
            self.rect.width = new_width
            self.rect.height = new_height

            if self.center_x is not None:
                self.rect.centerx = self.center_x
                self.rect.centery = self.center_y
            else:
                self.rect.centerx = old_center_x
                self.rect.centery = old_center_y

            if scale_progress >= 1.0:
                self.scale_animation_start = 0
                self.center_x = None
                self.center_y = None

    def is_animation_finished(self) -> bool:
        return self.animation_duration == 0 and self.is_played

    def get_scaled_sprite(self):
        if self.scale != 1.0:
            new_width = int(card_width * self.scale)
            new_height = int(card_height * self.scale)
            return pygame.transform.scale(self.sprite, (new_width, new_height))
        return self.sprite

    def get_sprite_back(self, suit_indices: int) -> pygame.Surface:
        if suit_indices in (0, 2):  # пики или трефы
            return card_back_black
        else:  # червы или бубны
            return card_back_red

    def draw(self, screen: pygame.Surface, show_back: bool = False) -> None:
        self.update_animation()

        if show_back or not self.is_face_up:
            back_sprite = self.get_sprite_back(self.suit_index)
            if self.scale != 1.0:
                back_sprite = pygame.transform.scale(back_sprite, (self.rect.width, self.rect.height))
            screen.blit(back_sprite, self.rect)
        else:
            sprite_to_draw = self.get_scaled_sprite()
            screen.blit(sprite_to_draw, self.rect)

    def __str__(self) -> str:
        return f"{self.value}{self.suit}"

class Deck:
    def __init__(self) -> None:
        self.deck: List[Card] = []
        self.suits = ["spades", "diamonds", "clubs", "hearts"]
        self.suit_indices = {"spades": 0, "diamonds": 1, "clubs": 2, "hearts": 3}
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.value_indices = {"2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, 
                              "8": 7, "9": 8, "10": 9, "J": 10, "Q": 11, "K": 12, "A": 0}
        self.create_deck_objects()

    def create_deck_objects(self) -> None:
        for suit in self.suits:
            suit_idx = self.suit_indices[suit]
            for value in self.values:
                rank = self.ranks[self.values.index(value)]
                value_idx = self.value_indices[value]
                card = Card(value, suit, rank, suit_idx, value_idx)
                card.set_sprite(sprite_sheet, card_width, card_height)
                self.deck.append(card)
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.deck)

    def divide(self) -> Tuple[List[Card], List[Card]]:
        half_deck = len(self.deck) // 2
        player_deck = self.deck[:half_deck].copy()
        computer_deck = self.deck[half_deck:].copy()
        return player_deck, computer_deck

class Table:
    def __init__(self, player_deck: List[Card], computer_deck: List[Card]) -> None:
        self.player_deck = player_deck
        self.computer_deck = computer_deck
        self.computer_cards: List[Card] = []
        self.player_cards: List[Card] = []
        self.overlap_offset = 30
        self.player_played_card = None
        self.computer_played_card = None
        self.computer_turn: bool = False
        self.computer_timer: int = 0
        self.comparison_timer: int = 0
        self.scale_timer: int = 0
        self.collect_timer: int = 0
        self.game_phase: str = "waiting_for_player"
        self.computer_y: int = 50
        self.player_y: int = height - card_height - 50
        self.center_x: int = (width - card_width) // 2
        self.center_y: int = (height - card_height) // 2
        self.under_computer_x: int = width // 2 - card_width // 2
        self.under_computer_y: int = self.computer_y
        self.under_player_x: int = width // 2 - card_width // 2
        self.under_player_y: int = self.player_y
        self.refresh_decks()

    def refresh_decks(self) -> None:
        self.player_cards.clear()
        total_player = min(9, len(self.player_deck))
        if total_player > 0:
            start_x_player = (width - (card_width + (total_player - 1) * self.overlap_offset)) // 2
            start_index = len(self.player_deck) - total_player
            for i in range(total_player):
                card = self.player_deck[start_index + i]
                if card != self.player_played_card:
                    card.set_position(start_x_player + i * self.overlap_offset, self.player_y)
                    if i == total_player - 1:
                        card.is_face_up = True
                    else:
                        card.is_face_up = False
                self.player_cards.append(card)

        self.computer_cards.clear()
        total_computer = min(9, len(self.computer_deck))
        if total_computer > 0:
            start_x_computer = (width - (card_width + (total_computer - 1) * self.overlap_offset)) // 2
            start_index = len(self.computer_deck) - total_computer
            for i in range(total_computer):
                card = self.computer_deck[start_index + i]
                if card != self.computer_played_card:
                    card.set_position(start_x_computer + i * self.overlap_offset, self.computer_y)
                    card.is_face_up = False
                self.computer_cards.append(card)

    def show_cards(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 36)
        for card in self.computer_cards:
            if card != self.computer_played_card:
                card.draw(screen, show_back=True)
        for card in self.player_cards:
            if card != self.player_played_card:
                card.draw(screen, show_back=not card.is_face_up)
        if self.player_played_card:
            self.player_played_card.draw(screen, show_back=False)
        if self.computer_played_card:
            self.computer_played_card.draw(screen, show_back=False)

        computer_remaining = len(self.computer_deck)
        computer_text = f"{computer_remaining}"
        computer_text_surface = font.render(computer_text, True, (0, 0, 0))
        computer_text_x = self.under_computer_x + card_width // 2 - 15
        computer_text_y = self.computer_y + card_height + 10
        screen.blit(computer_text_surface, (computer_text_x, computer_text_y))

        player_remaining = len(self.player_deck)
        player_text = f"{player_remaining}"
        player_text_surface = font.render(player_text, True, (0, 0, 0))
        player_text_x = self.under_player_x + card_width // 2 - 15
        player_text_y = self.player_y - 30
        screen.blit(player_text_surface, (player_text_x, player_text_y))

    def play_player_card(self) -> None:
        if not self.player_deck:
            return
        self.player_played_card = self.player_deck[-1]
        self.player_played_card.is_face_up = True
        self.player_played_card.start_animation(self.center_x - 100, self.center_y, 300)
        self.player_deck.pop()
        if self.computer_played_card is not None:
            self.game_phase = "comparing"
            self.comparison_timer = pygame.time.get_ticks()
        else:
            self.game_phase = "computer_turn"
            self.computer_timer = pygame.time.get_ticks()
        self.refresh_decks()

    def play_computer_card(self) -> None:
        if not self.computer_deck:
            return
        self.computer_played_card = self.computer_deck[-1]
        self.computer_played_card.is_face_up = True
        self.computer_played_card.start_animation(self.center_x + 100, self.center_y, 300)
        self.computer_deck.pop()
        if self.player_played_card is not None:
            self.game_phase = "comparing"
            self.comparison_timer = pygame.time.get_ticks()
        else:
            self.game_phase = "waiting_for_player"
        self.refresh_decks()

    def compare_and_scale_cards(self) -> None:
        if self.player_played_card and self.computer_played_card:
            player_center_x = self.player_played_card.rect.centerx
            player_center_y = self.player_played_card.rect.centery
            computer_center_x = self.computer_played_card.rect.centerx
            computer_center_y = self.computer_played_card.rect.centery
            if self.player_played_card.rank > self.computer_played_card.rank:
                self.player_played_card.start_scale_animation(1.2)
                self.computer_played_card.start_scale_animation(0.8)
                self.computer_turn = False
            elif self.player_played_card.rank < self.computer_played_card.rank:
                self.player_played_card.start_scale_animation(0.8)
                self.computer_played_card.start_scale_animation(1.2)
                self.computer_turn = True
            else:
                self.player_played_card.start_scale_animation(1.1)
                self.computer_played_card.start_scale_animation(1.1)
                self.computer_turn = False
            self.player_played_card.center_x = player_center_x
            self.player_played_card.center_y = player_center_y
            self.computer_played_card.center_x = computer_center_x
            self.computer_played_card.center_y = computer_center_y
            self.scale_timer = pygame.time.get_ticks()
            self.game_phase = "scaling"

    def collect_cards(self) -> None:
        if self.player_played_card and self.computer_played_card:
            self.player_played_card.scale = 1.0
            self.player_played_card.rect.width = card_width
            self.player_played_card.rect.height = card_height
            self.computer_played_card.scale = 1.0
            self.computer_played_card.rect.width = card_width
            self.computer_played_card.rect.height = card_height
            if self.player_played_card.rank > self.computer_played_card.rank:
                target_x = self.under_player_x
                target_y = self.under_player_y
                self.player_played_card.start_animation(target_x, target_y, 400)
                self.computer_played_card.start_animation(target_x, target_y, 400)
                self.player_deck.insert(0, self.player_played_card)
                self.player_deck.insert(0, self.computer_played_card)
            elif self.player_played_card.rank < self.computer_played_card.rank:
                target_x = self.under_computer_x
                target_y = self.under_computer_y
                self.player_played_card.start_animation(target_x, target_y, 400)
                self.computer_played_card.start_animation(target_x, target_y, 400)
                self.computer_deck.insert(0, self.player_played_card)
                self.computer_deck.insert(0, self.computer_played_card)
            else:
                player_target_x = self.under_player_x
                player_target_y = self.under_player_y
                computer_target_x = self.under_computer_x
                computer_target_y = self.under_computer_y
                self.player_played_card.start_animation(player_target_x, player_target_y, 400)
                self.computer_played_card.start_animation(computer_target_x, computer_target_y, 400)
                self.player_deck.insert(0, self.player_played_card)
                self.computer_deck.insert(0, self.computer_played_card)
            self.game_phase = "collecting"
            self.collect_timer = pygame.time.get_ticks()

    def finish_collecting(self) -> None:
        self.player_played_card = None
        self.computer_played_card = None
        self.refresh_decks()
        if self.computer_turn:
            self.game_phase = "computer_turn"
            self.computer_timer = pygame.time.get_ticks()
        else:
            self.game_phase = "waiting_for_player"

    def update(self, current_time: int) -> None:
        if self.game_phase == "computer_turn":
            if current_time - self.computer_timer > 800:
                self.play_computer_card()
        elif self.game_phase == "comparing":
            if self.player_played_card and self.computer_played_card:
                if self.player_played_card.is_animation_finished() and self.computer_played_card.is_animation_finished():
                    if current_time - self.comparison_timer > 500:
                        self.compare_and_scale_cards()
        elif self.game_phase == "scaling":
            player_done = self.player_played_card.is_scale_animation_finished()
            computer_done = self.computer_played_card.is_scale_animation_finished()
            if player_done and computer_done:
                if current_time - self.scale_timer > 400:
                    self.collect_cards()
        elif self.game_phase == "collecting":
            if current_time - self.collect_timer > 500:
                self.finish_collecting()

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drunkard")
clock = pygame.time.Clock()

my_deck = Deck()
player_deck, computer_deck = my_deck.divide()
game_table = Table(player_deck, computer_deck)

pygame.font.init()
font = pygame.font.SysFont(None, 36)

running = True
dragged_card = None

while running:
    current_time = pygame.time.get_ticks()
    game_table.update(current_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if game_table.game_phase == "waiting_for_player" and game_table.player_cards:
                last_card = game_table.player_cards[-1]
                if last_card.rect.collidepoint(mouse_x, mouse_y):
                    last_card.dragging = True
                    last_card.drag_offset_x = last_card.rect.x - mouse_x
                    last_card.drag_offset_y = last_card.rect.y - mouse_y
                    dragged_card = last_card
        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_card and game_table.game_phase == "waiting_for_player":
                dragged_card.dragging = False
                game_table.play_player_card()
                dragged_card = None
        if event.type == pygame.MOUSEMOTION:
            if dragged_card and dragged_card.dragging:
                mouse_x, mouse_y = event.pos
                dragged_card.rect.x = mouse_x + dragged_card.drag_offset_x
                dragged_card.rect.y = mouse_y + dragged_card.drag_offset_y
                dragged_card.rect.x = max(0, min(dragged_card.rect.x, width - card_width))
                dragged_card.rect.y = max(0, min(dragged_card.rect.y, height - card_height))

    screen.fill(background_color)
    game_table.show_cards(screen)
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
