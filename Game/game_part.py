import random
import pygame
import sys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collect the Stars!")

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 102, 204)
GRAY = (200, 200, 200)

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()

# --- Helper function to draw text ---
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

# --- Button function ---
def draw_button(surface, text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Detect hover
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(surface, active_color, (x, y, w, h))
        if click[0] == 1:  # Left click
            pygame.time.delay(200)
            return True
    else:
        pygame.draw.rect(surface, inactive_color, (x, y, w, h))

    draw_text(text, small_font, BLACK, surface, x + w // 2, y + h // 2)
    return False

# --- Game Loop Function ---
def game_loop(mouse_control=False):
    player_size = 30
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    speed = 5

    item_size = 20
    item_x = random.randint(0, WIDTH - item_size)
    item_y = random.randint(0, HEIGHT - item_size)
    score = 0

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False  # return to menu if ESC pressed

        if mouse_control:
            # Center the player on the mouse position
            mx, my = pygame.mouse.get_pos()
            player_x = mx - player_size // 2
            player_y = my - player_size // 2
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: player_y -= speed
            if keys[pygame.K_s]: player_y += speed
            if keys[pygame.K_a]: player_x -= speed
            if keys[pygame.K_d]: player_x += speed

        # Keep player in bounds
        player_x = max(0, min(WIDTH - player_size, player_x))
        player_y = max(0, min(HEIGHT - player_size, player_y))

        # Check collision
        if (player_x < item_x + item_size and
            player_x + player_size > item_x and
            player_y < item_y + item_size and
            player_y + player_size > item_y):
            score += 1
            item_x = random.randint(0, WIDTH - item_size)
            item_y = random.randint(0, HEIGHT - item_size)

        # Draw game
        win.fill(SKY_BLUE)
        pygame.draw.rect(win, BLACK, (player_x, player_y, player_size, player_size))
        pygame.draw.rect(win, YELLOW, (item_x, item_y, item_size, item_size))
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        win.blit(score_text, (10, 10))
        pygame.display.update()

# --- Main Menu ---
def main_menu():
    in_menu = True
    while in_menu:
        win.fill(SKY_BLUE)
        draw_text("Collect the Stars!", font, BLACK, win, WIDTH // 2, HEIGHT // 4)

        # Draw buttons
        if draw_button(win, "Play (WASD)", WIDTH // 2 - 75, HEIGHT // 2 - 75, 150, 50, GRAY, DARK_BLUE):
            in_menu = False
            game_loop(mouse_control=False)

        if draw_button(win, "Play (Mouse)", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, GRAY, DARK_BLUE):
            in_menu = False
            game_loop(mouse_control=True)

        if draw_button(win, "Quit", WIDTH // 2 - 75, HEIGHT // 2 + 75, 150, 50, GRAY, DARK_BLUE):
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)

# --- Run the menu ---
main_menu()