import pygame
import random

background_color = (255, 229, 236)

width = 1060
height = 750
fps = 30

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
        self.rect = None #это чтобы таскать
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
    
    def set_sprite(self, sprite_sheet, card_width, card_height):
        x = self.value_index * card_width
        y = self.suit_index * card_height
        self.sprite = sprite_sheet.subsurface((x, y, card_width, card_height))
        self.rect = self.sprite.get_rect() #тоже чтобы таскать
    
    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def get_sprite_back(self, suit_indices):
        if suit_indices == 0 or suit_indices == 2: 
            return card_back_black
        else: 
            return card_back_red

    #рисуем на экране
    def draw(self, screen, show_back = False):
        if show_back: #показать рубашку
            back_sprite = self.get_sprite_back(self.suit_index)
            screen.blit(back_sprite, self.rect)
        else:
            screen.blit(self.sprite, self.rect)
    
    def __str__(self) -> str:
        return f"{self.value}{self.suit}"

#for deck
jokers = ["joker_red", "joker_black"]

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
    
    def create_deck_objects(self) -> list:
        for suit in self.suits:
            suit_idx = self.suit_indices[suit]
            for value in self.values:
                rank = self.ranks[self.values.index(value)]
                value_idx = self.value_indices[value]
                card = Card(value, suit, rank, suit_idx, value_idx)
                card.set_sprite(sprite_sheet, card_width, card_height)
                self.deck.append(card)
        return self.deck

new_deck = Deck()
main_deck = new_deck.deck.copy()

#перемешиваем
random.shuffle(main_deck)
half_deck = len(main_deck) // 2
player_deck = main_deck[:half_deck].copy()
computer_deck = main_deck[half_deck:].copy()

#компьютер
computer_cards = []
total_computer_cards = min(9, len(computer_deck)) #поставила 9 карт, а не 6, потому что 6 занимают слишком мало места и не оч отображаются
start_x = (width - (card_width + (total_computer_cards - 1) * 30)) // 2 
computer_y = 50
overlap_offset = 30 #расстояние между картами

for i in range(total_computer_cards):
    card = computer_deck[i]
    card.set_position(start_x + i * overlap_offset, computer_y)
    computer_cards.append(card)

player_cards = []
total_player_cards = min(9, len(player_deck))
start_x = (width - (card_width + (total_player_cards - 1) * 30)) // 2  # Центрируем
player_y = height - card_height - 50

for i in range(total_player_cards):
    card = player_deck[i]
    card.set_position(start_x + i * overlap_offset, player_y)
    player_cards.append(card)

#тут будем шрифт менять
pygame.font.init()
font = pygame.font.SysFont(None, 36)

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drunkard")
clock = pygame.time.Clock()

running = True
dragged_card = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        #нажатие мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            #двигаем только первую
            if player_cards:
                last_card = player_cards[-1]
                if last_card.rect.collidepoint(mouse_x, mouse_y):
                    last_card.dragging = True
                    last_card.drag_offset_x = last_card.rect.x - mouse_x
                    last_card.drag_offset_y = last_card.rect.y - mouse_y
                    dragged_card = last_card
        
        #опускаем мышь
        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_card:
                dragged_card.dragging = False
                dragged_card = None
        
        #двигаем
        if event.type == pygame.MOUSEMOTION:
            if dragged_card and dragged_card.dragging:
                mouse_x, mouse_y = event.pos
                dragged_card.rect.x = mouse_x + dragged_card.drag_offset_x
                dragged_card.rect.y = mouse_y + dragged_card.drag_offset_y
    
    screen.fill(background_color)
    
    for card in computer_cards:
        card.draw(screen, show_back=False)
    
    #кол-во карт у компа (кол-во карт в колоде - кол-во отображаемых карт)
    computer_remaining = len(computer_deck) - total_computer_cards
    computer_text = f"x{computer_remaining}"
    computer_text_surface = font.render(computer_text, True, (0, 0, 0))
    computer_text_x = start_x - 60
    computer_text_y = computer_y + card_height // 2 + 35
    screen.blit(computer_text_surface, (computer_text_x, computer_text_y))
    
    for card in player_cards:
        card.draw(screen, show_back=False)
    
    #кол-во карт игрока
    player_remaining = len(player_deck) - total_player_cards
    player_text = f"x{player_remaining}"
    player_text_surface = font.render(player_text, True, (0, 0, 0))
    player_text_x = start_x + 360
    player_text_y = player_y + card_height // 2 + 35
    screen.blit(player_text_surface, (player_text_x, player_text_y))
    
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
