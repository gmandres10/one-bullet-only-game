import pygame, os 

GAME_PATH = os.path.dirname(os.path.abspath(__file__))


def get_asset_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(GAME_PATH, "assets", filename)


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
    draw_text("Welcome to Single Shot Arena!", BLUE, (10, 10))
    pygame.draw.circle(screen, (0, 255, 0), (100,100), 20)
    pygame.draw.rect(screen, (255, 0, 0), (400, 300, 100, 200))
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit() 