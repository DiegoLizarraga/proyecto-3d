import pygame
import math

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 220, 220)
GRAY = (160, 160, 160)
DARK_GRAY = (100, 100, 100)
VERY_DARK_GRAY = (60, 60, 60)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
PINK = (255, 100, 150)
ORANGE = (255, 150, 50)
PURPLE = (150, 50, 255)
CYAN = (50, 255, 255)

# Configuración de ventana
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Configuración del jugador
PLAYER_SPEED = 2.5
RUN_SPEED = 4.5
TURN_SPEED = 3
FOV = 60
HALF_FOV = FOV / 2
NUM_RAYS = WINDOW_WIDTH  # Aumentado para reducir pixelación
STAMINA_MAX = 100
STAMINA_REGEN = 1.5
STAMINA_DRAIN = 2.0
SPRAY_RANGE = 64 * 1.5  # TILE_SIZE * 1.5

# Mapa
TILE_SIZE = 64

# Graffiti
GRAFFITI_SIZE = 256  # Resolución más alta para graffiti
SPRAY_COLORS = [RED, BLUE, GREEN, YELLOW, PINK, ORANGE, PURPLE, CYAN]