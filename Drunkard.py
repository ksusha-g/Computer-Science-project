import pygame
import random

background_color = (255, 229, 236)

width = 1060
height = 750
fps = 30

#sprites
sprite_sheet = pygame.image.load("Cards.png")
card_width = 100 #0 - the first card, card_width*N (N - the number of the card)
sprite_sheet_height = sprite_sheet.get_height()
card_height = sprite_sheet_height // 4 #тут фигня, переделать. create_deck_objects тоже
card_image = sprite_sheet.subsurface((0, 0, card_width, card_height)) #example of a card
card_back_red = sprite_sheet.subsurface((card_width*14, card_height*2, card_width, card_height))
card_back_black = sprite_sheet.subsurface((card_width*14, card_height, card_width, card_height))

class Card:
    def __init__(self, value, suit, rank, suit_index, value_index):
        self.value = value
        self.suit = suit
        self.rank = rank
        self.suit_index = suit_index
        self.value_index = value_index
        self.sprite = None
    
    def set_sprite(self, sprite_sheet, card_width, card_height):
        x = self.value_index * card_width
        y = self.suit_index * card_height
        self.sprite = sprite_sheet.subsurface((x, y, card_width, card_height))
    
    def __str__(self):
        return f"{self.value}{self.suit}"

#for deck
jokers = ["joker_red", "joker_black"]

#deck - короче тут фигня какая-то, переделать
def create_deck_objects(sprite_sheet, card_width, card_height):
    deck = []
    suits = ["spades", "diamonds", "club", "hearts"]
    suit_indices = {"spades": 0, "diamonds": 1, "club": 2, "hearts": 3}
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    value_indices = {"2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7, "9": 8, "10": 9, "J": 10, "Q": 11, "K": 12, "A": 0}
    for suit in suits:
        suit_idx = suit_indices[suit]
        for value in values:
            rank = ranks[values.index(value)]
            value_idx = value_indices[value]
            card = Card(value, suit, rank, suit_idx, value_idx)
            card.set_sprite(sprite_sheet, card_width, card_height)
            deck.append(card)
    
    return deck

main_deck = create_deck_objects()

#random + 2 decks
random.shuffle(main_deck)
half_deck = len(main_deck) // 2
player_deck = main_deck[:half_deck].copy()
computer_deck = main_deck[half_deck:].copy()

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drunkard")
clock = pygame.time.Clock()


running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)
    screen.blit(card_image, (500, 290))
    screen.blit(card_back_red, (550, 290))
    screen.blit(card_back_black, (600, 290))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit() #so you can close the game
