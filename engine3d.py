import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

from settings import *
from world import WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, graffiti_walls

class Camera:
    def __init__(self, x, y, z, yaw):
        self.x = x
        self.y = y  # Altura fija para Half-Life style
        self.z = z
        self.yaw = yaw  # Solo rotación horizontal
        
    def update_view(self):
        glLoadIdentity()
        # Calcular dirección de vista
        look_x = self.x + math.cos(math.radians(self.yaw))
        look_z = self.z + math.sin(math.radians(self.yaw))
        gluLookAt(
            self.x, self.y, self.z,  # Posición de la cámara
            look_x, self.y, look_z,  # Punto a donde mira (misma altura Y)
            0, 1, 0  # Vector "arriba"
        )

class Renderer3D:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.wall_height = TILE_SIZE * 1.5
        self.floor_y = 0
        self.ceiling_y = self.wall_height
        
        # Cargar texturas de graffiti en OpenGL
        self.graffiti_textures = {}
        
    def init_opengl(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Configuración de OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Luz ambiente mejorada
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Niebla para profundidad atmosférica
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, [0.5, 0.5, 0.6, 1.0])
        glFogf(GL_FOG_START, TILE_SIZE * 5)
        glFogf(GL_FOG_END, TILE_SIZE * 12)
        
    def draw_cube_face(self, vertices, color, graffiti_key=None, face_idx=0):
        """Dibuja una cara de un cubo con opción de graffiti"""
        glBegin(GL_QUADS)
        glColor3f(*color)
        
        for vertex in vertices:
            glVertex3f(*vertex)
        glEnd()
        
        # Dibujar graffiti si existe
        if graffiti_key and graffiti_key in graffiti_walls:
            self.draw_graffiti_on_face(vertices, graffiti_key, face_idx)
    
    def draw_graffiti_on_face(self, vertices, key, face_idx):
        """Dibuja graffiti sobre una cara de pared - CORREGIDO"""
        surf = graffiti_walls[key]
        width = surf.get_width()
        height = surf.get_height()
        
        # Convertir superficie pygame a textura OpenGL (voltear verticalmente)
        tex_data = pygame.image.tostring(surf, "RGBA", False)  # False = no voltear
        
        glEnable(GL_TEXTURE_2D)
        if key not in self.graffiti_textures:
            self.graffiti_textures[key] = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, self.graffiti_textures[key])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Coordenadas de textura corregidas según la cara
        tex_coords = self.get_tex_coords_for_face(face_idx)
        
        # Dibujar quad con textura
        glBegin(GL_QUADS)
        glColor4f(1, 1, 1, 1)
        for i, vertex in enumerate(vertices):
            glTexCoord2f(*tex_coords[i])
            # Offset pequeño hacia la cámara para evitar z-fighting
            normal = self.calculate_face_normal(vertices)
            offset_vertex = [vertex[j] + normal[j] * 0.01 for j in range(3)]
            glVertex3f(*offset_vertex)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
    
    def get_tex_coords_for_face(self, face_idx):
        """Retorna coordenadas de textura correctas para cada cara"""
        # face_idx: 0=Norte, 1=Sur, 2=Oeste, 3=Este
        if face_idx == 0:  # Norte (Z-)
            return [(0, 1), (1, 1), (1, 0), (0, 0)]
        elif face_idx == 1:  # Sur (Z+)
            return [(1, 1), (0, 1), (0, 0), (1, 0)]
        elif face_idx == 2:  # Oeste (X-)
            return [(0, 1), (1, 1), (1, 0), (0, 0)]
        elif face_idx == 3:  # Este (X+)
            return [(1, 1), (0, 1), (0, 0), (1, 0)]
        return [(0, 1), (1, 1), (1, 0), (0, 0)]
    
    def calculate_face_normal(self, vertices):
        """Calcula la normal de una cara"""
        v1 = np.array(vertices[1]) - np.array(vertices[0])
        v2 = np.array(vertices[2]) - np.array(vertices[0])
        normal = np.cross(v1, v2)
        length = np.linalg.norm(normal)
        if length > 0:
            normal = normal / length
        return normal
        
    def draw_wall(self, x, z, wall_type, check_neighbors=True):
        """Dibuja un cubo de pared con optimización de caras"""
        wx = x * TILE_SIZE
        wz = z * TILE_SIZE
        
        # Colores según tipo de pared
        if wall_type == 1:
            color = (0.7, 0.3, 0.3)  # Ladrillos rojizos
        elif wall_type == 2:
            color = (0.9, 0.9, 0.9)  # Blancos
        else:
            color = (0.6, 0.6, 0.6)  # Grises
        
        # Solo dibujar caras visibles (culling básico)
        # Norte (Z-)
        if z == 0 or WORLD_MAP[z-1][x] == 0:
            face = [
                (wx, self.floor_y, wz),
                (wx + TILE_SIZE, self.floor_y, wz),
                (wx + TILE_SIZE, self.ceiling_y, wz),
                (wx, self.ceiling_y, wz)
            ]
            self.draw_cube_face(face, color, (x, z, 'N'), 0)
        
        # Sur (Z+)
        if z == MAP_HEIGHT-1 or WORLD_MAP[z+1][x] == 0:
            face = [
                (wx + TILE_SIZE, self.floor_y, wz + TILE_SIZE),
                (wx, self.floor_y, wz + TILE_SIZE),
                (wx, self.ceiling_y, wz + TILE_SIZE),
                (wx + TILE_SIZE, self.ceiling_y, wz + TILE_SIZE)
            ]
            self.draw_cube_face(face, color, (x, z, 'S'), 1)
        
        # Oeste (X-)
        if x == 0 or WORLD_MAP[z][x-1] == 0:
            face = [
                (wx, self.floor_y, wz + TILE_SIZE),
                (wx, self.floor_y, wz),
                (wx, self.ceiling_y, wz),
                (wx, self.ceiling_y, wz + TILE_SIZE)
            ]
            self.draw_cube_face(face, color, (x, z, 'W'), 2)
        
        # Este (X+)
        if x == MAP_WIDTH-1 or WORLD_MAP[z][x+1] == 0:
            face = [
                (wx + TILE_SIZE, self.floor_y, wz),
                (wx + TILE_SIZE, self.floor_y, wz + TILE_SIZE),
                (wx + TILE_SIZE, self.ceiling_y, wz + TILE_SIZE),
                (wx + TILE_SIZE, self.ceiling_y, wz)
            ]
            self.draw_cube_face(face, color, (x, z, 'E'), 3)
        
        # Techo - solo si es necesario
        if check_neighbors:
            face = [
                (wx, self.ceiling_y, wz),
                (wx + TILE_SIZE, self.ceiling_y, wz),
                (wx + TILE_SIZE, self.ceiling_y, wz + TILE_SIZE),
                (wx, self.ceiling_y, wz + TILE_SIZE)
            ]
            glBegin(GL_QUADS)
            darker_color = tuple(c * 0.5 for c in color)
            glColor3f(*darker_color)
            for vertex in face:
                glVertex3f(*vertex)
            glEnd()
    
    def draw_floor(self):
        """Dibuja el suelo con patrón de tablero"""
        glBegin(GL_QUADS)
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if WORLD_MAP[z][x] == 0:  # Solo donde hay espacio libre
                    wx = x * TILE_SIZE
                    wz = z * TILE_SIZE
                    
                    # Patrón de tablero
                    if (x + z) % 2 == 0:
                        glColor3f(0.2, 0.2, 0.22)
                    else:
                        glColor3f(0.25, 0.25, 0.27)
                    
                    glVertex3f(wx, self.floor_y, wz)
                    glVertex3f(wx + TILE_SIZE, self.floor_y, wz)
                    glVertex3f(wx + TILE_SIZE, self.floor_y, wz + TILE_SIZE)
                    glVertex3f(wx, self.floor_y, wz + TILE_SIZE)
        glEnd()
    
    def draw_ceiling(self):
        """Dibuja el techo"""
        glBegin(GL_QUADS)
        glColor3f(0.15, 0.15, 0.18)
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if WORLD_MAP[z][x] == 0:
                    wx = x * TILE_SIZE
                    wz = z * TILE_SIZE
                    glVertex3f(wx, self.ceiling_y, wz)
                    glVertex3f(wx, self.ceiling_y, wz + TILE_SIZE)
                    glVertex3f(wx + TILE_SIZE, self.ceiling_y, wz + TILE_SIZE)
                    glVertex3f(wx + TILE_SIZE, self.ceiling_y, wz)
        glEnd()
    
    def render_world(self, camera):
        """Renderiza todo el mundo 3D"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.5, 0.5, 0.6, 1.0)
        
        camera.update_view()
        
        # Actualizar posición de luz con la cámara
        glLightfv(GL_LIGHT0, GL_POSITION, [camera.x, camera.y + 20, camera.z, 1.0])
        
        # Dibujar en orden: suelo, paredes, techo
        self.draw_floor()
        
        # Dibujar paredes
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall_type = WORLD_MAP[z][x]
                if wall_type > 0:
                    self.draw_wall(x, z, wall_type)
        
        self.draw_ceiling()
    
    def cleanup(self):
        """Limpia texturas de OpenGL"""
        if self.graffiti_textures:
            glDeleteTextures(list(self.graffiti_textures.values()))