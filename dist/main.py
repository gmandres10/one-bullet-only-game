"""
Single Shot Arena
=================
A 2D action platformer built with Pygame.

The player controls a character who carries a single bouncing bullet.
Shooting the bullet (SPACE) launches it across the arena; it ricochets
off walls and the ceiling.  The player must either hit enemies with the
bullet or let enemies rebound off walls to earn points, then catch the
bullet (C) before shooting again.  Touching an enemy — or being struck
by the player's own bullet — ends the run.

Controls
--------
LEFT / RIGHT   Move the player horizontally
UP             Jump
SPACE          Fire the bullet (only when it is not already active)
C              Catch the bullet when it is in range
R              Restart after Game Over

Scoring
-------
Enemy wall rebound  +1 point
Bullet hits enemy   +3 points
"""

import pygame
import os
import random

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

GAME_PATH = os.path.dirname(os.path.abspath(__file__))


def get_asset_path(filename: str) -> str:
    """Return the absolute path to a file inside the ``assets/`` directory."""
    return os.path.join(GAME_PATH, "assets", filename)


# ---------------------------------------------------------------------------
# Pygame initialisation
# ---------------------------------------------------------------------------

pygame.init()

# ---------------------------------------------------------------------------
# Configuration & constants
# ---------------------------------------------------------------------------

GAME_TITLE = "Single Shot Arena"

# --- Display ---
SCREEN_WIDTH  = 800   # pixels
SCREEN_HEIGHT = 600   # pixels
MAX_FPS       = 60    # frames per second cap

# --- Colour palette (R, G, B) ---
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
BLUE   = (0,   0,   255)
RED    = (255, 0,   0)
GREEN  = (0,   255, 0)
YELLOW = (255, 255, 0)

# --- World geometry ---
FLOOR_Y = SCREEN_HEIGHT - 50   # y-coordinate of the ground surface

# --- Player tuning ---
PLAYER_SPEED      = 300    # horizontal pixels per second
PLAYER_JUMP_POWER = -700   # initial upward velocity when jumping (negative = up)
PLAYER_GRAVITY    = 1400   # downward acceleration in pixels/s²

# --- Enemy tuning ---
ENEMY_SPEED          = 200   # horizontal pixels per second
ENEMY_SPAWN_INTERVAL = 5.0   # seconds between automatic enemy spawns
MAX_ENEMIES          = 6     # absolute upper limit on live enemies at once

# --- Bullet tuning ---
BULLET_RADIUS      = 10    # radius of the bullet circle in pixels
BULLET_SPEED       = 500   # horizontal launch speed in pixels per second
BULLET_CATCH_RANGE = 100   # extra pixels around the player that count as catch zone

# --- Asset paths ---
THIS_FOLDER    = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER  = os.path.join(THIS_FOLDER, "assets", "images")

# --- UI font ---
FONT_INFO = pygame.font.SysFont("Arial", 24)

# --- Screen surface (created once at module level) ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)


# ===========================================================================
# Sprite classes
# ===========================================================================

class Player(pygame.sprite.Sprite):
    """
    The player-controlled character.

    Responsibilities
    ----------------
    - Horizontal movement bounded by the screen edges.
    - Jumping with simulated gravity.
    - Landing on the ground (FLOOR_Y) and on Platform sprites.
    - Tracking the last-faced direction so the bullet fires the right way.

    Attributes
    ----------
    image_right : pygame.Surface
        Sprite image facing right.
    image_left : pygame.Surface
        Horizontally-flipped sprite image facing left.
    direction : int
        +1 if facing right, -1 if facing left.
    speed : float
        Horizontal movement speed in pixels/second.
    velocity_y : float
        Current vertical speed (positive = falling).
    jump_power : float
        Vertical velocity applied when a jump starts.
    gravity : float
        Acceleration added to velocity_y each frame.
    is_jumping : bool
        True while the player is airborne.
    """

    def __init__(self):
        super().__init__()

        # Load and scale the player sprite; keep both facing directions ready.
        raw = pygame.image.load(os.path.join(IMAGES_FOLDER, "player.png")).convert_alpha()
        self.image_right = pygame.transform.scale(raw, (50, 100))
        self.image_left  = pygame.transform.flip(self.image_right, True, False)
        self.direction   = 1  # start facing right

        self.image = self.image_right
        self.rect  = self.image.get_rect()
        self.rect.topleft = (400, SCREEN_HEIGHT)  # spawn near centre, below the floor
        self.mask  = pygame.mask.from_surface(self.image)

        self.speed      = PLAYER_SPEED
        self.velocity_y = 0
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity    = PLAYER_GRAVITY
        self.is_jumping = False

    def update(self, delta, platforms):
        """
        Move the player, apply gravity, and resolve collisions.

        Parameters
        ----------
        delta : float
            Elapsed time since the last frame in seconds.
        platforms : pygame.sprite.Group
            Group of Platform sprites to test landing collisions against.
        """
        keys = pygame.key.get_pressed()

        # --- Horizontal movement ---
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x  -= self.speed * delta
            self.direction = -1
            self.image     = self.image_left

        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x  += self.speed * delta
            self.direction = 1
            self.image     = self.image_right

        # --- Jump initiation (only allowed when grounded) ---
        if keys[pygame.K_UP] and not self.is_jumping:
            self.velocity_y  = self.jump_power
            self.is_jumping  = True

        # --- Gravity integration ---
        self.velocity_y += self.gravity * delta
        self.rect.y     += self.velocity_y * delta

        # --- Ground collision ---
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping  = False
            self.velocity_y  = 0

        # --- Platform landing (only checked while falling) ---
        if self.velocity_y > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            for platform in hits:
                # Only land when approaching from above.
                if self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.is_jumping  = False
                    self.velocity_y  = 0


class Enemy(pygame.sprite.Sprite):
    """
    An enemy that walks back and forth across the arena.

    Enemies spawn from the sides of the screen (or anywhere once the player's
    score is high enough) and immediately start moving horizontally.  When an
    enemy hits a wall it reverses direction and sets a flag so the Game can
    award a point.

    Attributes
    ----------
    velocity_x : float
        Current horizontal speed (positive = right, negative = left).
    rebounded : bool
        Set to True for exactly one frame when the enemy bounces off a wall.
    """

    def __init__(self, x, y):
        """
        Parameters
        ----------
        x : int
            Initial left edge of the enemy's rectangle.
        y : int
            Initial top edge of the enemy's rectangle.
        """
        super().__init__()

        raw = pygame.image.load(os.path.join(IMAGES_FOLDER, "enemy.png")).convert_alpha()
        self.image_right = pygame.transform.scale(raw, (50, 50))
        self.image_left  = pygame.transform.flip(self.image_right, True, False)

        self.image = self.image_right
        self.rect  = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.velocity_x = -ENEMY_SPEED  # default: move left
        self.rebounded  = False
        self.mask       = pygame.mask.from_surface(self.image)

    def respawn(self, score):
        """
        Relocate this enemy to a fresh position without removing the sprite.

        At low scores enemies restart on the ground from one of the two sides;
        once the player reaches 10 points they can appear anywhere.

        Parameters
        ----------
        score : int
            Current player score, used to decide the spawn zone.
        """
        if score >= 10:
            self.rect.x  = random.randint(1, SCREEN_WIDTH - self.rect.width - 1)
            self.rect.y  = random.randint(0, FLOOR_Y - self.rect.height)
            self.velocity_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        else:
            side = random.choice(["left", "right"])
            if side == "left":
                self.rect.x  = 1
                self.velocity_x = ENEMY_SPEED
            else:
                self.rect.x  = SCREEN_WIDTH - self.rect.width - 1
                self.velocity_x = -ENEMY_SPEED
            self.rect.y = FLOOR_Y - self.rect.height

    def update(self, delta):
        """
        Advance the enemy horizontally and reverse direction at the screen edges.

        Parameters
        ----------
        delta : float
            Elapsed time since the last frame in seconds.
        """
        # Reset the rebound flag each frame so it is only True for one tick.
        self.rebounded = False

        self.rect.x += self.velocity_x * delta

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.velocity_x *= -1   # reverse direction
            self.rebounded   = True


class Bullet(pygame.sprite.Sprite):
    """
    The single projectile the player can fire and later catch.

    The bullet uses floating-point position tracking (``self.x``, ``self.y``)
    for sub-pixel accuracy, and only writes integer values into ``self.rect``
    when syncing with Pygame's collision system.

    The bullet bounces off all four arena walls (left, right, top, and the
    floor).  It starts off-screen and inactive; ``shoot()`` launches it.

    Attributes
    ----------
    active : bool
        Whether the bullet is currently in play.
    x, y : float
        Sub-pixel position of the bullet's top-left corner.
    velocity_x, velocity_y : float
        Current speed components in pixels per second.
    """

    def __init__(self):
        super().__init__()

        r = BULLET_RADIUS
        # Transparent surface so only the drawn circle is visible.
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (r, r), r)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.active     = False
        self.x          = -200.0  # park off-screen when inactive
        self.y          = -200.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0

    def shoot(self, origin_x, origin_y, direction):
        """
        Launch the bullet from the player's position.

        The bullet is offset horizontally so it does not immediately collide
        with the player, and given a slight upward arc.

        Parameters
        ----------
        origin_x : int
            Horizontal centre of the player sprite.
        origin_y : int
            Vertical centre of the player sprite.
        direction : int
            +1 to fire right, -1 to fire left.
        """
        offset = 60  # pixels ahead of the player where the bullet spawns
        self.x          = origin_x + offset * direction - BULLET_RADIUS
        self.y          = origin_y - BULLET_RADIUS
        self.velocity_x = BULLET_SPEED * direction
        self.velocity_y = -300  # initial upward kick
        self.active     = True

    def update(self, delta):
        """
        Advance the bullet and bounce it off arena boundaries.

        Parameters
        ----------
        delta : float
            Elapsed time since the last frame in seconds.
        """
        if not self.active:
            return  # nothing to do while the bullet is not in play

        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta

        # --- Horizontal wall bounces ---
        if self.x <= 0:
            self.x          = 0
            self.velocity_x *= -1
        elif self.x + BULLET_RADIUS * 2 >= SCREEN_WIDTH:
            self.x          = SCREEN_WIDTH - BULLET_RADIUS * 2
            self.velocity_x *= -1

        # --- Ceiling bounce ---
        if self.y <= 0:
            self.y          = 0
            self.velocity_y *= -1

        # --- Floor bounce ---
        if self.y + BULLET_RADIUS * 2 >= FLOOR_Y:
            self.y          = FLOOR_Y - BULLET_RADIUS * 2
            self.velocity_y *= -1

        # Sync the integer rect used by Pygame's collision system.
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


class Platform(pygame.sprite.Sprite):
    """
    A static elevated surface the player can land on.

    Platforms are plain coloured rectangles; no image asset is required.

    Parameters
    ----------
    x, y : int
        Top-left corner of the platform.
    width, height : int
        Dimensions of the platform in pixels.
    """

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# ===========================================================================
# Main game controller
# ===========================================================================

class Game:
    """
    Top-level controller that owns the game loop and all game state.

    The Game class wires together every other system: event handling, physics
    updates, spawn scheduling, collision resolution, scoring, and rendering.
    Call ``run()`` to enter the main loop.

    Attributes
    ----------
    screen : pygame.Surface
        The main display surface.
    clock : pygame.time.Clock
        Used to cap the frame rate and measure delta time.
    running : bool
        False causes the process to exit the main loop and quit.
    playing : bool
        False while the Game Over screen is shown; the loop still runs so
        the player can press R to restart.
    score : int
        Cumulative score for the current run.
    spawn_timer : float
        Countdown (in seconds) to the next automatic enemy spawn.
    all_sprites : pygame.sprite.Group
        Every sprite; drawn each frame.
    enemies : pygame.sprite.Group
        Active enemy sprites; used for collision and spawn-cap checks.
    platforms : pygame.sprite.Group
        Static platform sprites; used for player landing checks.
    player : Player
        The player-controlled character.
    bullet : Bullet
        The single projectile instance (reused across shots).
    """

    def __init__(self):
        self.screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock   = pygame.time.Clock()
        self.running = True
        self.playing = True
        self.score   = 0
        self.spawn_timer = ENEMY_SPAWN_INTERVAL

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies     = pygame.sprite.Group()
        self.platforms   = pygame.sprite.Group()

        # Core game objects
        self.player = Player()
        self.bullet = Bullet()

        self._create_platforms()
        self.all_sprites.add(self.player, self.bullet)
        self._spawn_enemy(1)  # one enemy at game start

    # -----------------------------------------------------------------------
    # Setup helpers
    # -----------------------------------------------------------------------

    def _create_platforms(self):
        """Place the two static platforms and register them in the sprite groups."""
        platform1 = Platform(200, FLOOR_Y - 150, 150, 20)
        platform2 = Platform(450, FLOOR_Y - 250, 150, 20)
        self.platforms.add(platform1, platform2)
        self.all_sprites.add(platform1, platform2)

    # -----------------------------------------------------------------------
    # Spawn logic
    # -----------------------------------------------------------------------

    def _spawn_enemy_timer(self, delta):
        """
        Count down the spawn timer and spawn an enemy when it expires.

        The enemy cap and respawn interval both scale with the player's score,
        creating a progressive difficulty curve.

        Parameters
        ----------
        delta : float
            Elapsed time since the last frame in seconds.
        """
        current_enemies = len(self.enemies)

        # Determine the cap based on score milestones.
        if self.score >= 20:
            cap = 6
        elif self.score >= 10:
            cap = 4
        elif self.score >= 5:
            cap = 3
        else:
            cap = 2

        cap = min(cap, MAX_ENEMIES)  # never exceed the hard limit

        if current_enemies >= cap:
            return  # already at capacity; don't spawn

        self.spawn_timer -= delta
        if self.spawn_timer <= 0:
            self._spawn_enemy(1)
            # Shrink the interval as the score grows, with a 2-second floor.
            interval = max(2.0, ENEMY_SPAWN_INTERVAL - self.score * 0.2)
            self.spawn_timer = interval

    def _spawn_enemy(self, count):
        """
        Instantiate ``count`` new Enemy sprites and add them to the groups.

        Spawn position depends on the current score:
        - score < 5  : always on the ground, entering from a random side.
        - score >= 5 : random position anywhere in the arena.

        Parameters
        ----------
        count : int
            Number of enemies to spawn.
        """
        for _ in range(count):
            side = random.choice(["left", "right"])
            if side == "left":
                x          = 1
                velocity_x = ENEMY_SPEED
            else:
                x          = SCREEN_WIDTH - 51
                velocity_x = -ENEMY_SPEED

            if self.score >= 5:
                # High-score mode: appear anywhere in the arena.
                x          = random.randint(1, SCREEN_WIDTH - 51)
                y          = random.randint(1, FLOOR_Y - 51)
                velocity_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
            else:
                y = FLOOR_Y - 51  # ground level

            new_enemy             = Enemy(x, y)
            new_enemy.velocity_x  = velocity_x
            self.all_sprites.add(new_enemy)
            self.enemies.add(new_enemy)

    # -----------------------------------------------------------------------
    # Bullet catch helper
    # -----------------------------------------------------------------------

    def _bullet_in_catch_zone(self):
        """
        Return True if the bullet is active and within the player's catch range.

        The catch zone is an inflated copy of the player's rect, so the player
        does not need pixel-perfect positioning to retrieve the bullet.
        """
        if not self.bullet.active:
            return False
        catch_rect = self.player.rect.inflate(BULLET_CATCH_RANGE, BULLET_CATCH_RANGE)
        return catch_rect.colliderect(self.bullet.rect)

    # -----------------------------------------------------------------------
    # Game state management
    # -----------------------------------------------------------------------

    def _restart(self):
        """Reset all game state to start a fresh run without restarting the process."""
        self.playing = True
        self.score   = 0

        # Clear every sprite group and rebuild from scratch.
        self.all_sprites.empty()
        self.enemies.empty()
        self.platforms.empty()

        self.player = Player()
        self.bullet = Bullet()
        self.all_sprites.add(self.player, self.bullet)
        self._create_platforms()
        self._spawn_enemy(1)
        self.spawn_timer = ENEMY_SPAWN_INTERVAL

    # -----------------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------------

    def _handle_events(self):
        """
        Process the Pygame event queue for window, keyboard, and quit events.

        Actions
        -------
        QUIT            Set ``running`` to False to exit the loop.
        R               Restart the game (only when not playing).
        SPACE           Fire the bullet (only when playing and bullet inactive).
        C               Catch the bullet if it is in the catch zone.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not self.playing:
                    self._restart()

                if event.key == pygame.K_SPACE and self.playing and not self.bullet.active:
                    self.bullet.shoot(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        self.player.direction,
                    )

                if event.key == pygame.K_c and self.playing:
                    if self._bullet_in_catch_zone():
                        self.bullet.active = False  # catch: deactivate the bullet

    # -----------------------------------------------------------------------
    # Rendering helpers
    # -----------------------------------------------------------------------

    def draw_text(self, txt, color, position=(10, 10), center=False):
        """
        Render a string onto the main screen surface.

        Parameters
        ----------
        txt : str
            The text to display.
        color : tuple
            RGB colour for the text.
        position : tuple
            (x, y) coordinates.  Treated as a centre point when ``center=True``,
            otherwise as the top-left corner.
        center : bool
            If True the text rect is centred on ``position``.
        """
        text_surface = FONT_INFO.render(txt, True, color)
        if center:
            text_rect = text_surface.get_rect(center=position)
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, position)

    def _draw_background(self):
        """
        Draw the gradient sky and solid ground strip.

        The sky uses a vertical gradient from near-black at the top to a
        slightly lighter dark blue-green at the bottom, drawn one horizontal
        line at a time.  A flat green rectangle represents the ground below
        FLOOR_Y.
        """
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(20 + ratio * 60)
            g = int(20 + ratio * 80)
            b = int(20 + ratio * 100)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        # Ground strip
        pygame.draw.rect(self.screen, (30, 100, 40), (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))
        # Ground line to give the floor a defined edge
        pygame.draw.line(self.screen, (20, 60, 20), (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 4)

    # -----------------------------------------------------------------------
    # Update & draw
    # -----------------------------------------------------------------------

    def _update(self, delta):
        """
        Advance the simulation by one frame.

        Performs in order:
        1. Update all sprites (movement, gravity).
        2. Run the enemy spawn timer.
        3. Award points for enemy wall rebounds.
        4. Check bullet-player collision (game over).
        5. Check bullet-enemy collision (kill enemy, award points).
        6. Check player-enemy collision (game over).

        Parameters
        ----------
        delta : float
            Elapsed time since the last frame in seconds.
        """
        if self.playing:
            self.player.update(delta, self.platforms)
            self.enemies.update(delta)
            self.bullet.update(delta)
            self._spawn_enemy_timer(delta)

        if self.bullet.active:
            # The bullet hitting the player is an instant loss.
            if pygame.sprite.collide_mask(self.bullet, self.player):
                self.playing = False

            # Bullet hitting any enemy kills that enemy and scores 3 points.
            hit = pygame.sprite.spritecollide(
                self.bullet, self.enemies, True, pygame.sprite.collide_mask
            )
            if hit:
                self.bullet.active = False
                self.score += 3

        # Direct contact between the player and any enemy is also a loss.
        if pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_mask):
            self.playing = False

    def _draw(self):
        """Render the complete frame: background, sprites, HUD, and overlays."""
        self._draw_background()

        # Floor border line drawn above sprites for visibility.
        pygame.draw.line(self.screen, BLACK, (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 3)

        self.all_sprites.draw(self.screen)

        # HUD: score in the top-left corner.
        self.draw_text(f"Score: {self.score}", WHITE, (10, 10))

        # Catch prompt appears above the player when the bullet is in range.
        if self._bullet_in_catch_zone():
            self.draw_text(
                "CATCH! [C]",
                GREEN,
                (self.player.rect.centerx, self.player.rect.top - 30),
                center=True,
            )

        # Game Over overlay.
        if not self.playing:
            self.draw_text(
                "Game Over! Press R to Restart",
                RED,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                center=True,
            )

        pygame.display.flip()

    # -----------------------------------------------------------------------
    # Main loop
    # -----------------------------------------------------------------------

    def run(self):
        """
        Enter the main game loop.

        The loop runs until ``self.running`` becomes False (e.g. the user
        closes the window).  Each iteration:
        1. Process events.
        2. Tick the clock (caps FPS and measures elapsed time).
        3. Update game logic with the measured delta time.
        4. Render the frame.
        """
        while self.running:
            self._handle_events()
            self.clock.tick(MAX_FPS)
            delta = self.clock.get_time() / 1000.0  # convert ms → seconds
            self._update(delta)
            self._draw()

        pygame.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
