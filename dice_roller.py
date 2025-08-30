import pygame
import random
import math
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎲 Dice Rolling Simulator")

BACKGROUND = (25, 25, 50)
DICE_COLOR = (245, 245, 245)
DOT_COLOR = (25, 25, 50)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (15, 15, 35)

title_font = pygame.font.SysFont("Arial", 48, bold=True)
button_font = pygame.font.SysFont("Arial", 28)
result_font = pygame.font.SysFont("Arial", 36, bold=True)
history_font = pygame.font.SysFont("Arial", 20)

try:
    roll_sound = pygame.mixer.Sound("roll.wav")
except:
    roll_sound = pygame.mixer.Sound(buffer=bytearray([]))

dice_value = 1
rolling = False
roll_animation_time = 0
roll_history = []
max_history = 10

button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)

dot_positions = {
    1: [(0, 0)],
    2: [(-1, -1), (1, 1)],
    3: [(-1, -1), (0, 0), (1, 1)],
    4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
    6: [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0)]
}

def draw_dice(x, y, size, value, rotation=0):
    shadow_offset = 5
    pygame.draw.rect(screen, SHADOW_COLOR, 
                    (x - size//2 + shadow_offset, y - size//2 + shadow_offset, size, size), 
                    0, 15)
    
    pygame.draw.rect(screen, DICE_COLOR, (x - size//2, y - size//2, size, size), 0, 15)
    pygame.draw.rect(screen, (200, 200, 200), (x - size//2, y - size//2, size, size), 3, 15)
    
    dot_radius = size // 10
    dot_spacing = size // 4
    
    for dx, dy in dot_positions[value]:
        dot_x = x + dx * dot_spacing
        dot_y = y + dy * dot_spacing
        
        angle = math.radians(rotation)
        rotated_x = x + (dot_x - x) * math.cos(angle) - (dot_y - y) * math.sin(angle)
        rotated_y = y + (dot_x - x) * math.sin(angle) + (dot_y - y) * math.cos(angle)
        
        pygame.draw.circle(screen, DOT_COLOR, (int(rotated_x), int(rotated_y)), dot_radius)

def draw_button():
    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    
    pygame.draw.rect(screen, button_color, button_rect, 0, 15)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, 15)
    
    text = button_font.render("Roll Dice", True, TEXT_COLOR)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

def draw_history():
    title = history_font.render("Roll History:", True, TEXT_COLOR)
    screen.blit(title, (50, 120))
    
    for i, (roll, value) in enumerate(roll_history[-max_history:]):
        text = history_font.render(f"Roll {roll}: {value}", True, TEXT_COLOR)
        screen.blit(text, (50, 150 + i * 25))

def draw_stats():
    if not roll_history:
        return
        
    values = [value for _, value in roll_history]
    total_rolls = len(values)
    
    freq = {i: values.count(i) for i in range(1, 7)}
    most_common = max(freq, key=freq.get)
    least_common = min(freq, key=freq.get)
    
    stats_text = [
        f"Total Rolls: {total_rolls}",
        f"Most Common: {most_common} ({freq[most_common]}/{total_rolls})",
        f"Least Common: {least_common} ({freq[least_common]}/{total_rolls})"
    ]
    
    for i, text in enumerate(stats_text):
        rendered = history_font.render(text, True, TEXT_COLOR)
        screen.blit(rendered, (WIDTH - 250, 120 + i * 25))

clock = pygame.time.Clock()
roll_count = 1

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos) and not rolling:
                rolling = True
                roll_animation_time = 0
                roll_sound.play()
    
    screen.fill(BACKGROUND)
    
    title = title_font.render("Dice Rolling Simulator", True, TEXT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    if rolling:
        roll_animation_time += 1
        anim_value = random.randint(1, 6)
        rotation = roll_animation_time * 10
        
        draw_dice(WIDTH//2, HEIGHT//2 - 50, 200, anim_value, rotation)
        
        if roll_animation_time > 60:
            rolling = False
            dice_value = random.randint(1, 6)
            roll_history.append((roll_count, dice_value))
            roll_count += 1
    else:
        draw_dice(WIDTH//2, HEIGHT//2 - 50, 200, dice_value)
    
    result_text = result_font.render(f"Result: {dice_value}", True, TEXT_COLOR)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 + 80))
    
    draw_button()
    
    draw_history()
    draw_stats()
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()