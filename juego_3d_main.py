import pygame
import math
import sys

# Inicializar Pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Configuración del jugador
PLAYER_SPEED = 3
TURN_SPEED = 3
FOV = 60  # Campo de visión
HALF_FOV = FOV / 2
NUM_RAYS = WINDOW_WIDTH // 2  # Número de rayos para el raycasting

# Mapa del mundo (1 = pared, 0 = espacio vacío)
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
TILE_SIZE = 64

class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
    
    def update(self, keys):
        # Rotación
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= TURN_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += TURN_SPEED
        
        # Normalizar el ángulo
        self.angle = self.angle % 360
        
        # Movimiento
        dx = 0
        dy = 0
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dx = math.cos(math.radians(self.angle)) * PLAYER_SPEED
            dy = math.sin(math.radians(self.angle)) * PLAYER_SPEED
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx = -math.cos(math.radians(self.angle)) * PLAYER_SPEED
            dy = -math.sin(math.radians(self.angle)) * PLAYER_SPEED
        
        # Verificar colisiones antes de mover
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Obtener posición en el mapa
        map_x = int(new_x // TILE_SIZE)
        map_y = int(new_y // TILE_SIZE)
        
        # Verificar límites del mapa
        if (0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT):
            # Verificar colisión X
            if WORLD_MAP[int(self.y // TILE_SIZE)][map_x] == 0:
                self.x = new_x
            
            # Verificar colisión Y
            if WORLD_MAP[map_y][int(self.x // TILE_SIZE)] == 0:
                self.y = new_y

def cast_ray(start_x, start_y, angle):
    """Lanza un rayo y devuelve la distancia hasta la primera pared"""
    # Convertir ángulo a radianes
    angle_rad = math.radians(angle)
    
    # Dirección del rayo
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    
    # Incremento pequeño para el rayo
    step = 1
    
    x = start_x
    y = start_y
    
    while True:
        # Avanzar el rayo
        x += dx * step
        y += dy * step
        
        # Convertir a coordenadas del mapa
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        # Verificar si estamos fuera del mapa
        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            break
        
        # Verificar si golpeamos una pared
        if WORLD_MAP[map_y][map_x] == 1:
            # Calcular distancia
            distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            return distance, map_x, map_y
    
    return float('inf'), 0, 0

def render_3d(screen, player):
    """Renderiza la vista 3D usando raycasting"""
    
    # Limpiar pantalla
    screen.fill(BLACK)
    
    # Dibujar cielo (mitad superior)
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT // 2))
    
    # Dibujar suelo (mitad inferior)
    pygame.draw.rect(screen, GRAY, (0, WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT // 2))
    
    # Calcular el ángulo inicial
    start_angle = player.angle - HALF_FOV
    
    # Lanzar rayos
    for i in range(NUM_RAYS):
        # Calcular el ángulo del rayo actual
        ray_angle = start_angle + (i * FOV / NUM_RAYS)
        
        # Lanzar el rayo
        distance, wall_x, wall_y = cast_ray(player.x, player.y, ray_angle)
        
        if distance != float('inf'):
            # Corregir el efecto "ojo de pez"
            corrected_distance = distance * math.cos(math.radians(ray_angle - player.angle))
            
            # Calcular altura de la pared en pantalla
            if corrected_distance > 0:
                wall_height = (TILE_SIZE * WINDOW_HEIGHT) / corrected_distance
            else:
                wall_height = WINDOW_HEIGHT
            
            # Limitar la altura de la pared
            wall_height = min(wall_height, WINDOW_HEIGHT)
            
            # Calcular posición vertical de la pared
            wall_top = (WINDOW_HEIGHT - wall_height) // 2
            wall_bottom = wall_top + wall_height
            
            # Calcular color basado en la distancia (más lejos = más oscuro)
            shade = max(50, 255 - int(distance * 2))
            wall_color = (shade // 3, shade // 3, shade)  # Color grisáceo
            
            # Dibujar la columna de la pared
            x = i * 2  # Cada rayo dibuja 2 píxeles de ancho
            pygame.draw.rect(screen, wall_color, (x, wall_top, 2, wall_height))

def draw_minimap(screen, player):
    """Dibuja un minimapa en la esquina superior izquierda"""
    minimap_size = 150
    minimap_scale = minimap_size / (MAP_WIDTH * TILE_SIZE)
    #neta como se batalla con esto jeje


    # Fondo del minimapa
    pygame.draw.rect(screen, BLACK, (10, 10, minimap_size, minimap_size))
    
    # Dibujar el mapa
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            color = WHITE if WORLD_MAP[y][x] == 1 else DARK_GRAY
            rect_x = 10 + x * (minimap_size // MAP_WIDTH)
            rect_y = 10 + y * (minimap_size // MAP_HEIGHT)
            rect_width = minimap_size // MAP_WIDTH
            rect_height = minimap_size // MAP_HEIGHT
            pygame.draw.rect(screen, color, (rect_x, rect_y, rect_width, rect_height))
    
    # Dibujar al jugador
    player_x = 10 + player.x * minimap_scale
    player_y = 10 + player.y * minimap_scale
    pygame.draw.circle(screen, RED, (int(player_x), int(player_y)), 3)
    
    # Dibujar dirección del jugador
    end_x = player_x + math.cos(math.radians(player.angle)) * 15
    end_y = player_y + math.sin(math.radians(player.angle)) * 15
    pygame.draw.line(screen, RED, (player_x, player_y), (end_x, end_y), 2)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Juego 3D de prueba - Python")
    clock = pygame.time.Clock()
    
    # Crear jugador (posición inicial en el centro del mapa)
    player = Player(TILE_SIZE * 1.5, TILE_SIZE * 1.5, 0)
    
    running = True
    while running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Input
        keys = pygame.key.get_pressed()
        player.update(keys)
        
        # Renderizado
        render_3d(screen, player)
        draw_minimap(screen, player)
        
        # Mostrar controles
        font = pygame.font.Font(None, 36)
        controls_text = [
            "Controles:",
            "W/↑ - Avanzar",
            "S/↓ - Retroceder", 
            "A/← - Girar izquierda",
            "D/→ - Girar derecha",
            "ESC - Salir"
        ]
        
        for i, text in enumerate(controls_text):
            color = WHITE if i == 0 else GRAY
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (WINDOW_WIDTH - 200, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()