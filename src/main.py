import pygame, os 

# -- Configuration and Constants --

GAME_TITLE = "Single Shot Arena"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_FPS = 60




pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)


# Game loop
running = True
while running:
    # Event handling 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Drawing
    pygame.draw.circle(screen, (0, 255, 0), (100,100), 50)
    # Update display
    pygame.display.flip()
    
pygame.quit() # teardown