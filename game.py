import pygame
import random
import sys

# ----------------------------
# Bush Game
# ----------------------------
# Controls: Arrow keys or WASD to move
# Hide inside green bushes to avoid enemies
# Collect yellow fruits for points
# ----------------------------

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_SIZE = 28
PLAYER_SPEED = 4

BUSH_COUNT = 12
BUSH_MIN_SIZE = 80
BUSH_MAX_SIZE = 160

ENEMY_COUNT = 3
ENEMY_SIZE = 30
ENEMY_SPEED = 2

FRUIT_SIZE = 12
FRUIT_SPAWN_INTERVAL = 4000  # #made by Sampod sharkarmilliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUSH_GREEN = (34, 139, 34)
PLAYER_COLOR = (200, 30, 30)
ENEMY_COLOR = (30, 30, 200)
HIDDEN_OUTLINE = (255, 255, 255)
FRUIT_COLOR = (255, 215, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bush Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# Entities
class RectEntity:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    def draw(self, surf, color):
        pygame.draw.rect(surf, color, self.rect)

class Player(RectEntity):
    def __init__(self, x, y):
        super().__init__((x, y, PLAYER_SIZE, PLAYER_SIZE))
        self.speed = PLAYER_SPEED
        self.hidden = False
        self.score = 0
        self.lives = 3

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def draw(self, surf):
        pygame.draw.rect(surf, PLAYER_COLOR, self.rect)
        if self.hidden:
            # draw subtle outline to indicate hidden state
            pygame.draw.rect(surf, HIDDEN_OUTLINE, self.rect, 2)

class Enemy(RectEntity):
    def __init__(self, x, y):
        super().__init__((x, y, ENEMY_SIZE, ENEMY_SIZE))
        # give random patrol direction
        self.vx = random.choice([-1, 1]) * ENEMY_SPEED
        self.vy = random.choice([-1, 1]) * ENEMY_SPEED

    def update(self, bushes):
        # simple movement with bouncing off walls
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy *= -1

        # slight chance to change direction when inside/near bush for variety
        for b in bushes:
            if self.rect.colliderect(b):
                if random.random() < 0.02:
                    self.vx *= -1
                    self.vy *= -1

    def draw(self, surf):
        pygame.draw.rect(surf, ENEMY_COLOR, self.rect)

class Bush(RectEntity):
    def __init__(self, x, y, w, h):
        super().__init__((x, y, w, h))

    def draw(self, surf):
        # draw as rounded rectangle-like (ellipse + rect) for nicer look
        pygame.draw.ellipse(surf, BUSH_GREEN, self.rect)

class Fruit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, FRUIT_SIZE, FRUIT_SIZE)

    def draw(self, surf):
        pygame.draw.circle(surf, FRUIT_COLOR, self.rect.center, FRUIT_SIZE // 2)

# Utility: place non-overlapping bushes
def generate_bushes():
    bushes = []
    attempts = 0
    while len(bushes) < BUSH_COUNT and attempts < 2000:
        w = random.randint(BUSH_MIN_SIZE, BUSH_MAX_SIZE)
        h = random.randint(BUSH_MIN_SIZE // 2, BUSH_MAX_SIZE // 2)
        x = random.randint(0, WIDTH - w)
        y = random.randint(0, HEIGHT - h)
        new = pygame.Rect(x, y, w, h)
        collision = False
        for b in bushes:
            if new.colliderect(b):
                collision = True
                break
        if not collision:
            bushes.append(new)
        attempts += 1
    return [Bush(b.x, b.y, b.w, b.h) for b in bushes]

def spawn_fruit(bushes):
    # spawn fruit inside a random bush
    if not bushes:
        return None
    bush = random.choice(bushes)
    fx = random.randint(bush.rect.left + 8, bush.rect.right - FRUIT_SIZE - 8)
    fy = random.randint(bush.rect.top + 8, bush.rect.bottom - FRUIT_SIZE - 8)
    return Fruit(fx, fy)

# initialize
bushes = generate_bushes()
player = Player(WIDTH//2, HEIGHT//2)
enemies = []
for _ in range(ENEMY_COUNT):
    ex = random.randint(0, WIDTH-ENEMY_SIZE)
    ey = random.randint(0, HEIGHT-ENEMY_SIZE)
    enemies.append(Enemy(ex, ey))

fruits = []
# start with one fruit
first_fruit = spawn_fruit(bushes)
if first_fruit:
    fruits.append(first_fruit)

# timers
FRUIT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(FRUIT_EVENT, FRUIT_SPAWN_INTERVAL)

game_over = False
paused = False

def draw_hud():
    s_surf = font.render(f"Score: {player.score}", True, WHITE)
    l_surf = font.render(f"Lives: {player.lives}", True, WHITE)
    info = font.render("Move: Arrows/WASD  •  Hide in bushes  •  Collect fruits", True, WHITE)
    screen.blit(s_surf, (10, 10))
    screen.blit(l_surf, (10, 36))
    screen.blit(info, (10, HEIGHT - 30))

def reset_level():
    global bushes, enemies, fruits, player, game_over
    bushes = generate_bushes()
    player.rect.topleft = (WIDTH//2 - PLAYER_SIZE//2, HEIGHT//2 - PLAYER_SIZE//2)
    enemies.clear()
    for _ in range(ENEMY_COUNT):
        ex = random.randint(0, WIDTH-ENEMY_SIZE)
        ey = random.randint(0, HEIGHT-ENEMY_SIZE)
        enemies.append(Enemy(ex, ey))
    fruits.clear()
    f = spawn_fruit(bushes)
    if f: fruits.append(f)
    player.hidden = False
    game_over = False

# main loop
while True:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == FRUIT_EVENT and not game_over and not paused:
            f = spawn_fruit(bushes)
            if f:
                fruits.append(f)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if event.key == pygame.K_r and game_over:
                player.score = 0
                player.lives = 3
                reset_level()

    if not game_over and not paused:
        keys = pygame.key.get_pressed()
        player.update(keys)

        # determine hidden state: player is hidden if fully inside any bush
        player.hidden = False
        for b in bushes:
            if b.rect.contains(player.rect):
                player.hidden = True
                break

        # enemies update
        for e in enemies:
            e.update(bushes)

        # enemy collision with player
        for e in enemies:
            if e.rect.colliderect(player.rect):
                if not player.hidden:
                    # lose life
                    player.lives -= 1
                    # knockback player
                    player.rect.x = max(0, player.rect.x - 60)
                    player.rect.y = max(0, player.rect.y - 60)
                    if player.lives <= 0:
                        game_over = True
                else:
                    # if hidden, enemy doesn't detect - small shove back to enemy
                    # gently move enemy away
                    if e.vx == 0 and e.vy == 0:
                        e.vx = ENEMY_SPEED
                    e.rect.x += e.vx * 10
                    e.rect.y += e.vy * 10

        # fruit collection
        for f in fruits[:]:
            if f.rect.colliderect(player.rect):
                player.score += 10
                fruits.remove(f)

        # keep fruits inside bushes only (optional): remove fruits that are outside bushes (rare)
        for f in fruits[:]:
            inside_any = any(b.rect.colliderect(f.rect) for b in bushes)
            if not inside_any:
                fruits.remove(f)

    # draw
    screen.fill((46, 94, 138))  # background - sky blue
    # draw bushes (behind player)
    for b in bushes:
        b.draw(screen)

    # draw fruits (on top of bushes)
    for f in fruits:
        f.draw(screen)

    # draw player and enemies
    player.draw(screen)
    for e in enemies:
        e.draw(screen)

    # HUD
    draw_hud()

    if paused:
        ptext = font.render("PAUSED - Press P to resume", True, WHITE)
        screen.blit(ptext, (WIDTH//2 - ptext.get_width()//2, HEIGHT//2 - 30))
    if game_over:
        over1 = font.render("GAME OVER", True, WHITE)
        over2 = font.render("Press R to restart", True, WHITE)
        screen.blit(over1, (WIDTH//2 - over1.get_width()//2, HEIGHT//2 - 30))
        screen.blit(over2, (WIDTH//2 - over2.get_width()//2, HEIGHT//2 + 6))

    pygame.display.flip()
