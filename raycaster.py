import math

from settings import *
from world import WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, WALL_TEXTURES, graffiti_walls

def cast_ray(px, py, angle):
    angle_rad = math.radians(angle)
    dir_x = math.cos(angle_rad)
    dir_y = math.sin(angle_rad)
    map_x = int(px // TILE_SIZE)
    map_y = int(py // TILE_SIZE)
    delta_x = 1e30 if dir_x == 0 else abs(1 / dir_x)
    delta_y = 1e30 if dir_y == 0 else abs(1 / dir_y)

    if dir_x < 0:
        step_x = -1
        side_x = ((px / TILE_SIZE) - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1 - (px / TILE_SIZE)) * delta_x

    if dir_y < 0:
        step_y = -1
        side_y = ((py / TILE_SIZE) - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1 - (py / TILE_SIZE)) * delta_y

    side = 0
    while True:
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1

        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            return float('inf'), 0, 0, 0, 0, 0

        wall_type = WORLD_MAP[map_y][map_x]
        if wall_type > 0:
            break

    if side == 0:
        dist = (map_x - px / TILE_SIZE + (1 - step_x) / 2) / dir_x
    else:
        dist = (map_y - py / TILE_SIZE + (1 - step_y) / 2) / dir_y

    if side == 0:
        hit_x = py + dist * dir_y
        wall_hit = (hit_x % TILE_SIZE) / TILE_SIZE
        if step_x < 0:
            wall_hit = 1 - wall_hit
    else:
        hit_x = px + dist * dir_x
        wall_hit = (hit_x % TILE_SIZE) / TILE_SIZE
        if step_y < 0:
            wall_hit = 1 - wall_hit

    return dist, map_x, map_y, wall_type, wall_hit, side

def render_3d(screen, player):
    # Cielo gradiente mejorado
    for y in range(WINDOW_HEIGHT // 2 + 1):
        c = int(100 + y * 155 / (WINDOW_HEIGHT // 2))
        pygame.draw.line(screen, (c // 2, c // 2, c), (0, y), (WINDOW_WIDTH, y))

    # Suelo gradiente
    for y in range(WINDOW_HEIGHT // 2):
        c = int(80 - y * 50 / (WINDOW_HEIGHT // 2))
        pygame.draw.line(screen, (c, c, c), (0, WINDOW_HEIGHT // 2 + y), (WINDOW_WIDTH, WINDOW_HEIGHT // 2 + y))

    start_angle = player.angle - HALF_FOV
    for i in range(NUM_RAYS):
        ray_angle = start_angle + (i * FOV / NUM_RAYS)
        dist, mx, my, wtype, hit, side = cast_ray(player.x, player.y, ray_angle)
        if dist == float('inf'):
            continue
        corrected_dist = dist * math.cos(math.radians(ray_angle - player.angle))
        wall_height = (TILE_SIZE * WINDOW_HEIGHT) / corrected_dist if corrected_dist > 0 else WINDOW_HEIGHT
        wall_height = min(wall_height, WINDOW_HEIGHT)
        wall_top = (WINDOW_HEIGHT - wall_height) // 2
        wall_bottom = wall_top + wall_height
        shade = max(0.3, 1 - dist / (TILE_SIZE * 8))
        if side == 1:
            shade *= 0.8  # Paredes laterales más oscuras para profundidad

        tex = WALL_TEXTURES.get(wtype)
        tex_size = tex.get_width() if tex else TILE_SIZE
        tex_x = int(hit * tex_size)

        graf_key = (mx, my)
        graf = graffiti_walls.get(graf_key)
        graf_size = GRAFFITI_SIZE if graf else 0

        for h in range(int(wall_height)):
            frac = h / wall_height
            tex_y = int(frac * tex_size)
            color = tex.get_at((tex_x, tex_y))
            color = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))

            if graf:
                g_x = int(hit * graf_size)
                g_y = int(frac * graf_size)
                g_color = graf.get_at((g_x, g_y))
                if g_color[3] > 0:  # Alpha
                    # Blend simple: replace if opaque
                    color = g_color[:3]

            screen_y = int(wall_top + h)
            pygame.draw.rect(screen, color, (i, screen_y, 1, 1))