import random
from typing import List, Tuple
from card import Card
from config import sprite_sheet, card_width, card_height

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