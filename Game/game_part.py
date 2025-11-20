import argparse
import random
import pygame
import sys
import time
import csv
from pathlib import Path

parser = argparse.ArgumentParser(description="Play the Color Sort game.")
parser.add_argument(
    "--input-source",
    choices=["mouse", "hand_tracking"],
    default="mouse",
    help="Input modality used to interact with the game; saved alongside the results.",
)
args = parser.parse_args()
INPUT_SOURCE = args.input_source

# Initialize pygame
pygame.init()

display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Random Color Sort - Fix")

# Fonts
FONT_BIG = pygame.font.SysFont(None, 72)
FONT_MED = pygame.font.SysFont(None, 40)
FONT_SMALL = pygame.font.SysFont(None, 28)
MOUSE_STATUS_FONT = pygame.font.SysFont(None, 32)

ROUND_TARGET = 10  # number of blocks the player needs to sort
TOTAL_CYCLES = 3
DATA_DIR = Path(__file__).resolve().parent.parent / "Data"

# Helpers
def random_color(min_val=30):
    """Return a visually distinct random color (avoid too-dark)."""
    return (random.randint(min_val, 255), random.randint(min_val, 255), random.randint(min_val, 255))

# Bins (fixed positions)
BIN_W, BIN_H = 220, 160
BIN_BOTTOM_MARGIN = 30
BIN_Y = HEIGHT - BIN_H - BIN_BOTTOM_MARGIN

def calculate_bin_positions(width):
    """Return three X offsets that keep the bins evenly spaced."""
    available_space = max(width - BIN_W * 3, 0)
    gap = available_space // 4  # leading gap plus gap between bins
    return [gap, gap * 2 + BIN_W, gap * 3 + 2 * BIN_W]

BIN_XS = calculate_bin_positions(WIDTH)

def make_bins():
    """Create three bins with random colors (duplicates allowed)."""
    return [{"rect": pygame.Rect(x, BIN_Y, BIN_W, BIN_H), "color": random_color()} for x in BIN_XS]

bins = make_bins()

# Block settings
BLOCK_SIZE = 96
BLOCK_START = (WIDTH//2 - BLOCK_SIZE//2, 150)
block_rect = pygame.Rect(*BLOCK_START, BLOCK_SIZE, BLOCK_SIZE)
block_color = None
dragging = False
offset_x = offset_y = 0

# Game state
score = 0
game_state = "menu"  # "menu", "playing", "gameover"
rounds_completed = 0
cycle_complete = False
round_results = []
current_wrong_attempts = 0
sort_durations = []
current_block_start_time = None
clock = pygame.time.Clock()
mouse_status = "Mouse Up"

def spawn_block_from_bins(track_time=True):
    """Choose the block color to match one of the current bin colors (so it's always placeable)."""
    global block_rect, block_color, current_block_start_time
    block_rect.topleft = BLOCK_START
    # pick a bin, then use its current color for the block
    chosen_bin = random.choice(bins)
    block_color = chosen_bin["color"]
    if track_time:
        current_block_start_time = time.time()
    else:
        current_block_start_time = None


def record_sort_duration():
    """Capture how long the current block took to place."""
    global current_block_start_time
    if current_block_start_time is None:
        return
    duration = max(time.time() - current_block_start_time, 0)
    sort_durations.append(duration)
    current_block_start_time = None


def export_round_results():
    """Write the per-round stats to a CSV file in the Data directory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("session_%Y%m%d_%H%M%S.csv")
    export_path = DATA_DIR / timestamp
    with export_path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["round", "average_time_seconds", "wrong_squares", "input_type"])
        for result in round_results:
            writer.writerow(
                [result["round"], f"{result['average_time']:.3f}", result["wrong_attempts"], INPUT_SOURCE]
            )
    print(f"[Data] Saved round data to {export_path}")

def reset_round():
    """Reset score and respawn bins for a new round."""
    global score, bins, block_rect, dragging, current_wrong_attempts, sort_durations
    score = 0
    bins = make_bins()
    block_rect.topleft = BLOCK_START
    dragging = False
    current_wrong_attempts = 0
    sort_durations = []
    spawn_block_from_bins()

def finish_round():
    """Advance round counter, capture stats, and show the results screen."""
    global game_state, rounds_completed, cycle_complete, round_results, current_block_start_time
    if game_state == "gameover":
        return

    average_time = sum(sort_durations) / len(sort_durations) if sort_durations else 0.0
    round_number = len(round_results) + 1
    round_results.append(
        {
            "round": round_number,
            "average_time": average_time,
            "wrong_attempts": current_wrong_attempts,
        }
    )

    rounds_completed = len(round_results)
    current_block_start_time = None
    if rounds_completed >= TOTAL_CYCLES:
        cycle_complete = True
        export_round_results()
    game_state = "gameover"

def draw_menu():
    screen.fill((30, 30, 30))
    title = FONT_BIG.render("Color Sort", True, (255,255,255))
    prompt_text = "Cycle complete! Click to restart" if cycle_complete else "Click to Start"
    prompt = FONT_MED.render(prompt_text, True, (200,200,200))
    progress = FONT_SMALL.render(f"Rounds: {rounds_completed}/{TOTAL_CYCLES}", True, (200,200,200))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 300))
    screen.blit(progress, (WIDTH//2 - progress.get_width()//2, 360))

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
    score_surf = FONT_SMALL.render(f"Score: {score}/{ROUND_TARGET}", True, (255,255,255))
    screen.blit(score_surf, (20, 20))

def draw_gameover():
    screen.fill((10, 10, 10))
    over = FONT_BIG.render("Game Over", True, (220, 40, 40))
    if score >= ROUND_TARGET:
        score_txt = FONT_MED.render("You sorted them all!", True, (230,230,230))
    else:
        score_txt = FONT_MED.render(f"Final Score: {score}", True, (230,230,230))
    round_txt = FONT_SMALL.render(f"Rounds played: {rounds_completed}/{TOTAL_CYCLES}", True, (200,200,200))
    latest_stats = round_results[-1] if round_results else None
    if latest_stats:
        wrong_txt = FONT_SMALL.render(f"Wrong placements: {latest_stats['wrong_attempts']}", True, (200,200,200))
        avg_txt = FONT_SMALL.render(f"Avg sort time: {latest_stats['average_time']:.2f}s", True, (200,200,200))
    else:
        wrong_txt = avg_txt = None
    retry = FONT_SMALL.render("Click to return to menu", True, (200,200,200))
    screen.blit(over, (WIDTH//2 - over.get_width()//2, 150))
    screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 260))
    screen.blit(round_txt, (WIDTH//2 - round_txt.get_width()//2, 310))
    if wrong_txt:
        screen.blit(wrong_txt, (WIDTH//2 - wrong_txt.get_width()//2, 340))
    if avg_txt:
        screen.blit(avg_txt, (WIDTH//2 - avg_txt.get_width()//2, 370))
    screen.blit(retry, (WIDTH//2 - retry.get_width()//2, 410))

# Initialize first block (without starting the timer until gameplay begins)
spawn_block_from_bins(track_time=False)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_status = "Mouse Down"
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_status = "Mouse Up"

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # start game
                if cycle_complete:
                    rounds_completed = 0
                    cycle_complete = False
                    round_results.clear()
                reset_round()
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
                                record_sort_duration()
                                score += 1
                                b["color"] = random_color()
                                if score >= ROUND_TARGET:
                                    finish_round()
                                else:
                                    spawn_block_from_bins()
                            else:
                                # wrong -> reset block to start so user can try again
                                current_wrong_attempts += 1
                                block_rect.topleft = BLOCK_START

                            break

                    if not placed:
                        # dropped outside bins -> reset to start
                        block_rect.topleft = BLOCK_START

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
    status_surf = MOUSE_STATUS_FONT.render(mouse_status, True, (255, 255, 255))
    screen.blit(status_surf, (WIDTH - status_surf.get_width() - 20, 20))

    pygame.display.flip()
    clock.tick(60)
