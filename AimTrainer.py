import math
import random
import time
import pygame
import json

pygame.init()

WIDTH, HEIGHT = 800, 600

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30

BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50

LABEL_FONT = pygame.font.SysFont("comicsans", 24)
HIT_SOUND = pygame.mixer.Sound("shot_hit.mp3")
MISS_SOUND = pygame.mixer.Sound("gun_shot.wav")
LIFE_LOST = pygame.mixer.Sound("life_lost.wav")

class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.image = pygame.image.load("target.png")

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE
        self.image_scaled = pygame.transform.scale(self.image, (int(self.size * 2), int(self.size * 2)))  # Scale the image
    def draw(self, win):
        win.blit(self.image_scaled, (self.x - self.size, self.y - self.size))

    def collide(self, x, y):
        dis = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dis <= self.size

def draw(win, targets):
    win.fill(BG_COLOR)
    for target in targets:
        target.draw(win)

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))

def end_screen(win, elapsed_time, targets_pressed, clicks, heatmap, player_name):
    win.fill(BG_COLOR)
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")
    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()
    save_leaderboard(elapsed_time, targets_pressed, accuracy, player_name)
    generate_heatmap(heatmap)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                run = False

def get_middle(surface):
    return WIDTH / 2 - surface.get_width() / 2

def save_leaderboard(time, hits, accuracy, player_name):
    leaderboard_entry = {
        "player": player_name,
        "time": format_time(time),
        "hits": hits,
        "accuracy": accuracy
    }

    try:
        with open("leaderboard.json", "r") as file:
            leaderboard = json.load(file)
    except FileNotFoundError:
        leaderboard = []

    leaderboard.append(leaderboard_entry)
    leaderboard = sorted(leaderboard, key=lambda x: x['hits'], reverse=True)[:10]

    with open("leaderboard.json", "w") as file:
        json.dump(leaderboard, file, indent=4)

def generate_heatmap(heatmap):
    heatmap_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x, y in heatmap:
        pygame.draw.circle(heatmap_surface, (255, 0, 0, 50), (x, y), 20)
    pygame.image.save(heatmap_surface, "heatmap.png")

def draw_text(win, text, font, color, x, y):
    label = font.render(text, True, color)
    win.blit(label, (x - label.get_width() // 2, y))

def main_menu():
    run = True
    player_name = ""
    active = False  # Text field active status
    input_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 , 200, 40)  # Input field rectangle

    while run:
        WIN.fill(BG_COLOR)

        # Menu Title
        draw_text(WIN, "Aim Trainer", pygame.font.SysFont("comicsans", 50), "white", WIDTH // 2, HEIGHT // 3 -100)

        # Instructions and Options
        draw_text(WIN, "Enter your name:", LABEL_FONT, "white", WIDTH // 2, HEIGHT // 2 - 40)
        draw_text(WIN, "1. Play Game", LABEL_FONT, "white", WIDTH // 2, HEIGHT // 2 + 50)
        draw_text(WIN, "2. Leaderboards", LABEL_FONT, "white", WIDTH // 2, HEIGHT // 2 + 100)
        draw_text(WIN, "Press Esc to Quit", LABEL_FONT, "white", WIDTH // 2, HEIGHT // 2 + 150)

        # Render the current name entered
        pygame.draw.rect(WIN, "white", input_rect, 2)  # Draw input field box
        draw_text(WIN, player_name, LABEL_FONT, "white", input_rect.centerx-15, input_rect.centery-15)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_1 and player_name:
                    run = False  # Exit menu and start game
                if event.key == pygame.K_2:
                    show_leaderboards()

                if active:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]  # Remove last character
                    elif event.key == pygame.K_RETURN:
                        active = False  # Deactivate text field
                    else:
                        player_name += event.unicode  # Add character to name

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True  # Activate text field
                else:
                    active = False  # Deactivate text field
    return player_name

def show_leaderboards():
    run = True
    while run:
        WIN.fill(BG_COLOR)

        # Display the Leaderboard title
        draw_text(WIN, "Leaderboards", pygame.font.SysFont("comicsans", 50), "white", WIDTH // 2, HEIGHT // 6)

        # Load the leaderboard data
        try:
            with open("leaderboard.json", "r") as file:
                leaderboard = json.load(file)
        except FileNotFoundError:
            leaderboard = []

        # Display only the top 5 entries
        for i, entry in enumerate(leaderboard[:5]):
            text = f"{i + 1}. {entry['player']} - Hits: {entry['hits']} - Time: {entry['time']} - Accuracy: {entry['accuracy']}%"
            draw_text(WIN, text, LABEL_FONT, "white", WIDTH // 2, HEIGHT // 6 + 50 * (i + 2))

        # Instruction to return to the main menu
        draw_text(WIN, "Press any key to return to the main menu", LABEL_FONT, "white", WIDTH // 2, HEIGHT - 50)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                run = False


def main():
    
    player_name = main_menu()
    player_name = player_name[:len(player_name)-1]
    run = True

    targets = []
    clock = pygame.time.Clock()

    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()
    heatmap = []

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1
                heatmap.append(mouse_pos)

        for target in targets:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                misses += 1
                LIFE_LOST.play()

            if click:
                if target.collide(*mouse_pos):
                    targets.remove(target)
                    targets_pressed += 1
                    HIT_SOUND.play()
                else:
                    MISS_SOUND.play()


        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks, heatmap, player_name)
            run = False

        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()