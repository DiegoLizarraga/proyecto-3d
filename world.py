import pygame
import random

from settings import TILE_SIZE

# Mapa del mundo (mantiene el diseño original)
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

# Texturas procedurales para el sistema 3D
def create_brick_texture(size):
    """Crea una textura de ladrillos procedural"""
    surf = pygame.Surface((size, size))
    brick_color = (180, 60, 60)
    mortar_color = (200, 200, 200)
    surf.fill(mortar_color)
    brick_width = size // 8
    brick_height = size // 16
    for row in range(0, size, brick_height):
        offset = 0 if (row // brick_height) % 2 == 0 else brick_width // 2
        for col in range(-offset, size + brick_width, brick_width):
            pygame.draw.rect(surf, brick_color, (col, row, brick_width - 2, brick_height - 2))
    return surf

def create_white_texture(size):
    """Crea una textura blanca con ruido para simular piedra"""
    surf = pygame.Surface((size, size))
    for x in range(size):
        for y in range(size):
            noise = random.randint(-20, 20)
            c = max(0, min(255, 220 + noise))
            surf.set_at((x, y), (c, c, c))
    return surf

# Diccionario de texturas (usado en el sistema antiguo, mantenido por compatibilidad)
WALL_TEXTURES = {
    1: create_brick_texture(TILE_SIZE),
    2: create_white_texture(TILE_SIZE),
}

# Almacenamiento de graffiti
# Clave: (x, z, face) donde face puede ser 'N', 'S', 'E', 'W'
# Valor: superficie pygame con el graffiti dibujado
graffiti_walls = {}