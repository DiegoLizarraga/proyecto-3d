import pygame
import math

from settings import *
from world import graffiti_walls, WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

def draw_minimap(screen, player):
    minimap_size = 180
    minimap_scale = minimap_size / (MAP_WIDTH * TILE_SIZE)
    pygame.draw.rect(screen, BLACK, (8, 8, minimap_size + 4, minimap_size + 4))
    pygame.draw.rect(screen, WHITE, (10, 10, minimap_size, minimap_size))
    tile_width = minimap_size // MAP_WIDTH
    tile_height = minimap_size // MAP_HEIGHT
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall_type = WORLD_MAP[y][x]
            if wall_type == 0:
                color = DARK_GRAY
            elif wall_type == 1:
                color = LIGHT_GRAY
            elif wall_type == 2:
                color = WHITE
            else:
                color = GRAY
            rect_x = 10 + x * tile_width
            rect_y = 10 + y * tile_height
            pygame.draw.rect(screen, color, (rect_x, rect_y, tile_width, tile_height))
            # Marcar graffiti
            if (x, y) in graffiti_walls:
                pygame.draw.circle(screen, RED, (rect_x + tile_width // 2, rect_y + tile_height // 2), 2)
    # Jugador
    player_x = 10 + int(player.x * minimap_scale)
    player_y = 10 + int(player.y * minimap_scale)
    pygame.draw.circle(screen, BLACK, (player_x, player_y), 4)
    pygame.draw.circle(screen, BLUE, (player_x, player_y), 2)
    # Dirección
    end_x = player_x + math.cos(math.radians(player.angle)) * 12
    end_y = player_y + math.sin(math.radians(player.angle)) * 12
    pygame.draw.line(screen, BLUE, (player_x, player_y), (end_x, end_y), 2)

def draw_ui(screen, player):
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    # Barra de stamina
    stamina_width = 150
    stamina_height = 15
    stamina_x = 20
    stamina_y = WINDOW_HEIGHT - 60
    pygame.draw.rect(screen, BLACK, (stamina_x - 2, stamina_y - 2, stamina_width + 4, stamina_height + 4))
    pygame.draw.rect(screen, DARK_GRAY, (stamina_x, stamina_y, stamina_width, stamina_height))
    current_width = int((player.stamina / STAMINA_MAX) * stamina_width)
    stamina_color = GREEN if player.stamina > 30 else (YELLOW if player.stamina > 10 else RED)
    pygame.draw.rect(screen, stamina_color, (stamina_x, stamina_y, current_width, stamina_height))
    stamina_text = small_font.render(f"Stamina: {int(player.stamina)}", True, WHITE)
    screen.blit(stamina_text, (stamina_x, stamina_y - 18))
    # Controles
    controls_text = [
        "=== CONTROLES ===",
        "Movimiento:",
        "W/↑ - Avanzar",
        "S/↓ - Retroceder",
        "A/← - Girar izq",
        "D/→ - Girar der",
        "Q/E - Lateral",
        "SHIFT - Correr",
        "",
        "Graffiti:",
        "Z - Modo paint (cerca de pared)",
        "C - Limpiar todo",
        "",
        "ESC - Salir"
    ]
    controls_start_y = WINDOW_HEIGHT - (len(controls_text) * 16) + 20  # Ajuste
    controls_x = WINDOW_WIDTH - 180
    for i, text in enumerate(controls_text):
        if text == "=== CONTROLES ===":
            color = YELLOW
        elif text in ("Movimiento:", "Graffiti:"):
            color = WHITE
        else:
            color = LIGHT_GRAY
        surf = small_font.render(text, True, color)
        screen.blit(surf, (controls_x, controls_start_y + i * 16))
    # Contador de graffitis
    total_walls = len(graffiti_walls)
    counter = font.render(f"Paredes con graffiti: {total_walls}", True, YELLOW)
    screen.blit(counter, (20, WINDOW_HEIGHT - 90))
    if total_walls > 0:
        clear_text = small_font.render("Presiona C para limpiar", True, RED)
        screen.blit(clear_text, (20, WINDOW_HEIGHT - 70))