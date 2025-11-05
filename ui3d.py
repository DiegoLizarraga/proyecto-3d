import pygame
from OpenGL.GL import *
import math

from settings import *
from world import graffiti_walls, WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

class UI3D:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colores urbanos/neón
        self.NEON_GREEN = (57, 255, 20)
        self.NEON_PINK = (255, 20, 147)
        self.NEON_BLUE = (0, 191, 255)
        self.NEON_YELLOW = (255, 255, 0)
        self.NEON_ORANGE = (255, 165, 0)
        self.URBAN_PURPLE = (138, 43, 226)
        self.DARK_BG = (20, 20, 30)
        self.LIGHT_TEXT = (240, 240, 240)
        
    def begin_2d_rendering(self):
        """Cambia a modo 2D para dibujar UI"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)  # Corregido: Y va de HEIGHT (arriba) a 0 (abajo)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_FOG)
    
    def end_2d_rendering(self):
        """Restaura modo 3D"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_FOG)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def draw_rect(self, x, y, w, h, color, filled=True):
        """Dibuja un rectángulo en 2D con coordenadas corregidas"""
        # Ya no invertimos Y, usamos coordenadas directas de pygame
        
        if filled:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_LOOP)
        glColor4f(color[0]/255, color[1]/255, color[2]/255, 1.0 if len(color) == 3 else color[3]/255)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
    
    def draw_text_gl(self, text, x, y, color, font_size=None):
        """Dibuja texto usando pygame y lo convierte a textura OpenGL - CORREGIDO"""
        # Ya no invertimos Y
        
        font = self.small_font if font_size is None else pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        w, h = text_surface.get_size()
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        # CORRECCIÓN PRINCIPAL: Invertir coordenadas de textura en Y
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        
        glDeleteTextures([tex_id])
        glDisable(GL_TEXTURE_2D)
    
    def draw_minimap(self, player):
        """Dibuja el minimapa con estilo urbano"""
        minimap_size = 180
        minimap_scale = minimap_size / (MAP_WIDTH * TILE_SIZE)
        
        # Fondo del minimapa con estilo urbano
        self.draw_rect(8, 8, minimap_size + 4, minimap_size + 4, self.DARK_BG)
        self.draw_rect(10, 10, minimap_size, minimap_size, (40, 40, 50))
        
        # Borde neón
        self.draw_rect(10, 10, minimap_size, minimap_size, self.NEON_BLUE, filled=False)
        
        tile_width = minimap_size / MAP_WIDTH
        tile_height = minimap_size / MAP_HEIGHT
        
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall_type = WORLD_MAP[z][x]
                if wall_type == 0:
                    color = (60, 60, 70)
                elif wall_type == 1:
                    color = (100, 100, 120)
                elif wall_type == 2:
                    color = (140, 140, 160)
                else:
                    color = (80, 80, 100)
                
                rect_x = 10 + x * tile_width
                rect_y = 10 + z * tile_height
                self.draw_rect(rect_x, rect_y, tile_width, tile_height, color)
                
                # Marcar graffiti con estilo neón
                has_graffiti = any(key[:2] == (x, z) for key in graffiti_walls.keys())
                if has_graffiti:
                    cx = rect_x + tile_width / 2
                    cy = rect_y + tile_height / 2
                    # Dibujar punto neón
                    self.draw_rect(cx - 3, cy - 3, 6, 6, self.NEON_PINK)
        
        # Jugador con estilo neón
        player_x = 10 + player.x * minimap_scale
        player_y = 10 + player.z * minimap_scale
        
        # Círculo del jugador con efecto neón
        self.draw_rect(player_x - 5, player_y - 5, 10, 10, self.DARK_BG)
        self.draw_rect(player_x - 3, player_y - 3, 6, 6, self.NEON_GREEN)
        
        # Dirección con línea neón
        end_x = player_x + math.cos(math.radians(player.yaw)) * 12
        end_y = player_y + math.sin(math.radians(player.yaw)) * 12
        self.draw_line(player_x, player_y, end_x, end_y, self.NEON_GREEN)
    
    def draw_line(self, x1, y1, x2, y2, color):
        """Dibuja una línea con coordenadas corregidas"""
        # Ya no invertimos Y
        
        glBegin(GL_LINES)
        glColor3f(color[0]/255, color[1]/255, color[2]/255)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()
    
    def draw_ui(self, player):
        """Dibuja toda la UI con estilo urbano"""
        # Minimapa
        self.draw_minimap(player)
        
        # Barra de stamina con estilo urbano
        stamina_width = 150
        stamina_height = 15
        stamina_x = 20
        stamina_y = WINDOW_HEIGHT - 60
        
        # Fondo de la barra
        self.draw_rect(stamina_x - 2, stamina_y - 2, stamina_width + 4, stamina_height + 4, self.DARK_BG)
        self.draw_rect(stamina_x, stamina_y, stamina_width, stamina_height, (40, 40, 50))
        
        # Borde neón
        self.draw_rect(stamina_x, stamina_y, stamina_width, stamina_height, self.NEON_BLUE, filled=False)
        
        current_width = int((player.stamina / STAMINA_MAX) * stamina_width)
        if player.stamina > 30:
            stamina_color = self.NEON_GREEN
        elif player.stamina > 10:
            stamina_color = self.NEON_YELLOW
        else:
            stamina_color = self.NEON_PINK
        
        self.draw_rect(stamina_x, stamina_y, current_width, stamina_height, stamina_color)
        
        # Texto de stamina con estilo urbano
        self.draw_text_gl(f"ENERGÍA: {int(player.stamina)}", stamina_x, stamina_y - 18, self.NEON_ORANGE)
        
        # Verificar si hay pared cerca
        wall_info = player.get_wall_in_front()
        if wall_info:
            # Indicador de que puede pintar con estilo neón
            self.draw_text_gl("¡PULSA Z PARA PINTAR!", WINDOW_WIDTH // 2 - 80, 30, self.NEON_GREEN, font_size=20)
        
        # Controles con estilo urbano
        controls_text = [
            "=== CONTROLES ===",
            "Mouse - Mirar",
            "WASD - Mover",
            "SHIFT - Correr",
            "",
            "GRAFFITI:",
            "Z - Modo paint",
            "C - Limpiar todo",
            "",
            "ESC - Salir"
        ]
        
        controls_x = WINDOW_WIDTH - 180
        controls_start_y = WINDOW_HEIGHT - (len(controls_text) * 16) + 20
        
        # Fondo para los controles
        self.draw_rect(controls_x - 10, controls_start_y - 10, 170, len(controls_text) * 16 + 20, 
                      (20, 20, 30, 200))  # Semi-transparente
        
        for i, text in enumerate(controls_text):
            if text == "=== CONTROLES ===":
                color = self.NEON_YELLOW
            elif text in ("GRAFFITI:", "Mouse - Mirar"):
                color = self.LIGHT_TEXT
            else:
                color = (180, 180, 200)
            self.draw_text_gl(text, controls_x, controls_start_y + i * 16, color)
        
        # Contador de graffitis con estilo urbano
        total_walls = len(graffiti_walls)
        self.draw_text_gl(f"PAREDES CON GRAFFITI: {total_walls}", 20, WINDOW_HEIGHT - 90, self.NEON_PINK)
        
        if total_walls > 0:
            self.draw_text_gl("PULSA C PARA LIMPIAR", 20, WINDOW_HEIGHT - 70, self.NEON_ORANGE)
        
        # Crosshair neón en el centro
        cx = WINDOW_WIDTH / 2
        cy = WINDOW_HEIGHT / 2
        crosshair_size = 10
        
        # Si hay pared cerca, crosshair verde neón
        if wall_info:
            crosshair_color = self.NEON_GREEN
        else:
            crosshair_color = self.NEON_BLUE
        
        # Crosshair horizontal con efecto neón
        self.draw_line(cx - crosshair_size, cy, cx + crosshair_size, cy, crosshair_color)
        # Crosshair vertical con efecto neón
        self.draw_line(cx, cy - crosshair_size, cx, cy + crosshair_size, crosshair_color)
        
        # Puntos en los extremos del crosshair para más estilo
        self.draw_rect(cx - crosshair_size - 2, cy - 2, 4, 4, crosshair_color)
        self.draw_rect(cx + crosshair_size - 2, cy - 2, 4, 4, crosshair_color)
        self.draw_rect(cx - 2, cy - crosshair_size - 2, 4, 4, crosshair_color)
        self.draw_rect(cx - 2, cy + crosshair_size - 2, 4, 4, crosshair_color)