import pygame, os, random

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
YELLOW = (255, 255, 0)

# Game Constants
FLOOR_Y = SCREEN_HEIGHT - 50
PLAYER_SPEED = 300
PLAYER_JUMP_POWER = -800
PLAYER_GRAVITY = 1400
ENEMY_SPEED = 200
BULLET_RADIUS = 10
BULLET_SPEED = 500
BULLET_CATCH_RANGE = 20


# Define fonts
FONT_INFO = pygame.font.SysFont("Arial", 24)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.Surface((50, 100))
        self.image.fill (BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (400, SCREEN_HEIGHT)
        
        self.speed = PLAYER_SPEED
        self.velocity_y = 0
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = PLAYER_GRAVITY
        self.is_jumping = False
        
    def update(self, delta, platforms):
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
        self.velocity_y += self.gravity * delta
        self.rect.y += self.velocity_y * delta
        
        # check for landing
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False
            self.velocity_y = 0
        
        # check for landing on platforms
        if self.velocity_y > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            for platform in hits:
                if self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.is_jumping = False
                    self.velocity_y = 0
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = ( x, y )
        self.velocity_x = -ENEMY_SPEED
        self.rebounded = False
        
    def respawn(self, score):
        if score >= 10:
            self.rect.x = random.randint(1, SCREEN_WIDTH - self.rect.width - 1)
            self.rect.y = random.randint(0, FLOOR_Y - self.rect.height)

            self.velocity_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        else:
            side = random.choice(["left", "right"])
            if side == "left":
                self.rect.x = 1 
                self.velocity_x = ENEMY_SPEED
            else:
                self.rect.x = SCREEN_WIDTH - self.rect.width - 1
                self.velocity_x = -ENEMY_SPEED
            self.rect.y = FLOOR_Y - self.rect.height
    def update(self, delta):
        self.rebounded = False
        self.rect.x += self.velocity_x * delta
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.velocity_x *= -1
            self.rebounded = True
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        r = BULLET_RADIUS
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (r, r), r)
        self.rect = self.image.get_rect()
        
        self.active = False
        self.x = -200
        self.y = -200
        self.velocity_x = 0
        self.velocity_y = 0
        
    def shoot(self, origin_x, origin_y, direction):
        self.x = origin_x - BULLET_RADIUS
        self.y = origin_y - BULLET_RADIUS
        self.velocity_x = BULLET_SPEED * direction
        self.velocity_y = -300
        self.active = True
    
    def update(self, delta):
        if not self.active:
            return
        
        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta
        
        if self.x <=0:
            self.x = 0
            self.velocity_x *= -1
        elif self.x + BULLET_RADIUS * 2 >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - BULLET_RADIUS * 2
            self.velocity_x *= -1
        
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1
            
        if self.y + BULLET_RADIUS * 2 >= FLOOR_Y:
            self.y = FLOOR_Y - BULLET_RADIUS * 2
            self.velocity_y *= -1
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
class Game: 
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = True
        self.score = 0
        
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.player = Player()
        self.bullet = Bullet()
        self._create_platforms()
        self.all_sprites.add(self.player, self.bullet)
        self._spawn_enemy(1)
        
    def _create_platforms(self):
        platform1 = Platform(200, FLOOR_Y - 150, 150, 20)
        platform2 = Platform(450, FLOOR_Y - 250, 150, 20)
        self.platforms.add(platform1, platform2)
        self.all_sprites.add(platform1, platform2)    
    
    def _spawn_enemy(self, count):
        for i in range(count):
            side = random.choice(["left", "right"])
            if side == "left":
                x = 1
                velocity_x = ENEMY_SPEED
            else:
                x = SCREEN_WIDTH - 51
                velocity_x = -ENEMY_SPEED
            
            if self.score >= 5:
                x = random.randint(1, SCREEN_WIDTH - 51)
                y = random.randint(1, FLOOR_Y - 51)
                velocity_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
            else:
                y = FLOOR_Y - 51   
    
            new_enemy = Enemy(x, y)
            new_enemy.velocity_x = velocity_x
            self.all_sprites.add(new_enemy)
            self.enemies.add(new_enemy)
            
    def _bullet_in_catch_zone(self):
        if not self.bullet.active:
            return False
        catch_rect = self.player.rect.inflate(BULLET_CATCH_RANGE, BULLET_CATCH_RANGE)
        return catch_rect.colliderect(self.bullet.rect)
            
    def _restart(self):
        self.playing = True
        self.score = 0
        self.all_sprites.empty()
        self.enemies.empty()
        self.platforms.empty()
        self.player = Player()
        self.bullet = Bullet()
        self.all_sprites.add(self.player, self.bullet)
        self._create_platforms()
        self._spawn_enemy(1)
            
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not self.playing:
                    self._restart()
                if event.key == pygame.K_SPACE and self.playing and not self.bullet.active:
                    self.bullet.shoot(self.player.rect.centerx, self.player.rect.centery, 1)
                if event.key == pygame.K_c and self.playing:
                    if self._bullet_in_catch_zone():
                        self.bullet.active = False
    
    # Draw text
    def draw_text(self, txt, color, position=(10,10), center=False):
        text_surface = FONT_INFO.render(txt, True, color)
    
        if center:
            text_rect = text_surface.get_rect(center=position)
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, position)
        
    def _update(self, delta):
        if self.playing:
            self.player.update(delta, self.platforms)
            self.enemies.update(delta)
            self.bullet.update(delta)
            
        for enemy in self.enemies:
            if enemy.rebounded:
                self.score += 1
        
        if self.bullet.active:
            
            if pygame.sprite.collide_rect(self.bullet, self.player):
                if not self._bullet_in_catch_zone():
                    self.bullet.active = False
            hit = pygame.sprite.spritecollide(self.bullet, self.enemies, True)
            if hit:
                self.bullet.active = False
                self.score += 3
            
                if self.score < 5:
                    self._spawn_enemy(1)
                if self.score >= 5:
                    self._spawn_enemy(2)
                elif self.score >= 10:
                    self._spawn_enemy(2)
                    
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.playing = False       
    
    def _draw(self):
        self.screen.fill(WHITE)
        
        pygame.draw.line(self.screen, BLACK, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 3)
        
        self.all_sprites.draw(self.screen)
        self.draw_text(f"Score: {self.score}", BLACK, (10, 10)) 
        
        if not self.playing:
            self.draw_text("Game Over! Press R to Restart", RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), center=True)
            
        pygame.display.flip()
    def run(self):
        while self.running:
            self._handle_events()
            self.clock.tick(MAX_FPS)
            self._update(self.clock.get_time() / 1000.0)
            self._draw()
        pygame.quit()
            
if __name__ == "__main__":
    game = Game()
    game.run()            