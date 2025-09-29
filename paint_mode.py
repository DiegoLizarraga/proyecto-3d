import pygame
import math

from settings import *

class PaintTool:
    def __init__(self):
        self.tool = 'pencil'  # Opciones: pencil, eraser, line, rect, circle
        self.color = SPRAY_COLORS[0]
        self.size = 5
        self.start_pos = None

def enter_paint_mode(screen, mx, my):
    key = (mx, my)
    if key not in graffiti_walls:
        surf = pygame.Surface((GRAFFITI_SIZE, GRAFFITI_SIZE), pygame.SRCALPHA)
        graffiti_walls[key] = surf
    canvas = graffiti_walls[key]

    tool = PaintTool()
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    running = True
    while running:
        temp_canvas = canvas.copy()  # Para previews
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Herramientas
                elif event.key == pygame.K_p:
                    tool.tool = 'pencil'
                elif event.key == pygame.K_e:
                    tool.tool = 'eraser'
                elif event.key == pygame.K_l:
                    tool.tool = 'line'
                elif event.key == pygame.K_r:
                    tool.tool = 'rect'
                elif event.key == pygame.K_c:
                    tool.tool = 'circle'
                # Colores
                for i in range(len(SPRAY_COLORS)):
                    if event.key == pygame.K_1 + i:
                        tool.color = SPRAY_COLORS[i]
                # Tamaño
                if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    tool.size = min(50, tool.size + 1)
                if event.key == pygame.K_MINUS:
                    tool.size = max(1, tool.size - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                tool.start_pos = event.pos
                if tool.tool in ('pencil', 'eraser'):
                    draw_on_canvas(canvas, tool, tool.start_pos, tool.start_pos)
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    pos = event.pos
                    if tool.tool in ('pencil', 'eraser'):
                        draw_on_canvas(canvas, tool, tool.start_pos, pos)
                    elif tool.tool in ('line', 'rect', 'circle'):
                        draw_shape(temp_canvas, tool, tool.start_pos, pos, preview=True)
                    tool.start_pos = pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if tool.tool in ('line', 'rect', 'circle'):
                    draw_shape(canvas, tool, tool.start_pos, event.pos, preview=False)
                tool.start_pos = None

        # Renderizar canvas escalado
        scaled = pygame.transform.scale(temp_canvas if tool.start_pos and tool.tool in ('line', 'rect', 'circle') else canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(scaled, (0, 0))

        # UI de paint
        draw_paint_ui(screen, tool)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.mouse.set_visible(False)

def draw_on_canvas(canvas, tool, start, end):
    color = tool.color if tool.tool == 'pencil' else (0, 0, 0, 0)
    cx1 = int(start[0] * GRAFFITI_SIZE / WINDOW_WIDTH)
    cy1 = int(start[1] * GRAFFITI_SIZE / WINDOW_HEIGHT)
    cx2 = int(end[0] * GRAFFITI_SIZE / WINDOW_WIDTH)
    cy2 = int(end[1] * GRAFFITI_SIZE / WINDOW_HEIGHT)
    pygame.draw.line(canvas, color, (cx1, cy1), (cx2, cy2), tool.size)

def draw_shape(canvas, tool, start, end, preview=False):
    color = tool.color
    width = tool.size
    cx1 = int(start[0] * GRAFFITI_SIZE / WINDOW_WIDTH)
    cy1 = int(start[1] * GRAFFITI_SIZE / WINDOW_HEIGHT)
    cx2 = int(end[0] * GRAFFITI_SIZE / WINDOW_WIDTH)
    cy2 = int(end[1] * GRAFFITI_SIZE / WINDOW_HEIGHT)
    if tool.tool == 'line':
        pygame.draw.line(canvas, color, (cx1, cy1), (cx2, cy2), width)
    elif tool.tool == 'rect':
        rect = pygame.Rect(min(cx1, cx2), min(cy1, cy2), abs(cx1 - cx2), abs(cy1 - cy2))
        pygame.draw.rect(canvas, color, rect, width)
    elif tool.tool == 'circle':
        radius = int(math.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2))
        pygame.draw.circle(canvas, color, (cx1, cy1), radius, width)

def draw_paint_ui(screen, tool):
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    # Panel
    panel_x = WINDOW_WIDTH - 200
    panel_y = 10
    pygame.draw.rect(screen, (40, 40, 40, 180), (panel_x, panel_y, 190, 120))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, 190, 120), 2)
    # Info
    texts = [
        f"Herramienta: {tool.tool}",
        f"Tamaño: {tool.size}",
        "Color:"
    ]
    for i, t in enumerate(texts):
        surf = small_font.render(t, True, WHITE)
        screen.blit(surf, (panel_x + 10, panel_y + 10 + i * 20))
    # Color preview
    pygame.draw.rect(screen, tool.color, (panel_x + 70, panel_y + 50, 30, 20))
    # Instrucciones
    instr = "P:pencil E:eraser L:line R:rect C:circle 1-8:color +/-:size ESC:salir"
    surf = small_font.render(instr, True, WHITE)
    screen.blit(surf, (20, WINDOW_HEIGHT - 30))