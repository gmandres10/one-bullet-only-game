import pygame, os 

GAME_PATH = os.path.dirname(os.path.abspath(__file__))


def get_asset_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(GAME_PATH, "assets", filename)


# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
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
PLAYER_SPEED = 300
PLAYER_JUMP_POWER = -600
PLAYER_GRAVITY = 1400
ENEMY_SPEED = 200

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)

# Define fonts
FONT_INFO = pygame.font.SysFont("Arial", 24)

# Draw text
def draw_text(screen, txt, color, position=(10,10), center=False):
    text_surface = FONT_INFO.render(txt, True, color)
    
    if center:
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, position)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.Surface((100, 200))
        self.image.fill (BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (20, SCREEN_HEIGHT - 250)
        
        self.speed = PLAYER_SPEED
        self.velocity_y = 0
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = PLAYER_GRAVITY
        self.is_jumping = False
        
    def update(self, delta):
        keys = pygame.key.get_pressed()
        
        # horizontal movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed * delta
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed * delta 
            
        # jumping
        if keys[pygame.K_UP] and not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
        
        # apply gravity
        if self.is_jumping:
            self.velocity_y += self.gravity * delta
            self.rect.y += self.velocity_y * delta
        
        # check for landing
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False
            self.velocity_y = 0
        
class Enemies(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (SCREEN_WIDTH - 100, FLOOR_Y - 50)
        self.velocity_x = -ENEMY_SPEED
        
    def update(self, delta):
        self.rect.x += self.velocity_x * delta
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity_x *= -1
        
# Create player instance
all_sprites = pygame.sprite.Group()
player = Player()       
enemies = Enemies()
all_sprites.add(player)
all_sprites.add(enemies)


# Game loop
running = True
while running:
    # Event handling 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Clock update 
    clock.tick(MAX_FPS)
            
    # Update game state
    all_sprites.update(clock.get_time() / 1000.0)  # Pass delta time in seconds
    
    #collision detection
    collided_enemies = pygame.sprite.spritecollide(player, [enemies], False)
    
    if collided_enemies:
        draw_text(screen, "Game Over!", RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), center=True)
    
    # Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    # Draw floor
    pygame.draw.line(screen, BLACK, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 2)   
    draw_text(screen,"Welcome to Single Shot Arena!", BLUE, (10, 10), )
    pygame.draw.circle(screen, (RED), (300,300), 20)
    
    # Draw player
    screen.blit(player.image, player.rect)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit() 