# Single Shot Arena

> A fast-paced 2D action platformer where you control **one bullet** — fire it, watch it bounce, and catch it before you can shoot again.  Touch an enemy, or get hit by your own bullet, and it's over.

---

## Game Pitch

You are the last warrior standing in a relentless arena.  Your weapon?  A single, indestructible bullet that bounces off every wall and the ceiling.  Enemies swarm from the edges of the screen, growing faster and more numerous as your score climbs.  Master the arc of your bullet, rack up wall-rebound bonuses, and always be ready to snatch the bullet out of the air — because without it, you are defenceless.

---

## How to Run

### Requirements

- Python 3.8 or newer
- [Pygame](https://www.pygame.org/) — install with:

```bash
pip install pygame
```

### Running the game

```bash
python main.py
```

> The game expects an `assets/images/` folder containing `player.png` and `enemy.png` relative to `main.py`.

---

## Controls

| Key | Action |
|-----|--------|
| `LEFT` arrow | Move left |
| `RIGHT` arrow | Move right |
| `UP` arrow | Jump |
| `SPACE` | Fire the bullet *(only when the bullet is not already active)* |
| `C` | Catch the bullet *(only when the "CATCH!" prompt is visible)* |
| `R` | Restart after Game Over |

---

## Scoring

| Event | Points |
|-------|--------|
| Enemy bounces off a wall | +1 |
| Bullet hits an enemy | +3 |

Lose conditions:
- The player's own bullet collides with the player.
- The player touches any enemy directly.

---

## Difficulty Scaling

The game becomes progressively harder as your score increases:

| Score | Enemy cap | Spawn behaviour |
|-------|-----------|-----------------|
| 0 – 4 | 2 enemies | Ground only, from left or right edge |
| 5 – 9 | 3 enemies | Random position anywhere in the arena |
| 10 – 19 | 4 enemies | Random position, shorter spawn interval |
| 20+ | 6 enemies | Maximum chaos, fastest spawn rate |

The spawn interval shrinks by 0.2 seconds per score point (minimum 2 seconds).

---

## File Structure

```
one-bullet-only-game/
├── README.md   # Game description, controls, and OOP logic
├── demo.mp4      # <30 second gameplay clip
├── src/                # Development "Playground" (it’s ok if this code is buggy/messy)
│   ├── assets/         # Assets used during development
│   │   └── *.*                 # (Optional) Various images
│   ├── main.py      # The entry point for the game         
└── dist/                # "Production" version (this is the code that will be graded)
      ├── assets/         # Verified assets for the working game copied from src
      │   └── *.*                 # Stable version of asset files copied from src
      ├── main.py      # The stable version of main.py
      └── *.py               # Stable version of other .py files copied from src
```

| File / Folder | Purpose |
|---------------|---------|
| `main.py` | Entry point and complete game implementation — constants, all classes, and the game loop |
| `assets/images/` | Sprite images loaded at runtime |
| `README.md` | Project documentation |

---

## OOP Breakdown

### `Player` — `pygame.sprite.Sprite`
Represents the player-controlled character.  Handles horizontal movement, jumping physics (gravity integration), and landing detection on the ground and on platforms.  Stores a `direction` value (`+1` / `-1`) so the bullet always fires the way the player is facing.

### `Enemy` — `pygame.sprite.Sprite`
Represents a single enemy unit.  Walks horizontally across the arena and reverses direction when it reaches a screen edge, setting a `rebounded` flag for one frame so the `Game` can award a point.  Has a `respawn()` method to reposition without removing and recreating the sprite.

### `Bullet` — `pygame.sprite.Sprite`
Represents the one projectile in the game.  Uses floating-point position coordinates for smooth sub-pixel movement, then syncs to an integer `rect` each frame for Pygame's collision system.  Bounces off all four arena boundaries.  Activated by `shoot()` and deactivated when caught or after hitting an enemy.

### `Platform` — `pygame.sprite.Sprite`
Represents a static elevated surface.  Drawn as a solid green rectangle; no image asset needed.  Created once at game start; the `Player.update()` method performs landing checks against a group of these sprites.

### `Game`
The top-level controller and game loop.  Owns all sprite groups, manages the spawn timer, routes keyboard events to the correct actions, resolves all collisions (bullet↔player, bullet↔enemy, player↔enemy), updates the score, and drives the render pipeline each frame.  Calling `run()` starts the game.

---

## Notes

- The game is intentionally a **single-file project** (`main.py`) to keep it easy to read and submit.
- Delta-time (`delta`) is used throughout so the game runs at the same speed regardless of frame rate.
- Pixel-perfect collision detection (`pygame.sprite.collide_mask`) is used for all gameplay-critical checks.
