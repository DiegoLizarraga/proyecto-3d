import math
import pygame

from settings import *
from world import WORLD_MAP, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class Player3D:
    def __init__(self, x, z, yaw):
        self.x = x
        self.z = z
        self.y = TILE_SIZE * 0.6  # Altura de ojos fija
        self.yaw = yaw  # Solo rotación horizontal
        self.is_running = False
        self.stamina = STAMINA_MAX
        self.spray_range = SPRAY_RANGE
        self.collision_radius = TILE_SIZE * 0.3
        
    def update(self, keys, dt):
        """Actualiza posición y estado del jugador"""
        # Sistema de stamina
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if running and self.stamina > 0:
            self.is_running = True
            self.stamina -= STAMINA_DRAIN
        else:
            self.is_running = False
            if self.stamina < STAMINA_MAX:
                self.stamina += STAMINA_REGEN
        self.stamina = max(0, min(STAMINA_MAX, self.stamina))
        
        # Velocidad
        speed = RUN_SPEED if self.is_running else PLAYER_SPEED
        move_speed = speed * 60 * dt  # Normalizar por framerate
        
        # Calcular dirección
        dx = 0
        dz = 0
        
        # Adelante/atrás
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dx += math.cos(math.radians(self.yaw)) * move_speed
            dz += math.sin(math.radians(self.yaw)) * move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dx -= math.cos(math.radians(self.yaw)) * move_speed
            dz -= math.sin(math.radians(self.yaw)) * move_speed
        
        # Strafe izquierda/derecha
        if keys[pygame.K_a]:
            dx += math.cos(math.radians(self.yaw - 90)) * move_speed
            dz += math.sin(math.radians(self.yaw - 90)) * move_speed
        if keys[pygame.K_d]:
            dx += math.cos(math.radians(self.yaw + 90)) * move_speed
            dz += math.sin(math.radians(self.yaw + 90)) * move_speed
        
        # Rotación con teclas (alternativa al mouse)
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.yaw -= TURN_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_e]:
            self.yaw += TURN_SPEED
        self.yaw %= 360
        
        # Aplicar movimiento con colisión
        self.move_with_collision(dx, dz)
    
    def move_with_collision(self, dx, dz):
        """Mueve al jugador detectando colisiones con paredes"""
        # Intentar movimiento en X
        new_x = self.x + dx
        if self.can_move_to(new_x, self.z):
            self.x = new_x
        
        # Intentar movimiento en Z
        new_z = self.z + dz
        if self.can_move_to(self.x, new_z):
            self.z = new_z
    
    def can_move_to(self, x, z):
        """Verifica si el jugador puede moverse a una posición"""
        # Verificar múltiples puntos alrededor del jugador para colisión circular
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        for angle in angles:
            check_x = x + math.cos(math.radians(angle)) * self.collision_radius
            check_z = z + math.sin(math.radians(angle)) * self.collision_radius
            
            map_x = int(check_x // TILE_SIZE)
            map_z = int(check_z // TILE_SIZE)
            
            # Verificar límites
            if map_x < 0 or map_x >= MAP_WIDTH or map_z < 0 or map_z >= MAP_HEIGHT:
                return False
            
            # Verificar colisión con pared
            if WORLD_MAP[map_z][map_x] > 0:
                return False
        
        return True
    
    def get_wall_in_front(self):
        """Detecta si hay una pared enfrente del jugador dentro del rango de spray"""
        ray_x = self.x
        ray_z = self.z
        dir_x = math.cos(math.radians(self.yaw))
        dir_z = math.sin(math.radians(self.yaw))
        
        # Raycast más preciso
        step = 1.0
        max_steps = int(self.spray_range / step)
        
        prev_map_x = int(ray_x // TILE_SIZE)
        prev_map_z = int(ray_z // TILE_SIZE)
        
        for i in range(1, max_steps):
            ray_x += dir_x * step
            ray_z += dir_z * step
            
            map_x = int(ray_x // TILE_SIZE)
            map_z = int(ray_z // TILE_SIZE)
            
            # Verificar límites
            if map_x < 0 or map_x >= MAP_WIDTH or map_z < 0 or map_z >= MAP_HEIGHT:
                return None
            
            # Detectar cuando golpeamos una pared
            if WORLD_MAP[map_z][map_x] > 0:
                # Determinar qué cara golpeamos basándonos en la dirección
                face = 'N'
                
                # Detectar si cruzamos en X o Z
                if map_x != prev_map_x and map_z == prev_map_z:
                    # Cruzamos en X
                    face = 'W' if map_x > prev_map_x else 'E'
                elif map_z != prev_map_z and map_x == prev_map_x:
                    # Cruzamos en Z
                    face = 'N' if map_z > prev_map_z else 'S'
                else:
                    # Cruce diagonal - usar dirección dominante
                    if abs(dir_x) > abs(dir_z):
                        face = 'W' if dir_x > 0 else 'E'
                    else:
                        face = 'N' if dir_z > 0 else 'S'
                
                print(f"Pared detectada en ({map_x}, {map_z}) cara {face}, distancia: {i}")  # Debug
                return (map_x, map_z, face)
            
            prev_map_x = map_x
            prev_map_z = map_z
        
        print(f"No se detectó pared en rango {self.spray_range}")  # Debug
        return None