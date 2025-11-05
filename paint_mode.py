import pygame
import math
import random

from settings import *
from world import graffiti_walls

class PaintTool:
    def __init__(self):
        self.tool = 'brush'  # brush, spray, eraser, line, rect, circle, fill
        self.color = SPRAY_COLORS[0]
        self.size = 10
        self.start_pos = None
        self.opacity = 255
        
class ColorPalette:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color_size = 30
        self.colors = SPRAY_COLORS
        self.custom_colors = []
        
    def draw(self, screen):
        # Dibujar paleta principal
        for i, color in enumerate(self.colors):
            row = i // 4
            col = i % 4
            rect = pygame.Rect(
                self.x + col * (self.color_size + 5),
                self.y + row * (self.color_size + 5),
                self.color_size,
                self.color_size
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
    
    def get_color_at(self, pos):
        for i, color in enumerate(self.colors):
            row = i // 4
            col = i % 4
            rect = pygame.Rect(
                self.x + col * (self.color_size + 5),
                self.y + row * (self.color_size + 5),
                self.color_size,
                self.color_size
            )
            if rect.collidepoint(pos):
                return color
        return None

def enter_paint_mode(screen, renderer, wall_key):
    """
    Modo de pintura mejorado - Ventana de Paint completa
    """
    # Crear ventana de paint más grande
    paint_width = 1024
    paint_height = 768
    paint_screen = pygame.display.set_mode((paint_width, paint_height))
    pygame.display.set_caption(f"Paint Mode - Pared {wall_key}")
    
    # Crear o cargar canvas
    if wall_key not in graffiti_walls:
        canvas = pygame.Surface((GRAFFITI_SIZE, GRAFFITI_SIZE), pygame.SRCALPHA)
        canvas.fill((240, 240, 240, 255))  # Fondo blanco
        graffiti_walls[wall_key] = canvas
    else:
        canvas = graffiti_walls[wall_key]
    
    # Crear superficie temporal para preview
    temp_canvas = canvas.copy()
    
    tool = PaintTool()
    palette = ColorPalette(20, paint_height - 120)
    
    # Área de canvas
    canvas_display_size = 650
    canvas_x = 20
    canvas_y = 20
    
    clock = pygame.time.Clock()
    running = True
    drawing = False
    last_pos = None
    
    # Historial para deshacer (máximo 20 estados)
    history = [canvas.copy()]
    history_index = 0
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Calcular posición en el canvas real
        canvas_rect = pygame.Rect(canvas_x, canvas_y, canvas_display_size, canvas_display_size)
        in_canvas = canvas_rect.collidepoint(mouse_pos)
        
        if in_canvas:
            # Convertir coordenadas de pantalla a canvas
            rel_x = mouse_pos[0] - canvas_x
            rel_y = mouse_pos[1] - canvas_y
            canvas_pos = (
                int(rel_x * GRAFFITI_SIZE / canvas_display_size),
                int(rel_y * GRAFFITI_SIZE / canvas_display_size)
            )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Herramientas
                elif event.key == pygame.K_b:
                    tool.tool = 'brush'
                elif event.key == pygame.K_s:
                    tool.tool = 'spray'
                elif event.key == pygame.K_e:
                    tool.tool = 'eraser'
                elif event.key == pygame.K_l:
                    tool.tool = 'line'
                elif event.key == pygame.K_r:
                    tool.tool = 'rect'
                elif event.key == pygame.K_c:
                    tool.tool = 'circle'
                elif event.key == pygame.K_f:
                    tool.tool = 'fill'
                
                # Tamaño
                elif event.key == pygame.K_LEFTBRACKET:
                    tool.size = max(1, tool.size - 2)
                elif event.key == pygame.K_RIGHTBRACKET:
                    tool.size = min(50, tool.size + 2)
                
                # Deshacer/Rehacer
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if history_index > 0:
                        history_index -= 1
                        canvas = history[history_index].copy()
                        graffiti_walls[wall_key] = canvas
                elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if history_index < len(history) - 1:
                        history_index += 1
                        canvas = history[history_index].copy()
                        graffiti_walls[wall_key] = canvas
                
                # Limpiar
                elif event.key == pygame.K_x:
                    canvas.fill((240, 240, 240, 255))
                    add_to_history(canvas, history, history_index)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    # Verificar si clickeó en la paleta
                    clicked_color = palette.get_color_at(mouse_pos)
                    if clicked_color:
                        tool.color = clicked_color
                    elif in_canvas:
                        drawing = True
                        tool.start_pos = canvas_pos
                        last_pos = canvas_pos
                        
                        if tool.tool == 'brush':
                            draw_brush(canvas, canvas_pos, tool)
                        elif tool.tool == 'spray':
                            draw_spray(canvas, canvas_pos, tool)
                        elif tool.tool == 'eraser':
                            draw_eraser(canvas, canvas_pos, tool)
                        elif tool.tool == 'fill':
                            flood_fill(canvas, canvas_pos, tool.color)
                            add_to_history(canvas, history, history_index)
            
            elif event.type == pygame.MOUSEMOTION:
                if drawing and in_canvas:
                    if tool.tool == 'brush':
                        draw_line_smooth(canvas, last_pos, canvas_pos, tool)
                        last_pos = canvas_pos
                    elif tool.tool == 'spray':
                        draw_spray(canvas, canvas_pos, tool)
                    elif tool.tool == 'eraser':
                        draw_line_smooth(canvas, last_pos, canvas_pos, tool, erase=True)
                        last_pos = canvas_pos
                    elif tool.tool in ['line', 'rect', 'circle']:
                        # Mostrar preview
                        temp_canvas = canvas.copy()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    if tool.tool in ['line', 'rect', 'circle'] and tool.start_pos:
                        if tool.tool == 'line':
                            draw_line_shape(canvas, tool.start_pos, canvas_pos, tool)
                        elif tool.tool == 'rect':
                            draw_rectangle(canvas, tool.start_pos, canvas_pos, tool)
                        elif tool.tool == 'circle':
                            draw_circle_shape(canvas, tool.start_pos, canvas_pos, tool)
                    
                    drawing = False
                    tool.start_pos = None
                    last_pos = None
                    add_to_history(canvas, history, history_index)
        
        # Dibujar preview de formas
        display_canvas = canvas
        if drawing and tool.tool in ['line', 'rect', 'circle'] and tool.start_pos and in_canvas:
            temp_canvas = canvas.copy()
            if tool.tool == 'line':
                draw_line_shape(temp_canvas, tool.start_pos, canvas_pos, tool)
            elif tool.tool == 'rect':
                draw_rectangle(temp_canvas, tool.start_pos, canvas_pos, tool)
            elif tool.tool == 'circle':
                draw_circle_shape(temp_canvas, tool.start_pos, canvas_pos, tool)
            display_canvas = temp_canvas
        
        # Renderizar
        paint_screen.fill((60, 60, 70))
        
        # Dibujar canvas escalado
        scaled_canvas = pygame.transform.scale(display_canvas, (canvas_display_size, canvas_display_size))
        paint_screen.blit(scaled_canvas, (canvas_x, canvas_y))
        
        # Marco del canvas
        pygame.draw.rect(paint_screen, WHITE, (canvas_x-2, canvas_y-2, canvas_display_size+4, canvas_display_size+4), 3)
        
        # Dibujar UI
        draw_paint_toolbar(paint_screen, tool, palette, paint_width, paint_height)
        
        # Cursor personalizado si está en el canvas
        if in_canvas:
            draw_custom_cursor(paint_screen, mouse_pos, tool)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Actualizar textura en el renderer
    if wall_key in renderer.graffiti_textures:
        del renderer.graffiti_textures[wall_key]
    
    # Restaurar ventana original
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Videojuego 3D Estilo Half-Life - Graffiti Edition")

def add_to_history(canvas, history, history_index):
    """Agrega el estado actual al historial"""
    # Eliminar estados futuros si estamos en medio del historial
    if history_index < len(history) - 1:
        history[history_index + 1:] = []
    
    # Agregar nuevo estado
    history.append(canvas.copy())
    history_index = len(history) - 1
    
    # Limitar historial a 20 estados
    if len(history) > 20:
        history.pop(0)
        history_index -= 1
    
    return history_index

def draw_brush(canvas, pos, tool):
    """Dibuja con pincel circular suave"""
    pygame.draw.circle(canvas, (*tool.color[:3], tool.opacity), pos, tool.size)

def draw_spray(canvas, pos, tool):
    """Efecto spray realista"""
    for _ in range(int(tool.size * 2)):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, tool.size * 1.5)
        px = int(pos[0] + math.cos(angle) * distance)
        py = int(pos[1] + math.sin(angle) * distance)
        
        if 0 <= px < GRAFFITI_SIZE and 0 <= py < GRAFFITI_SIZE:
            alpha = random.randint(50, tool.opacity)
            try:
                current = canvas.get_at((px, py))
                # Mezcla con el color existente
                new_color = (
                    int(current[0] * (1 - alpha/255) + tool.color[0] * (alpha/255)),
                    int(current[1] * (1 - alpha/255) + tool.color[1] * (alpha/255)),
                    int(current[2] * (1 - alpha/255) + tool.color[2] * (alpha/255)),
                    255
                )
                canvas.set_at((px, py), new_color)
            except:
                pass

def draw_eraser(canvas, pos, tool):
    """Borra dibujando blanco"""
    pygame.draw.circle(canvas, (240, 240, 240, 255), pos, tool.size)

def draw_line_smooth(canvas, start, end, tool, erase=False):
    """Dibuja línea suave entre dos puntos"""
    if start is None or end is None:
        return
    
    color = (240, 240, 240, 255) if erase else (*tool.color[:3], tool.opacity)
    
    # Calcular distancia
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < 1:
        pygame.draw.circle(canvas, color, end, tool.size)
        return
    
    # Dibujar círculos intermedios para suavidad
    steps = max(1, int(distance / 2))
    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        x = int(start[0] + dx * t)
        y = int(start[1] + dy * t)
        pygame.draw.circle(canvas, color, (x, y), tool.size)

def draw_line_shape(canvas, start, end, tool):
    """Dibuja línea recta"""
    pygame.draw.line(canvas, tool.color, start, end, tool.size)

def draw_rectangle(canvas, start, end, tool):
    """Dibuja rectángulo"""
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    pygame.draw.rect(canvas, tool.color, rect, tool.size)

def draw_circle_shape(canvas, start, end, tool):
    """Dibuja círculo"""
    radius = int(math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2))
    if radius > 0:
        pygame.draw.circle(canvas, tool.color, start, radius, tool.size)

def flood_fill(canvas, pos, color):
    """Rellena área con color (flood fill)"""
    if not (0 <= pos[0] < GRAFFITI_SIZE and 0 <= pos[1] < GRAFFITI_SIZE):
        return
    
    target_color = canvas.get_at(pos)
    if target_color[:3] == color[:3]:
        return
    
    # Flood fill optimizado con stack
    stack = [pos]
    visited = set()
    
    while stack and len(visited) < 50000:  # Limitar para evitar lag
        x, y = stack.pop()
        
        if (x, y) in visited:
            continue
        if not (0 <= x < GRAFFITI_SIZE and 0 <= y < GRAFFITI_SIZE):
            continue
        
        current = canvas.get_at((x, y))
        if current[:3] != target_color[:3]:
            continue
        
        canvas.set_at((x, y), color)
        visited.add((x, y))
        
        # Agregar vecinos
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

def draw_paint_toolbar(screen, tool, palette, width, height):
    """Dibuja la barra de herramientas mejorada"""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Panel lateral derecho
    panel_x = 690
    panel_y = 20
    panel_w = width - panel_x - 20
    panel_h = 650
    
    pygame.draw.rect(screen, (45, 45, 55), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)
    
    # Título
    title = font.render("HERRAMIENTAS", True, YELLOW)
    screen.blit(title, (panel_x + 20, panel_y + 10))
    
    y_offset = panel_y + 50
    
    # Herramienta actual
    tools_info = [
        ("B - Brush", 'brush'),
        ("S - Spray", 'spray'),
        ("E - Eraser", 'eraser'),
        ("L - Line", 'line'),
        ("R - Rectangle", 'rect'),
        ("C - Circle", 'circle'),
        ("F - Fill", 'fill'),
    ]
    
    for text, tool_name in tools_info:
        color = GREEN if tool.tool == tool_name else WHITE
        surf = small_font.render(text, True, color)
        screen.blit(surf, (panel_x + 20, y_offset))
        y_offset += 25
    
    y_offset += 20
    
    # Tamaño
    size_text = small_font.render(f"Tamaño: {tool.size}", True, WHITE)
    screen.blit(size_text, (panel_x + 20, y_offset))
    y_offset += 25
    
    size_help = small_font.render("[ ] - Cambiar tamaño", True, LIGHT_GRAY)
    screen.blit(size_help, (panel_x + 20, y_offset))
    y_offset += 40
    
    # Preview del color actual
    color_label = small_font.render("Color actual:", True, WHITE)
    screen.blit(color_label, (panel_x + 20, y_offset))
    y_offset += 25
    
    color_rect = pygame.Rect(panel_x + 20, y_offset, 60, 60)
    pygame.draw.rect(screen, tool.color, color_rect)
    pygame.draw.rect(screen, WHITE, color_rect, 2)
    y_offset += 80
    
    # Controles
    controls = [
        "CONTROLES:",
        "Click - Dibujar",
        "Ctrl+Z - Deshacer",
        "Ctrl+Y - Rehacer",
        "X - Limpiar todo",
        "ESC - Salir y guardar"
    ]
    
    for text in controls:
        color = YELLOW if text == "CONTROLES:" else LIGHT_GRAY
        surf = small_font.render(text, True, color)
        screen.blit(surf, (panel_x + 20, y_offset))
        y_offset += 22
    
    # Dibujar paleta de colores
    palette.draw(screen)
    
    # Texto de la paleta
    palette_label = small_font.render("Paleta de colores:", True, WHITE)
    screen.blit(palette_label, (20, height - 140))

def draw_custom_cursor(screen, pos, tool):
    """Dibuja cursor personalizado según la herramienta"""
    if tool.tool in ['brush', 'spray', 'eraser']:
        # Círculo que muestra el tamaño
        pygame.draw.circle(screen, WHITE, pos, tool.size, 1)
        pygame.draw.circle(screen, (0, 0, 0), pos, tool.size + 1, 1)
    
    # Crosshair central
    pygame.draw.line(screen, WHITE, (pos[0] - 5, pos[1]), (pos[0] + 5, pos[1]), 1)
    pygame.draw.line(screen, WHITE, (pos[0], pos[1] - 5), (pos[0], pos[1] + 5), 1)