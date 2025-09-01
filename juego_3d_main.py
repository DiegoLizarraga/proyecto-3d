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
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BROWN = (139, 69, 19)
DARK_BLUE = (0, 0, 139)
DARK_GREEN = (0, 100, 0)

# Configuración del jugador
PLAYER_SPEED = 2.5  # Velocidad de caminar
RUN_SPEED = 4.5     # Velocidad de correr
TURN_SPEED = 3
FOV = 60  # Campo de visión
HALF_FOV = FOV / 2
NUM_RAYS = WINDOW_WIDTH // 2  # Número de rayos para el raycasting

# Mapa del mundo expandido (1 = pared básica, 2 = pared especial, 0 = espacio vacío)
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 0, 2, 2, 0, 1, 1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 2, 0, 1, 1, 0, 0, 1, 1, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 2, 0, 1, 1, 0, 0, 1, 1, 0, 2, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 2, 2, 0, 0, 2, 2, 0, 1, 1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
TILE_SIZE = 64

# Diccionario de colores para diferentes tipos de paredes
WALL_COLORS = {
    1: (100, 100, 100),    # Pared básica gris
    2: (139, 69, 19),      # Pared especial marrón
}

class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_running = False
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen_rate = 1.5
        self.stamina_drain_rate = 2.0
    
    def update(self, keys):
        # Verificar si el jugador quiere correr (mantener shift presionado)
        running_keys = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Solo puede correr si tiene stamina
        if running_keys and self.stamina > 0:
            self.is_running = True
            self.stamina -= self.stamina_drain_rate
        else:
            self.is_running = False
            # Regenerar stamina cuando no está corriendo
            if self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen_rate
        
        # Limitar stamina entre 0 y max
        self.stamina = max(0, min(self.max_stamina, self.stamina))
        
        # Determinar velocidad actual
        current_speed = RUN_SPEED if self.is_running else PLAYER_SPEED
        
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
            dx = math.cos(math.radians(self.angle)) * current_speed
            dy = math.sin(math.radians(self.angle)) * current_speed
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx = -math.cos(math.radians(self.angle)) * current_speed
            dy = -math.sin(math.radians(self.angle)) * current_speed
        
        # Movimiento lateral (strafing)
        if keys[pygame.K_q]:
            dx += math.cos(math.radians(self.angle - 90)) * current_speed
            dy += math.sin(math.radians(self.angle - 90)) * current_speed
        
        if keys[pygame.K_e]:
            dx += math.cos(math.radians(self.angle + 90)) * current_speed
            dy += math.sin(math.radians(self.angle + 90)) * current_speed
        
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
    """Lanza un rayo y devuelve la distancia hasta la primera pared y su tipo"""
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
        wall_type = WORLD_MAP[map_y][map_x]
        if wall_type != 0:
            # Calcular distancia
            distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            return distance, map_x, map_y, wall_type
    
    return float('inf'), 0, 0, 0

def render_3d(screen, player):
    """Renderiza la vista 3D usando raycasting"""
    
    # Limpiar pantalla
    screen.fill(BLACK)
    
    # Dibujar cielo (mitad superior) con gradiente
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(50 + (i * 50) / (WINDOW_HEIGHT // 2))
        sky_color = (color_intensity // 4, color_intensity // 4, color_intensity)
        pygame.draw.line(screen, sky_color, (0, i), (WINDOW_WIDTH, i))
    
    # Dibujar suelo (mitad inferior) con gradiente
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(100 - (i * 50) / (WINDOW_HEIGHT // 2))
        floor_color = (color_intensity // 2, color_intensity // 3, color_intensity // 4)
        pygame.draw.line(screen, floor_color, (0, WINDOW_HEIGHT // 2 + i), (WINDOW_WIDTH, WINDOW_HEIGHT // 2 + i))
    
    # Calcular el ángulo inicial
    start_angle = player.angle - HALF_FOV
    
    # Lanzar rayos
    for i in range(NUM_RAYS):
        # Calcular el ángulo del rayo actual
        ray_angle = start_angle + (i * FOV / NUM_RAYS)
        
        # Lanzar el rayo
        distance, wall_x, wall_y, wall_type = cast_ray(player.x, player.y, ray_angle)
        
        if distance != float('inf') and wall_type != 0:
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
            
            # Obtener color base de la pared según su tipo
            base_color = WALL_COLORS.get(wall_type, (128, 128, 128))
            
            # Calcular sombreado basado en la distancia
            shade_factor = max(0.2, 1.0 - (distance / (TILE_SIZE * 8)))
            wall_color = (
                int(base_color[0] * shade_factor),
                int(base_color[1] * shade_factor),
                int(base_color[2] * shade_factor)
            )
            
            # Dibujar la columna de la pared
            x = i * 2  # Cada rayo dibuja 2 píxeles de ancho
            pygame.draw.rect(screen, wall_color, (x, wall_top, 2, wall_height))

def draw_minimap(screen, player):
    """Dibuja un minimapa mejorado en la esquina superior izquierda"""
    minimap_size = 200
    minimap_scale = minimap_size / (MAP_WIDTH * TILE_SIZE)
    
    # Fondo del minimapa con borde
    pygame.draw.rect(screen, BLACK, (8, 8, minimap_size + 4, minimap_size + 4))
    pygame.draw.rect(screen, WHITE, (10, 10, minimap_size, minimap_size))
    
    # Dibujar el mapa
    tile_width = minimap_size // MAP_WIDTH
    tile_height = minimap_size // MAP_HEIGHT
    
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall_type = WORLD_MAP[y][x]
            
            if wall_type == 0:
                color = BLACK  # Espacio vacío
            elif wall_type == 1:
                color = GRAY   # Pared básica
            elif wall_type == 2:
                color = BROWN  # Pared especial
            else:
                color = WHITE
            
            rect_x = 10 + x * tile_width
            rect_y = 10 + y * tile_height
            pygame.draw.rect(screen, color, (rect_x, rect_y, tile_width, tile_height))
    
    # Dibujar al jugador
    player_x = 10 + player.x * minimap_scale
    player_y = 10 + player.y * minimap_scale
    
    # Círculo del jugador con borde
    pygame.draw.circle(screen, BLACK, (int(player_x), int(player_y)), 5)
    pygame.draw.circle(screen, RED, (int(player_x), int(player_y)), 3)
    
    # Dibujar dirección del jugador
    end_x = player_x + math.cos(math.radians(player.angle)) * 15
    end_y = player_y + math.sin(math.radians(player.angle)) * 15
    pygame.draw.line(screen, RED, (player_x, player_y), (end_x, end_y), 3)

def draw_ui(screen, player):
    """Dibuja la interfaz de usuario (stamina, estado, etc.)"""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    
    # Barra de stamina
    stamina_width = 200
    stamina_height = 20
    stamina_x = WINDOW_WIDTH - stamina_width - 20
    stamina_y = WINDOW_HEIGHT - 40
    
    # Fondo de la barra de stamina
    pygame.draw.rect(screen, BLACK, (stamina_x - 2, stamina_y - 2, stamina_width + 4, stamina_height + 4))
    pygame.draw.rect(screen, DARK_GRAY, (stamina_x, stamina_y, stamina_width, stamina_height))
    
    # Barra de stamina actual
    current_stamina_width = int((player.stamina / player.max_stamina) * stamina_width)
    stamina_color = GREEN if player.stamina > 30 else (YELLOW if player.stamina > 10 else RED)
    pygame.draw.rect(screen, stamina_color, (stamina_x, stamina_y, current_stamina_width, stamina_height))
    
    # Texto de stamina
    stamina_text = small_font.render(f"Stamina: {int(player.stamina)}/{player.max_stamina}", True, WHITE)
    screen.blit(stamina_text, (stamina_x, stamina_y - 20))
    
    # Indicador de velocidad
    speed_text = "CORRIENDO" if player.is_running else "CAMINANDO"
    speed_color = YELLOW if player.is_running else WHITE
    speed_surface = font.render(speed_text, True, speed_color)
    screen.blit(speed_surface, (stamina_x, stamina_y + 25))
    
    # Mostrar controles
    controls_text = [
        "Controles:",
        "W/↑ - Avanzar",
        "S/↓ - Retroceder", 
        "A/← - Girar izquierda",
        "D/→ - Girar derecha",
        "Q - Moverse izquierda",
        "E - Moverse derecha",
        "SHIFT - Correr",
        "ESC - Salir"
    ]
    
    for i, text in enumerate(controls_text):
        color = WHITE if i == 0 else LIGHT_GRAY
        text_surface = small_font.render(text, True, color)
        screen.blit(text_surface, (20, WINDOW_HEIGHT - 200 + i * 20))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Juego 3D Mejorado - Exploración")
    clock = pygame.time.Clock()
    
    # Crear jugador (posición inicial)
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
        draw_ui(screen, player)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()