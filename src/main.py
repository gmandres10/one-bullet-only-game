import pygame, os 

# -- Configuration and Constants --

GAME_TITLE = "Single Shot Arena"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_FPS = 60




pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)
