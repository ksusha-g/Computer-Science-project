import pygame
from config import width, height, fps, background_color, card_width, card_height
from deck import Deck
from table import Table
from music import MusicPlayer
from buttons import SpeedButton, MusicButton

def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drunkard")
    clock = pygame.time.Clock()

    #играет музыка
    music_player = MusicPlayer()

    my_deck = Deck()
    player_deck, computer_deck = my_deck.divide()
    game_table = Table(player_deck, computer_deck)

    pygame.font.init()
    font = pygame.font.SysFont(None, 36)

    #задаем кнопки
    button_width = 50
    button_height = 50
    button_spacing = 10

    #кнопки скорости
    speed_button_x = width - button_width * 3 - 20 - (button_spacing * 2)
    speed_button_y = height - button_height - 20

    speed_buttons = [
        SpeedButton(speed_button_x + i * (button_width + button_spacing), speed_button_y, 
                    button_width, button_height, f"{multiplier}x", multiplier)
        for i, multiplier in enumerate([1.0, 1.5, 2.0])
    ]
    speed_buttons[0].set_active(True)  #изначально скорость х1

    #кнопки музыки
    music_button_x = 20
    music_button_y = height - button_height - 20
    prev_button = MusicButton(music_button_x, music_button_y, 
                             button_width, button_height,
                             "Music_Prev_Idle.png", "Music_Prev_Pushed.png", "prev")
    pause_button = MusicButton(music_button_x + button_width + button_spacing, music_button_y,
                              button_width, button_height,
                              "Pause_Idle.png", "Pause_Pused.png", "pause")
    next_button = MusicButton(music_button_x + (button_width + button_spacing) * 2, music_button_y,
                             button_width, button_height,
                             "Music_Next_Idle.png", "Music_Next_Pushed.png", "next")
    music_player.update_button_states(pause_button)

    running = True
    dragged_card = None

    while running:
        current_time = pygame.time.get_ticks()
        game_table.update(current_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            #кнопки скорости
            for button in speed_buttons:
                if button.handle_event(event):
                    for btn in speed_buttons:
                        btn.set_active(False)
                    button.set_active(True)
                    game_table.set_speed(button.speed_multiplier)
            
            #кнопки музыки
            if prev_button.handle_event(event):
                music_player.prev_track()
                music_player.update_button_states(pause_button)
            
            if pause_button.handle_event(event):
                music_player.toggle_play_pause()
                music_player.update_button_states(pause_button)
            
            if next_button.handle_event(event):
                music_player.next_track()
                music_player.update_button_states(pause_button)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                clicked_on_button = False
                all_buttons = speed_buttons + [prev_button, pause_button, next_button]
                for button in all_buttons:
                    if button.rect.collidepoint(mouse_x, mouse_y):
                        clicked_on_button = True
                        break
                #тут вроде анимация волны у карт
                if not clicked_on_button and game_table.game_phase == "waiting_for_player" and game_table.player_cards:
                    last_card = game_table.player_cards[-1]
                    if last_card.rect.collidepoint(mouse_x, mouse_y):
                        last_card.dragging = True
                        last_card.drag_offset_x = last_card.rect.x - mouse_x
                        last_card.drag_offset_y = last_card.rect.y - mouse_y
                        dragged_card = last_card
            if event.type == pygame.MOUSEBUTTONUP:
                if dragged_card and game_table.game_phase == "waiting_for_player":
                    dragged_card.dragging = False
                    dragged_card.base_x = dragged_card.rect.x
                    dragged_card.base_y = dragged_card.rect.y
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
        
        #рисуем кнопки
        for button in speed_buttons:
            button.draw(screen)
        
        prev_button.draw(screen)
        pause_button.draw(screen)
        next_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

main()