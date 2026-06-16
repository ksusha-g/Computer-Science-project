import pygame

# Константы
background_color = (255, 229, 236)
width = 1060
height = 750
fps = 60

# Загрузка спрайтов
sprite_sheet = pygame.image.load("Cards.png")
card_width = 100
sprite_sheet_height = sprite_sheet.get_height()
card_height = sprite_sheet_height // 4
card_image = sprite_sheet.subsurface((0, 0, card_width, card_height))
card_back_red = sprite_sheet.subsurface((card_width * 14, card_height * 2, card_width, card_height))
card_back_black = sprite_sheet.subsurface((card_width * 14, card_height * 3, card_width, card_height))