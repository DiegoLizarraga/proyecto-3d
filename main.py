import pygame
import sys

from settings import *
from player import Player
from world import graffiti_walls
from raycaster import render_3d, cast_ray
from ui import draw_minimap, draw_ui
from paint_mode import enter_paint_mode

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Videojuego 3D de Graffiti Mejorado")
clock = pygame.time.Clock()

player = Player(TILE_SIZE * 1.5, TILE_SIZE * 1.5, 0)
pygame.mouse.set_visible(False)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_c:
                graffiti_walls.clear()

    keys = pygame.key.get_pressed()
    player.update(keys)

    # Entrar en modo paint
    if keys[pygame.K_z]:
        dist, mx, my, _, _, _ = cast_ray(player.x, player.y, player.angle)
        if dist < player.spray_range and dist != float('inf'):
            enter_paint_mode(screen, mx, my)
            pygame.time.wait(200)  # Evitar reentrada inmediata

    # Render
    render_3d(screen, player)
    draw_minimap(screen, player)
    draw_ui(screen, player)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()