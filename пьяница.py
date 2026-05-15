import pygame
import random

background_color = (255, 229, 236)

width = 860
height = 600
fps = 30

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My game")
clock = pygame.time.Clock()


running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)

    pygame.display.flip()
    clock.tick(fps)
