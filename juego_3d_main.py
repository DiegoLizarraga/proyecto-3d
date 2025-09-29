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
PLAYER_SPEED = 2.5
RUN_SPEED = 4.5
TURN_SPEED = 3
FOV = 60
HALF_FOV = FOV / 2
NUM_RAYS = WINDOW_WIDTH // 2

# Mapa del barrio
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
TILE_SIZE = 64

# Sistema de graffiti mejorado - ahora almacena trazos completos
graffiti_walls = {}

# Colores de spray disponibles
SPRAY_COLORS = [RED, BLUE, GREEN, YELLOW, PINK, ORANGE, PURPLE, CYAN]
current_spray_color = 0

# Modos de spray
SPRAY_MODES = ['libre', 'linea', 'circulo', 'rectangulo', 'estrella', 'zigzag']
current_spray_mode = 0

# Tamaños de spray
SPRAY_SIZES = [2, 4, 6, 8, 10]
current_spray_size = 2

# Diccionario de colores base para diferentes tipos de paredes
WALL_COLORS = {
    1: LIGHT_GRAY,
    2: WHITE,
}

class GraffitiStroke:
    """Representa un trazo de graffiti completo"""
    def __init__(self, color, size, mode):
        self.color = color
        self.size = size
        self.mode = mode
        self.points = []  # Lista de puntos (x, y) en coordenadas de pared
        self.completed = False
    
    def add_point(self, x, y):
        """Agrega un punto al trazo"""
        self.points.append((x, y))
    
    def complete(self):
        """Marca el trazo como completado"""
        self.completed = True

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
        self.spray_range = TILE_SIZE * 1.8
        
        # Estado de dibujo
        self.is_spraying = False
        self.current_stroke = None
        self.target_wall = None
        self.last_spray_pos = None
    
    def update(self, keys):
        global current_spray_color, current_spray_mode, current_spray_size
        
        # Cambiar color de spray con las teclas numéricas
        for i in range(min(8, len(SPRAY_COLORS))):
            if keys[pygame.K_1 + i]:
                current_spray_color = i
        
        # Cambiar modo de spray con M
        if keys[pygame.K_m]:
            current_spray_mode = (current_spray_mode + 1) % len(SPRAY_MODES)
            pygame.time.wait(200)  # Evitar cambios múltiples
        
        # Cambiar tamaño con + y -
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            current_spray_size = min(len(SPRAY_SIZES) - 1, current_spray_size + 1)
            pygame.time.wait(150)
        if keys[pygame.K_MINUS]:
            current_spray_size = max(0, current_spray_size - 1)
            pygame.time.wait(150)
        
        # Verificar si el jugador quiere correr
        running_keys = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if running_keys and self.stamina > 0:
            self.is_running = True
            self.stamina -= self.stamina_drain_rate
        else:
            self.is_running = False
            if self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen_rate
        
        self.stamina = max(0, min(self.max_stamina, self.stamina))
        
        current_speed = RUN_SPEED if self.is_running else PLAYER_SPEED
        
        # Rotación
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= TURN_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += TURN_SPEED
        
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
        
        if keys[pygame.K_q]:
            dx += math.cos(math.radians(self.angle - 90)) * current_speed
            dy += math.sin(math.radians(self.angle - 90)) * current_speed
        
        if keys[pygame.K_e]:
            dx += math.cos(math.radians(self.angle + 90)) * current_speed
            dy += math.sin(math.radians(self.angle + 90)) * current_speed
        
        # Verificar colisiones
        new_x = self.x + dx
        new_y = self.y + dy
        
        map_x = int(new_x // TILE_SIZE)
        map_y = int(new_y // TILE_SIZE)
        
        if (0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT):
            if WORLD_MAP[int(self.y // TILE_SIZE)][map_x] == 0:
                self.x = new_x
            
            if WORLD_MAP[map_y][int(self.x // TILE_SIZE)] == 0:
                self.y = new_y
        
        # Sistema de spray mejorado - mantener Z presionado para dibujar
        if keys[pygame.K_z]:
            if not self.is_spraying:
                self.start_spray()
            else:
                self.continue_spray()
        else:
            if self.is_spraying:
                self.end_spray()
    
    def start_spray(self):
        """Inicia un nuevo trazo de graffiti"""
        distance, wall_x, wall_y, wall_type = cast_ray(self.x, self.y, self.angle)
        
        if distance <= self.spray_range and wall_type != 0:
            self.is_spraying = True
            self.target_wall = (wall_x, wall_y)
            
            # Crear nuevo trazo
            self.current_stroke = GraffitiStroke(
                SPRAY_COLORS[current_spray_color],
                SPRAY_SIZES[current_spray_size],
                SPRAY_MODES[current_spray_mode]
            )
            
            # Calcular posición en la pared (coordenadas normalizadas 0-1)
            wall_pos = self.calculate_wall_position(distance)
            self.current_stroke.add_point(wall_pos[0], wall_pos[1])
            self.last_spray_pos = wall_pos
    
    def continue_spray(self):
        """Continúa el trazo actual"""
        if not self.is_spraying or not self.current_stroke:
            return
        
        distance, wall_x, wall_y, wall_type = cast_ray(self.x, self.y, self.angle)
        
        # Verificar si seguimos en la misma pared
        if (wall_x, wall_y) == self.target_wall and distance <= self.spray_range:
            wall_pos = self.calculate_wall_position(distance)
            
            # Solo agregar punto si se movió suficiente
            if self.last_spray_pos:
                dx = wall_pos[0] - self.last_spray_pos[0]
                dy = wall_pos[1] - self.last_spray_pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0.01:  # Threshold para evitar puntos muy cercanos
                    self.current_stroke.add_point(wall_pos[0], wall_pos[1])
                    self.last_spray_pos = wall_pos
        else:
            # Cambió de pared, terminar trazo actual
            self.end_spray()
    
    def end_spray(self):
        """Termina el trazo actual"""
        if self.is_spraying and self.current_stroke and len(self.current_stroke.points) > 0:
            self.current_stroke.complete()
            
            # Guardar el trazo en la pared
            wall_key = self.target_wall
            if wall_key not in graffiti_walls:
                graffiti_walls[wall_key] = []
            
            graffiti_walls[wall_key].append(self.current_stroke)
            
            # Limitar número de trazos por pared
            if len(graffiti_walls[wall_key]) > 50:
                graffiti_walls[wall_key] = graffiti_walls[wall_key][-50:]
        
        self.is_spraying = False
        self.current_stroke = None
        self.target_wall = None
        self.last_spray_pos = None
    
    def calculate_wall_position(self, distance):
        """Calcula la posición normalizada (0-1) en la pared donde se está dibujando"""
        # Usar una semilla basada en la posición y ángulo del jugador
        # para dar coordenadas consistentes en la pared
        angle_offset = (self.angle % 360) / 360.0
        distance_factor = min(1.0, distance / self.spray_range)
        
        # Agregar variación basada en el ángulo para distribuir el graffiti
        import random
        random.seed(int(self.x * 100 + self.y * 100 + self.angle))
        
        x = (angle_offset + random.random() * 0.1) % 1.0
        y = 0.3 + distance_factor * 0.4 + random.random() * 0.2
        
        return (x, y)

def cast_ray(start_x, start_y, angle):
    """Lanza un rayo y devuelve la distancia hasta la primera pared y su tipo"""
    angle_rad = math.radians(angle)
    
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    
    step = 1
    
    x = start_x
    y = start_y
    
    while True:
        x += dx * step
        y += dy * step
        
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            break
        
        wall_type = WORLD_MAP[map_y][map_x]
        if wall_type != 0:
            distance = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            return distance, map_x, map_y, wall_type
    
    return float('inf'), 0, 0, 0

def render_3d(screen, player):
    """Renderiza la vista 3D usando raycasting con efectos de graffiti mejorados"""
    
    screen.fill(BLACK)
    
    # Dibujar cielo
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(200 + (i * 55) / (WINDOW_HEIGHT // 2))
        sky_color = (color_intensity, color_intensity, color_intensity)
        pygame.draw.line(screen, sky_color, (0, i), (WINDOW_WIDTH, i))
    
    # Dibujar suelo
    for i in range(WINDOW_HEIGHT // 2):
        color_intensity = int(80 - (i * 20) / (WINDOW_HEIGHT // 2))
        floor_color = (color_intensity, color_intensity, color_intensity)
        pygame.draw.line(screen, floor_color, (0, WINDOW_HEIGHT // 2 + i), (WINDOW_WIDTH, WINDOW_HEIGHT // 2 + i))
    
    start_angle = player.angle - HALF_FOV
    
    for i in range(NUM_RAYS):
        ray_angle = start_angle + (i * FOV / NUM_RAYS)
        
        distance, wall_x, wall_y, wall_type = cast_ray(player.x, player.y, ray_angle)
        
        if distance != float('inf') and wall_type != 0:
            corrected_distance = distance * math.cos(math.radians(ray_angle - player.angle))
            
            if corrected_distance > 0:
                wall_height = (TILE_SIZE * WINDOW_HEIGHT) / corrected_distance
            else:
                wall_height = WINDOW_HEIGHT
            
            wall_height = min(wall_height, WINDOW_HEIGHT)
            
            wall_top = (WINDOW_HEIGHT - wall_height) // 2
            wall_bottom = wall_top + wall_height
            
            base_color = WALL_COLORS.get(wall_type, GRAY)
            
            shade_factor = max(0.3, 1.0 - (distance / (TILE_SIZE * 6)))
            wall_color = (
                int(base_color[0] * shade_factor),
                int(base_color[1] * shade_factor),
                int(base_color[2] * shade_factor)
            )
            
            x = i * 2
            pygame.draw.rect(screen, wall_color, (x, wall_top, 2, wall_height))
            
            # Dibujar graffiti mejorado
            wall_key = (wall_x, wall_y)
            if wall_key in graffiti_walls:
                draw_graffiti_strokes(screen, x, wall_top, wall_height, graffiti_walls[wall_key], corrected_distance, i, NUM_RAYS)

def draw_graffiti_strokes(screen, x, wall_top, wall_height, strokes, distance, ray_index, total_rays):
    """Dibuja trazos de graffiti en una columna de pared"""
    if distance > TILE_SIZE * 5:
        return
    
    # Calcular posición normalizada en la pared (0-1)
    wall_u = ray_index / total_rays
    
    for stroke in strokes:
        if not stroke.completed or len(stroke.points) < 1:
            continue
        
        # Aplicar sombreado por distancia
        shade = max(0.4, 1.0 - (distance / (TILE_SIZE * 5)))
        color = (
            int(stroke.color[0] * shade),
            int(stroke.color[1] * shade),
            int(stroke.color[2] * shade)
        )
        
        # Dibujar según el modo
        if stroke.mode == 'libre':
            # Dibujar trazo libre - conectar puntos cercanos
            for i, point in enumerate(stroke.points):
                px, py = point
                
                # Verificar si este punto está cerca de la columna actual
                if abs(px - wall_u) < 0.02:
                    # Calcular posición Y en la pantalla
                    screen_y = wall_top + int(py * wall_height)
                    
                    # Dibujar punto con el tamaño del spray
                    size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                    pygame.draw.rect(screen, color, (x, screen_y - size//2, 2, size))
        
        elif stroke.mode == 'linea':
            # Dibujar línea recta entre primer y último punto
            if len(stroke.points) >= 2:
                p1 = stroke.points[0]
                p2 = stroke.points[-1]
                
                # Interpolar para ver si pasa por esta columna
                if min(p1[0], p2[0]) <= wall_u <= max(p1[0], p2[0]):
                    # Interpolación lineal
                    t = (wall_u - p1[0]) / (p2[0] - p1[0]) if p2[0] != p1[0] else 0
                    py = p1[1] + t * (p2[1] - p1[1])
                    
                    screen_y = wall_top + int(py * wall_height)
                    size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                    pygame.draw.rect(screen, color, (x, screen_y - size//2, 2, size * 2))
        
        elif stroke.mode == 'circulo':
            # Dibujar círculo
            if len(stroke.points) >= 2:
                center = stroke.points[0]
                edge = stroke.points[-1]
                
                cx, cy = center
                radius = math.sqrt((edge[0] - cx)**2 + (edge[1] - cy)**2)
                
                # Verificar si esta columna intersecta el círculo
                dist_to_center = abs(wall_u - cx)
                
                if dist_to_center <= radius:
                    # Calcular puntos de intersección
                    y_offset = math.sqrt(radius**2 - dist_to_center**2)
                    
                    y1 = cy - y_offset
                    y2 = cy + y_offset
                    
                    screen_y1 = wall_top + int(y1 * wall_height)
                    screen_y2 = wall_top + int(y2 * wall_height)
                    
                    size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                    
                    # Dibujar los dos puntos del círculo
                    pygame.draw.rect(screen, color, (x, screen_y1 - size//2, 2, size))
                    pygame.draw.rect(screen, color, (x, screen_y2 - size//2, 2, size))
        
        elif stroke.mode == 'rectangulo':
            # Dibujar rectángulo
            if len(stroke.points) >= 2:
                p1 = stroke.points[0]
                p2 = stroke.points[-1]
                
                x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
                
                # Verificar si esta columna está dentro del rectángulo
                if x1 <= wall_u <= x2:
                    size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                    
                    # Dibujar bordes superior e inferior
                    screen_y1 = wall_top + int(y1 * wall_height)
                    screen_y2 = wall_top + int(y2 * wall_height)
                    
                    pygame.draw.rect(screen, color, (x, screen_y1 - size//2, 2, size))
                    pygame.draw.rect(screen, color, (x, screen_y2 - size//2, 2, size))
                    
                    # Dibujar lados verticales si está en los bordes
                    if abs(wall_u - x1) < 0.01 or abs(wall_u - x2) < 0.01:
                        pygame.draw.line(screen, color, (x, screen_y1), (x, screen_y2), 2)
        
        elif stroke.mode == 'estrella':
            # Dibujar estrella de 5 puntas
            if len(stroke.points) >= 2:
                center = stroke.points[0]
                edge = stroke.points[-1]
                
                cx, cy = center
                radius = math.sqrt((edge[0] - cx)**2 + (edge[1] - cy)**2)
                
                # Generar puntos de la estrella
                star_points = []
                for i in range(10):
                    angle = i * 36 * math.pi / 180 - math.pi / 2
                    r = radius if i % 2 == 0 else radius * 0.4
                    px = cx + math.cos(angle) * r
                    py = cy + math.sin(angle) * r
                    star_points.append((px, py))
                
                # Dibujar líneas de la estrella que cruzan esta columna
                size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                
                for i in range(len(star_points)):
                    p1 = star_points[i]
                    p2 = star_points[(i + 1) % len(star_points)]
                    
                    if min(p1[0], p2[0]) <= wall_u <= max(p1[0], p2[0]):
                        t = (wall_u - p1[0]) / (p2[0] - p1[0]) if p2[0] != p1[0] else 0
                        py = p1[1] + t * (p2[1] - p1[1])
                        
                        screen_y = wall_top + int(py * wall_height)
                        pygame.draw.rect(screen, color, (x, screen_y - size//2, 2, size))
        
        elif stroke.mode == 'zigzag':
            # Dibujar zigzag
            if len(stroke.points) >= 2:
                # Crear puntos de zigzag entre inicio y fin
                p1 = stroke.points[0]
                p2 = stroke.points[-1]
                
                zigzag_points = []
                steps = 8
                for i in range(steps + 1):
                    t = i / steps
                    px = p1[0] + t * (p2[0] - p1[0])
                    
                    # Alternar arriba y abajo
                    offset = 0.1 if i % 2 == 0 else -0.1
                    py = p1[1] + t * (p2[1] - p1[1]) + offset
                    
                    zigzag_points.append((px, py))
                
                # Dibujar zigzag
                size = max(1, int(stroke.size * (1.0 - distance / (TILE_SIZE * 5))))
                
                for i in range(len(zigzag_points) - 1):
                    pt1 = zigzag_points[i]
                    pt2 = zigzag_points[i + 1]
                    
                    if min(pt1[0], pt2[0]) <= wall_u <= max(pt1[0], pt2[0]):
                        t = (wall_u - pt1[0]) / (pt2[0] - pt1[0]) if pt2[0] != pt1[0] else 0
                        py = pt1[1] + t * (pt2[1] - pt1[1])
                        
                        screen_y = wall_top + int(py * wall_height)
                        pygame.draw.rect(screen, color, (x, screen_y - size//2, 2, size))

def draw_minimap(screen, player):
    """Dibuja un minimapa del barrio"""
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
            
            # Marcar paredes con graffiti
            wall_key = (x, y)
            if wall_key in graffiti_walls:
                center_x = rect_x + tile_width // 2
                center_y = rect_y + tile_height // 2
                pygame.draw.circle(screen, RED, (center_x, center_y), 2)
    
    # Dibujar al jugador
    player_x = 10 + player.x * minimap_scale
    player_y = 10 + player.y * minimap_scale
    
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
    
    # Barra de stamina
    stamina_width = 150
    stamina_height = 15
    stamina_x = 20
    stamina_y = WINDOW_HEIGHT - 60
    
    pygame.draw.rect(screen, BLACK, (stamina_x - 2, stamina_y - 2, stamina_width + 4, stamina_height + 4))
    pygame.draw.rect(screen, DARK_GRAY, (stamina_x, stamina_y, stamina_width, stamina_height))
    
    current_stamina_width = int((player.stamina / player.max_stamina) * stamina_width)
    stamina_color = GREEN if player.stamina > 30 else (YELLOW if player.stamina > 10 else RED)
    pygame.draw.rect(screen, stamina_color, (stamina_x, stamina_y, current_stamina_width, stamina_height))
    
    stamina_text = small_font.render(f"Stamina: {int(player.stamina)}", True, WHITE)
    screen.blit(stamina_text, (stamina_x, stamina_y - 18))
    
    # Panel de herramientas de spray (esquina superior derecha)
    panel_x = WINDOW_WIDTH - 200
    panel_y = 10
    panel_width = 190
    panel_height = 140
    
    # Fondo del panel
    pygame.draw.rect(screen, (40, 40, 40, 200), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)
    
    # Título
    title = small_font.render("=== SPRAY ===", True, YELLOW)
    screen.blit(title, (panel_x + 50, panel_y + 5))
    
    # Preview del color actual
    color_size = 25
    color_x = panel_x + 10
    color_y = panel_y + 30
    
    pygame.draw.rect(screen, BLACK, (color_x - 2, color_y - 2, color_size + 4, color_size + 4))
    pygame.draw.rect(screen, SPRAY_COLORS[current_spray_color], (color_x, color_y, color_size, color_size))
    
    color_text = small_font.render(f"Color: {current_spray_color + 1}", True, WHITE)
    screen.blit(color_text, (color_x + 35, color_y + 5))
    
    # Modo actual
    mode_text = small_font.render(f"Modo: {SPRAY_MODES[current_spray_mode]}", True, WHITE)
    screen.blit(mode_text, (panel_x + 10, panel_y + 65))
    
    # Tamaño actual
    size_text = small_font.render(f"Tamaño: {SPRAY_SIZES[current_spray_size]}", True, WHITE)
    screen.blit(size_text, (panel_x + 10, panel_y + 85))
    
    # Indicador de spray activo
    if player.is_spraying:
        spray_status = small_font.render("SPRAYING!", True, RED)
        screen.blit(spray_status, (panel_x + 55, panel_y + 115))
    
    # Paleta de colores pequeña
    palette_y = panel_y + 105
    for i, color in enumerate(SPRAY_COLORS):
        px = panel_x + 10 + (i * 22)
        pygame.draw.rect(screen, color, (px, palette_y, 18, 10))
        if i == current_spray_color:
            pygame.draw.rect(screen, WHITE, (px - 1, palette_y - 1, 20, 12), 2)
        else:
            pygame.draw.rect(screen, BLACK, (px, palette_y, 18, 10), 1)
    
    # Controles (abajo a la derecha)
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
        "Z (mantener) - Spray",
        "1-8 - Color",
        "M - Cambiar modo",
        "+/- - Tamaño",
        "",
        "ESC - Salir"
    ]
    
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
    
    # Contador de graffitis y trazos
    total_strokes = sum(len(strokes) for strokes in graffiti_walls.values())
    total_walls = len(graffiti_walls)
    graffiti_counter = font.render(f"Trazos: {total_strokes} | Paredes: {total_walls}", True, YELLOW)
    screen.blit(graffiti_counter, (20, WINDOW_HEIGHT - 40))
    
    # Instrucción de borrado
    if total_strokes > 0:
        clear_text = small_font.render("Presiona C para limpiar todo", True, RED)
        screen.blit(clear_text, (20, WINDOW_HEIGHT - 85))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulador de Graffiti 3D Mejorado - Sistema Paint")
    clock = pygame.time.Clock()
    
    # Crear jugador
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
                elif event.key == pygame.K_c:
                    # Limpiar todos los graffitis
                    graffiti_walls.clear()
        
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