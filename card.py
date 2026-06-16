import pygame
import math
from config import card_width, card_height, sprite_sheet, card_back_red, card_back_black

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
        
        self.wave_offset = 0
        self.base_x = 0
        self.base_y = 0
        self.enable_wave = True

    def set_sprite(self, sprite_sheet: pygame.Surface, card_width: int, card_height: int) -> None:
        x = self.value_index * card_width
        y = self.suit_index * card_height
        self.sprite = sprite_sheet.subsurface((x, y, card_width, card_height))
        self.rect = self.sprite.get_rect()

    def set_position(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y
        self.base_x = x
        self.base_y = y

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

    def update_animation(self, speed_multiplier: float = 1.0) -> None:
        if self.animation_duration > 0:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.animation_start_time) * speed_multiplier
            self.animation_progress = min(1.0, elapsed / self.animation_duration)
            ease_progress = 1 - (1 - self.animation_progress) ** 2

            self.rect.x = self.animation_start_x + (self.animation_target_x - self.animation_start_x) * ease_progress
            self.rect.y = self.animation_start_y + (self.animation_target_y - self.animation_start_y) * ease_progress

            if self.animation_progress >= 1.0:
                self.animation_duration = 0
                self.is_played = True
                self.base_x = self.rect.x
                self.base_y = self.rect.y

        if self.scale_animation_start > 0:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.scale_animation_start) * speed_multiplier
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

    #волна
    def update_wave(self, time: float, index: int, total_cards: int, wave_amplitude: int, wave_speed: float) -> None:
        if self.enable_wave and self.animation_duration == 0 and self.scale_animation_start == 0 and not self.dragging:
            phase = (index / total_cards) * 2 * math.pi
            wave_offset = math.sin(time * wave_speed + phase) * wave_amplitude
            self.rect.y = self.base_y + wave_offset

    def is_animation_finished(self) -> bool:
        return self.animation_duration == 0 and self.is_played

    def get_scaled_sprite(self):
        if self.scale != 1.0:
            new_width = int(card_width * self.scale)
            new_height = int(card_height * self.scale)
            return pygame.transform.scale(self.sprite, (new_width, new_height))
        return self.sprite

    def get_sprite_back(self, suit_indices: int) -> pygame.Surface:
        if suit_indices in (0, 2):
            return card_back_black
        else:
            return card_back_red

    def draw(self, screen: pygame.Surface, show_back: bool = False, speed_multiplier: float = 1.0) -> None:
        self.update_animation(speed_multiplier)

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