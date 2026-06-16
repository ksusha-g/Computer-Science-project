import pygame
from typing import List
from card import Card
from config import width, height, card_width, card_height

class Table:
    def __init__(self, player_deck: List[Card], computer_deck: List[Card]) -> None:
        self.player_deck = player_deck
        self.computer_deck = computer_deck
        self.computer_cards: List[Card] = []
        self.player_cards: List[Card] = []
        self.overlap_offset = 40  #увеличили расстояние между картами
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
        self.speed_multiplier: float = 1.0
        
        #параметры волновой анимации
        self.wave_time = 0
        self.wave_amplitude = 8 #амплитуда волны в пикселях
        self.wave_speed = 1.5 #скорость волны
        
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
                    card.enable_wave = True
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
                    card.enable_wave = False
                    card.is_face_up = False
                self.computer_cards.append(card)

    #волна
    def update_wave_animation(self) -> None:
        self.wave_time += 0.016 * self.speed_multiplier
        #только у игрока
        for i, card in enumerate(self.player_cards):
            if card != self.player_played_card and card.animation_duration == 0 and not card.dragging:
                card.update_wave(self.wave_time, i, len(self.player_cards), 
                               self.wave_amplitude, self.wave_speed)

    def show_cards(self, screen: pygame.Surface) -> None:
        self.update_wave_animation()
        font = pygame.font.SysFont(None, 36)
        for card in self.computer_cards:
            if card != self.computer_played_card:
                card.draw(screen, show_back=True, speed_multiplier=self.speed_multiplier)
        for card in self.player_cards:
            if card != self.player_played_card:
                card.draw(screen, show_back=not card.is_face_up, speed_multiplier=self.speed_multiplier)
        if self.player_played_card:
            self.player_played_card.draw(screen, show_back=False, speed_multiplier=self.speed_multiplier)
        if self.computer_played_card:
            self.computer_played_card.draw(screen, show_back=False, speed_multiplier=self.speed_multiplier)

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
        self.player_played_card.enable_wave = False
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
            delay = int(800 / self.speed_multiplier)
            if current_time - self.computer_timer > delay:
                self.play_computer_card()
        elif self.game_phase == "comparing":
            if self.player_played_card and self.computer_played_card:
                if self.player_played_card.is_animation_finished() and self.computer_played_card.is_animation_finished():
                    delay = int(500 / self.speed_multiplier)
                    if current_time - self.comparison_timer > delay:
                        self.compare_and_scale_cards()
        elif self.game_phase == "scaling":
            player_done = self.player_played_card.is_scale_animation_finished()
            computer_done = self.computer_played_card.is_scale_animation_finished()
            if player_done and computer_done:
                delay = int(400 / self.speed_multiplier)
                if current_time - self.scale_timer > delay:
                    self.collect_cards()
        elif self.game_phase == "collecting":
            delay = int(500 / self.speed_multiplier)
            if current_time - self.collect_timer > delay:
                self.finish_collecting()

    def set_speed(self, multiplier: float) -> None:
        self.speed_multiplier = multiplier