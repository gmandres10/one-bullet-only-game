import pygame, os 

# Initialize Pygame
pygame.init()

# -- Configuration and Constants --

GAME_TITLE = "Single Shot Arena"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_FPS = 60

# Colors 
wHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

# Define fonts
FONT_INFO = pygame.font.SysFont("Arial", 24)

# Draw text
def draw_text(txt, color, position=(10,10)):
    text_surface = FONT_INFO.render(txt, True, color)
    screen.blit(text_surface, position)




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