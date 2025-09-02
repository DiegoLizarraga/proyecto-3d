import pygame
import math
import sys

# Inicializar Pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colores para el simulador de graffiti
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

# Configuración del jugador
PLAYER_SPEED = 2.5  # Velocidad de caminar
RUN_SPEED = 4.5     # Velocidad de correr
TURN_SPEED = 3
FOV = 60  # Campo de visión
HALF_FOV = FOV / 2
NUM_RAYS = WINDOW_WIDTH // 2  # Número de rayos para el raycasting

# Mapa del barrio (1 = casa/edificio, 2 = pared alta, 0 = calle/espacio vacío)
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
#libre para modificarse

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)
TILE_SIZE = 64

# Sistema de graffiti - almacena qué paredes han sido rayadas
# Cada entrada es: (map_x, map_y, wall_type, graffiti_data)
graffiti_walls = {}

# Colores de spray disponibles
SPRAY_COLORS = [RED, BLUE, GREEN, YELLOW, PINK, ORANGE, PURPLE, CYAN]
current_spray_color = 0  # Índice del color actual

# Diccionario de colores base para diferentes tipos de paredes
WALL_COLORS = {
    1: LIGHT_GRAY,    # Casas - gris claro
    2: WHITE,         # Paredes altas - blanco
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
        self.spray_range = TILE_SIZE * 1.2  # Rango para rayar paredes
    
    def update(self, keys):
        global current_spray_color
        
        # Cambiar color de spray con las teclas numéricas
        for i in range(len(SPRAY_COLORS)):
            if keys[pygame.K_1 + i]:
                current_spray_color = i
        
        # Rayar pared con Z
        if keys[pygame.K_z]:
            self.spray_wall()
        
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
    
    def spray_wall(self):
        """Rayar la pared más cercana en la dirección que mira el jugador"""
        # Lanzar un rayo en la dirección que mira el jugador
        distance, wall_x, wall_y, wall_type = cast_ray(self.x, self.y, self.angle)
        
        # Solo rayar si la pared está al alcance
        if distance <= self.spray_range and wall_type != 0:
            wall_key = (wall_x, wall_y)
            
            if wall_key not in graffiti_walls:
                graffiti_walls[wall_key] = []
            
            # Agregar un "graffiti" (punto de color) en esta pared
            # Simular diferentes patrones de graffiti
            import random
            graffiti_pattern = {
                'color': SPRAY_COLORS[current_spray_color],
                'pattern': random.choice(['dot', 'line', 'splash'])
            }
            
            graffiti_walls[wall_key].append(graffiti_pattern)
            
            # Limitar el número de graffitis por pared para rendimiento
            if len(graffiti_walls[wall_key]) > 20:
                graffiti_walls[wall_key] = graffiti_walls[wall_key][-20:]

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
    """Renderiza la vista 3D usando raycasting con efectos de graffiti"""
    
    # Limpiar pantalla
    screen.fill(BLACK)
    
    # Dibujar cielo (mitad superior) - tonos grises
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(200 + (i * 55) / (WINDOW_HEIGHT // 2))
        sky_color = (color_intensity, color_intensity, color_intensity)
        pygame.draw.line(screen, sky_color, (0, i), (WINDOW_WIDTH, i))
    
    # Dibujar suelo (mitad inferior) - asfalto gris oscuro
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(80 - (i * 20) / (WINDOW_HEIGHT // 2))
        floor_color = (color_intensity, color_intensity, color_intensity)
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
            base_color = WALL_COLORS.get(wall_type, GRAY)
            
            # Calcular sombreado basado en la distancia
            shade_factor = max(0.3, 1.0 - (distance / (TILE_SIZE * 6)))
            wall_color = (
                int(base_color[0] * shade_factor),
                int(base_color[1] * shade_factor),
                int(base_color[2] * shade_factor)
            )
            
            # Dibujar la columna de la pared base
            x = i * 2  # Cada rayo dibuja 2 píxeles de ancho
            pygame.draw.rect(screen, wall_color, (x, wall_top, 2, wall_height))
            
            # Dibujar graffiti si existe en esta pared
            wall_key = (wall_x, wall_y)
            if wall_key in graffiti_walls:
                draw_graffiti_on_wall(screen, x, wall_top, wall_height, graffiti_walls[wall_key], corrected_distance)

def draw_graffiti_on_wall(screen, x, wall_top, wall_height, graffiti_list, distance):
    """Dibuja graffiti en una columna de pared"""
    if distance > TILE_SIZE * 4:  # No dibujar graffiti muy lejano
        return
    
    for graffiti in graffiti_list:
        import random
        
        # Posición aleatoria en la pared para el graffiti
        graffiti_y = wall_top + random.randint(int(wall_height * 0.2), int(wall_height * 0.8))
        
        if graffiti['pattern'] == 'dot':
            # Punto de graffiti
            pygame.draw.rect(screen, graffiti['color'], (x, graffiti_y, 2, 3))
        elif graffiti['pattern'] == 'line':
            # Línea de graffiti
            pygame.draw.rect(screen, graffiti['color'], (x, graffiti_y, 2, 8))
        elif graffiti['pattern'] == 'splash':
            # Salpicadura de graffiti
            pygame.draw.rect(screen, graffiti['color'], (x, graffiti_y, 2, 2))
            pygame.draw.rect(screen, graffiti['color'], (x, graffiti_y + 3, 2, 1))

def draw_minimap(screen, player):
    """Dibuja un minimapa del barrio"""
    minimap_size = 180
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
                color = DARK_GRAY  # Calles
            elif wall_type == 1:
                color = LIGHT_GRAY   # Casas
            elif wall_type == 2:
                color = WHITE  # Paredes altas
            else:
                color = GRAY
            
            rect_x = 10 + x * tile_width
            rect_y = 10 + y * tile_height
            pygame.draw.rect(screen, color, (rect_x, rect_y, tile_width, tile_height))
            
            # Marcar paredes con graffiti
            wall_key = (x, y)
            if wall_key in graffiti_walls:
                # Punto pequeño para indicar graffiti
                center_x = rect_x + tile_width // 2
                center_y = rect_y + tile_height // 2
                pygame.draw.circle(screen, RED, (center_x, center_y), 1)
    
    # Dibujar al jugador
    player_x = 10 + player.x * minimap_scale
    player_y = 10 + player.y * minimap_scale
    
    # Círculo del jugador
    pygame.draw.circle(screen, BLACK, (int(player_x), int(player_y)), 4)
    pygame.draw.circle(screen, BLUE, (int(player_x), int(player_y)), 2)
    
    # Dibujar dirección del jugador
    end_x = player_x + math.cos(math.radians(player.angle)) * 12
    end_y = player_y + math.sin(math.radians(player.angle)) * 12
    pygame.draw.line(screen, BLUE, (player_x, player_y), (end_x, end_y), 2)

def draw_ui(screen, player):
    """Dibuja la interfaz de usuario del simulador de graffiti"""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Barra de stamina - MOVIDA A LA IZQUIERDA
    stamina_width = 150
    stamina_height = 15
    stamina_x = 20  # Ahora en la izquierda
    stamina_y = WINDOW_HEIGHT - 60
    
    # Fondo de la barra de stamina
    pygame.draw.rect(screen, BLACK, (stamina_x - 2, stamina_y - 2, stamina_width + 4, stamina_height + 4))
    pygame.draw.rect(screen, DARK_GRAY, (stamina_x, stamina_y, stamina_width, stamina_height))
    
    # Barra de stamina actual
    current_stamina_width = int((player.stamina / player.max_stamina) * stamina_width)
    stamina_color = GREEN if player.stamina > 30 else (YELLOW if player.stamina > 10 else RED)
    pygame.draw.rect(screen, stamina_color, (stamina_x, stamina_y, current_stamina_width, stamina_height))
    
    # Texto de stamina
    stamina_text = small_font.render(f"Stamina: {int(player.stamina)}", True, WHITE)
    screen.blit(stamina_text, (stamina_x, stamina_y - 18))
    
    # Mostrar color de spray actual - mantener arriba a la derecha
    spray_preview_size = 30
    spray_x = WINDOW_WIDTH - 60
    spray_y = 20
    
    pygame.draw.rect(screen, BLACK, (spray_x - 2, spray_y - 2, spray_preview_size + 4, spray_preview_size + 4))
    pygame.draw.rect(screen, SPRAY_COLORS[current_spray_color], (spray_x, spray_y, spray_preview_size, spray_preview_size))
    
    # Texto del color actual
    color_text = small_font.render(f"Color: {current_spray_color + 1}", True, WHITE)
    screen.blit(color_text, (spray_x - 50, spray_y + 35))
    
    # Controles - MOVIDOS ABAJO A LA DERECHA
    controls_text = [
        "=== CONTROLES ===",
        "Movimiento:",
        "W/↑ - Avanzar",
        "S/↓ - Retroceder", 
        "A/← - Girar izquierda",
        "D/→ - Girar derecha",
        "Q/E - Moverse lateral",
        "SHIFT - Correr",
        "",
        "Graffiti:",
        "Z - Rayar pared",
        "1-8 - Cambiar color",
        "",
        "ESC - Salir"
    ]
    
    # Posicionar controles en la esquina inferior derecha
    controls_start_y = WINDOW_HEIGHT - (len([t for t in controls_text if t != ""]) * 16) - 20
    controls_x = WINDOW_WIDTH - 180
    
    line_count = 0
    for text in controls_text:
        if text == "":
            continue
            
        if text == "=== CONTROLES ===":
            color = YELLOW
            text_surface = small_font.render(text, True, color)
        elif text == "Movimiento:" or text == "Graffiti:":
            color = WHITE
            text_surface = small_font.render(text, True, color)
        else:
            color = LIGHT_GRAY
            text_surface = small_font.render(text, True, color)
        
        screen.blit(text_surface, (controls_x, controls_start_y + line_count * 16))
        line_count += 1
    
    # Contador de graffitis - mantener abajo a la izquierda
    total_graffitis = sum(len(graffiti_list) for graffiti_list in graffiti_walls.values())
    graffiti_counter = font.render(f"Graffitis: {total_graffitis}", True, YELLOW)
    screen.blit(graffiti_counter, (20, WINDOW_HEIGHT - 40))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulador de Graffiti 3D - Barrio")
    clock = pygame.time.Clock()
    
    # Crear jugador (empezar en una calle del barrio)
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