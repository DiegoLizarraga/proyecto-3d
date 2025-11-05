import pygame
from pygame.locals import *
from OpenGL.GL import *
import sys
import math

from settings import *
from player3d import Player3D
from engine3d import Renderer3D, Camera
from world import WORLD_MAP, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, graffiti_walls
from paint_mode import enter_paint_mode
from ui3d import UI3D

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Pintura por tiner - Graffiti Edition")
clock = pygame.time.Clock()

# Inicializar motor 3D
renderer = Renderer3D(WINDOW_WIDTH, WINDOW_HEIGHT)
renderer.init_opengl()

# Jugador y cámara
player = Player3D(TILE_SIZE * 1.5, TILE_SIZE * 1.5, 0)
camera = Camera(player.x, TILE_SIZE * 0.6, player.z, player.yaw)  # Altura de ojos

# UI
ui = UI3D(screen)

# Ocultar cursor
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

running = True
z_key_pressed = False  # Para evitar múltiples activaciones

while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time en segundos
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_c:
                graffiti_walls.clear()
                renderer.graffiti_textures.clear()
        elif event.type == pygame.MOUSEMOTION:
            # Movimiento del mouse para rotar cámara
            mouse_dx = event.rel[0]
            player.yaw += mouse_dx * MOUSE_SENSITIVITY
            player.yaw %= 360
    
    keys = pygame.key.get_pressed()
    player.update(keys, dt)
    
    # Actualizar posición de cámara
    camera.x = player.x
    camera.z = player.z
    camera.yaw = player.yaw
    
    # Detectar tecla Z para modo paint
    if keys[pygame.K_z] and not z_key_pressed:
        z_key_pressed = True
        wall_info = player.get_wall_in_front()
        
        if wall_info:
            x, z, face = wall_info
            key = (x, z, face)
            
            print(f"Detectada pared en: {key}")  # Debug
            
            # Deshabilitar grab del mouse antes de entrar a paint mode
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            
            # Entrar en modo paint
            enter_paint_mode(screen, renderer, key)
            
            # Restaurar ventana 3D después de salir del paint mode
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
            pygame.display.set_caption("Videojuego 3D Estilo Half-Life - Graffiti Edition")
            renderer.init_opengl()  # Reinicializar OpenGL
            
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            print("No hay pared cerca")  # Debug
    
    # Resetear flag cuando se suelta la tecla
    if not keys[pygame.K_z]:
        z_key_pressed = False
    
    # Renderizar mundo 3D
    renderer.render_world(camera)
    
    # Cambiar a modo 2D para UI
    ui.begin_2d_rendering()
    ui.draw_ui(player)
    ui.end_2d_rendering()
    
    pygame.display.flip()

# Cleanup
renderer.cleanup()
pygame.quit()
sys.exit()