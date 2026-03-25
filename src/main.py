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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game Constants
FLOOR_Y = SCREEN_HEIGHT - 50
PLAYER_SPEED = 1
PLAYER_JUMP_POWER = -400
PLAYER_GRAVITY = 1200


# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

# Define fonts
FONT_INFO = pygame.font.SysFont("Arial", 24)

# Draw text
def draw_text(txt, color, position=(10,10)):
    text_surface = FONT_INFO.render(txt, True, color)
    screen.blit(text_surface, position)
    
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.Surface((100, 200))
        self.image.fill (BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (20, SCREEN_HEIGHT - 250)
        self.speed = PLAYER_SPEED
        
    def update(self, delta):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed * delta 
        
        
    def update(self):
        # Move player horizontally
        self.rect.x += self.velocity_x
        # Wrap around screen
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0

# Create player instance
player = Player()

# Game loop
running = True
while running:
    # Event handling 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Update game state
    player.update()
    
    # Drawing
    draw_text("Welcome to Single Shot Arena!", BLUE, (10, 10))
    pygame.draw.circle(screen, (RED), (300,300), 20)
    pygame.draw.rect(screen, (GREEN), (400, 300, 100, 200))
    
    # Draw player
    screen.blit(player.image, player.rect)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit() 