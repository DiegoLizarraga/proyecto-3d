import math

from settings import *
from world import WORLD_MAP, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_running = False
        self.stamina = STAMINA_MAX
        self.spray_range = SPRAY_RANGE

    def update(self, keys):
        # Correr
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if running and self.stamina > 0:
            self.is_running = True
            self.stamina -= STAMINA_DRAIN
        else:
            self.is_running = False
            if self.stamina < STAMINA_MAX:
                self.stamina += STAMINA_REGEN
        self.stamina = max(0, min(STAMINA_MAX, self.stamina))

        speed = RUN_SPEED if self.is_running else PLAYER_SPEED

        # Rotación
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= TURN_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += TURN_SPEED
        self.angle %= 360

        # Movimiento
        dx = 0
        dy = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dx += math.cos(math.radians(self.angle)) * speed
            dy += math.sin(math.radians(self.angle)) * speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx -= math.cos(math.radians(self.angle)) * speed
            dy -= math.sin(math.radians(self.angle)) * speed
        if keys[pygame.K_q]:
            dx += math.cos(math.radians(self.angle - 90)) * speed
            dy += math.sin(math.radians(self.angle - 90)) * speed
        if keys[pygame.K_e]:
            dx += math.cos(math.radians(self.angle + 90)) * speed
            dy += math.sin(math.radians(self.angle + 90)) * speed

        # Colisiones
        new_x = self.x + dx
        new_y = self.y + dy
        map_x = int(new_x // TILE_SIZE)
        map_y = int(new_y // TILE_SIZE)
        if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
            if WORLD_MAP[int(self.y // TILE_SIZE)][map_x] == 0:
                self.x = new_x
            if WORLD_MAP[map_y][int(self.x // TILE_SIZE)] == 0:
                self.y = new_y