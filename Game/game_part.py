import random
import pygame
import sys

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Color Sort - Fix")

# Fonts
FONT_BIG = pygame.font.SysFont(None, 72)
FONT_MED = pygame.font.SysFont(None, 40)
FONT_SMALL = pygame.font.SysFont(None, 28)

# Helpers
def random_color(min_val=30):
    """Return a visually distinct random color (avoid too-dark)."""
    return (random.randint(min_val, 255), random.randint(min_val, 255), random.randint(min_val, 255))

# Bins (fixed positions)
BIN_W, BIN_H = 160, 120
BIN_Y = HEIGHT - 150
BIN_XS = [90, 320, 550]

def make_bins():
    """Create three bins with random colors (duplicates allowed)."""
    return [{"rect": pygame.Rect(x, BIN_Y, BIN_W, BIN_H), "color": random_color()} for x in BIN_XS]

bins = make_bins()

# Block settings
BLOCK_SIZE = 64
BLOCK_START = (WIDTH//2 - BLOCK_SIZE//2, 150)
block_rect = pygame.Rect(*BLOCK_START, BLOCK_SIZE, BLOCK_SIZE)
block_color = None
dragging = False
offset_x = offset_y = 0

# Game state
score = 0
lives = 3
game_state = "menu"  # "menu", "playing", "gameover"
clock = pygame.time.Clock()

def spawn_block_from_bins():
    """Choose the block color to match one of the current bin colors (so it's always placeable)."""
    global block_rect, block_color
    block_rect.topleft = BLOCK_START
    # pick a bin, then use its current color for the block
    chosen_bin = random.choice(bins)
    block_color = chosen_bin["color"]

def draw_menu():
    screen.fill((30, 30, 30))
    title = FONT_BIG.render("Color Sort", True, (255,255,255))
    prompt = FONT_MED.render("Click to Start", True, (200,200,200))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 300))

def draw_game():
    screen.fill((25, 25, 30))
    # Draw bins (fixed positions, dynamic colors)
    for b in bins:
        pygame.draw.rect(screen, b["color"], b["rect"], border_radius=10)
        pygame.draw.rect(screen, (0,0,0), b["rect"], width=3, border_radius=10)  # outline

    # Draw block
    pygame.draw.rect(screen, block_color, block_rect, border_radius=8)
    pygame.draw.rect(screen, (0,0,0), block_rect, width=2, border_radius=8)

    # HUD
    score_surf = FONT_SMALL.render(f"Score: {score}", True, (255,255,255))
    lives_surf = FONT_SMALL.render(f"Lives: {lives}", True, (255,255,255))
    screen.blit(score_surf, (20, 20))
    screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 20, 20))

def draw_gameover():
    screen.fill((10, 10, 10))
    over = FONT_BIG.render("Game Over", True, (220, 40, 40))
    score_txt = FONT_MED.render(f"Final Score: {score}", True, (230,230,230))
    retry = FONT_SMALL.render("Click to return to menu", True, (200,200,200))
    screen.blit(over, (WIDTH//2 - over.get_width()//2, 150))
    screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 260))
    screen.blit(retry, (WIDTH//2 - retry.get_width()//2, 350))

# Initialize first block
spawn_block_from_bins()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # start game
                score = 0
                lives = 3
                bins = make_bins()
                spawn_block_from_bins()
                game_state = "playing"

        elif game_state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if block_rect.collidepoint(event.pos):
                    dragging = True
                    mx, my = event.pos
                    offset_x = block_rect.x - mx
                    offset_y = block_rect.y - my

            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                block_rect.x = mx + offset_x
                block_rect.y = my + offset_y

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    dragging = False
                    placed = False
                    # Check collision with bins
                    for b in bins:
                        if block_rect.colliderect(b["rect"]):
                            placed = True
                            # compare colors directly (exact match because block color came from a bin)
                            if block_color == b["color"]:
                                # correct
                                score += 1
                                # change THAT bin's color to a brand new random color
                                b["color"] = random_color()
                                # spawn the next block using updated bins (ensures it's placeable)
                                spawn_block_from_bins()
                            else:
                                # wrong
                                lives -= 1
                                # reset block position (keep same color so user can try again)
                                block_rect.topleft = BLOCK_START

                            break

                    if not placed:
                        # dropped outside bins -> reset to start
                        block_rect.topleft = BLOCK_START

                    if lives <= 0:
                        game_state = "gameover"

        elif game_state == "gameover":
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = "menu"

    # Draw according to state
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "gameover":
        draw_gameover()

    pygame.display.flip()
    clock.tick(60)