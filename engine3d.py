import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

from settings import *
from world import WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, graffiti_walls


# ─────────────────────────────────────────────────────────────────────────────
# Constantes de sombreado por cara (iluminación direccional baked)
# ─────────────────────────────────────────────────────────────────────────────
FACE_SHADE = {
    'N': 0.85,   # Norte
    'S': 1.00,   # Sur — cara más iluminada
    'E': 0.92,   # Este
    'W': 0.78,   # Oeste — algo más oscuro
    'top': 0.65, # Techo de bloque
}

# Colores base por tipo de pared — valores altos para que el shading
# no los lleve a negro
WALL_COLORS = {
    1: (0.82, 0.42, 0.38),  # Ladrillos rojizos
    2: (0.92, 0.92, 0.90),  # Piedra blanca
    3: (0.70, 0.70, 0.72),  # Gris genérico
}


# ─────────────────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self, x, y, z, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw   # grados, solo horizontal

        # Planos del frustum en XZ (calculados en update_frustum)
        self._frustum_planes = []

    # ------------------------------------------------------------------
    def update_view(self):
        glLoadIdentity()
        look_x = self.x + math.cos(math.radians(self.yaw))
        look_z = self.z + math.sin(math.radians(self.yaw))
        gluLookAt(
            self.x, self.y, self.z,
            look_x, self.y, look_z,
            0, 1, 0,
        )
        self._update_frustum()

    # ------------------------------------------------------------------
    def _update_frustum(self):
        """Calcula 3 planos 2D (XZ) del frustum: izquierdo, derecho, trasero."""
        half_fov = FOV / 2.0
        yaw_rad = math.radians(self.yaw)
        left_rad = math.radians(self.yaw - half_fov - 5)   # margen 5°
        right_rad = math.radians(self.yaw + half_fov + 5)

        # Normales de los planos (apuntando hacia adentro del frustum)
        # Plano izquierdo: normal apunta a la derecha del rayo izquierdo
        ln = ( math.sin(left_rad),  math.cos(left_rad))
        # Plano derecho: normal apunta a la izquierda del rayo derecho
        rn = (-math.sin(right_rad), -math.cos(right_rad))
        # Plano trasero: normal apunta hacia adelante
        fn = ( math.cos(yaw_rad), math.sin(yaw_rad))

        self._frustum_planes = [
            (ln, (self.x, self.z)),
            (rn, (self.x, self.z)),
            (fn, (self.x, self.z)),
        ]

    # ------------------------------------------------------------------
    def tile_in_frustum(self, tx, tz):
        """
        Comprueba si el tile (tx, tz) en coordenadas de mapa
        es visible aproximadamente dentro del frustum 2D.
        """
        # Centro mundial del tile
        cx = (tx + 0.5) * TILE_SIZE
        cz = (tz + 0.5) * TILE_SIZE
        r = TILE_SIZE * 0.85  # radio de conservatismo

        for (nx, nz), (ox, oz) in self._frustum_planes:
            # Distancia del centro del tile al plano
            d = nx * (cx - ox) + nz * (cz - oz)
            if d < -r:
                return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
class Renderer3D:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.wall_height = TILE_SIZE * 1.5
        self.floor_y = 0.0
        self.ceiling_y = self.wall_height

        # Cache de texturas OpenGL para graffiti  {key -> gl_tex_id}
        self.graffiti_textures = {}
        # Versión del surface para detectar cambios
        self._graffiti_versions = {}

    # ------------------------------------------------------------------
    def init_opengl(self):
        # Limpiar caché de texturas: el contexto OpenGL puede haber cambiado
        # (ej. al recrear la ventana después del modo paint)
        self.graffiti_textures.clear()
        self._graffiti_versions.clear()

        glViewport(0, 0, self.width, self.height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, self.width / self.height, 0.5, 2000.0)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Sin lighting de OpenGL — usamos FACE_SHADE manual (más predecible)
        glDisable(GL_LIGHTING)

        # Niebla lineal — el color debe coincidir con glClearColor
        # para que el horizonte se funda suavemente
        fog_color = [0.15, 0.15, 0.20, 1.0]
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, fog_color)
        glFogf(GL_FOG_START, TILE_SIZE * 6)    # empieza a 6 tiles
        glFogf(GL_FOG_END,   TILE_SIZE * 14)   # opaco a 14 tiles

        # Sin back-face culling: los quads de pared se ven desde dentro
        # del mapa y no tienen winding consistente
        glDisable(GL_CULL_FACE)

        glClearColor(*fog_color)

    # ------------------------------------------------------------------
    # Texturas
    # ------------------------------------------------------------------
    def _upload_graffiti_texture(self, key):
        """Sube (o re-sube si cambió) el surface de graffiti a GPU."""
        surf = graffiti_walls.get(key)
        if surf is None:
            return

        version = id(surf)   # Si se reemplazó el surface, id cambia
        if self.graffiti_textures.get(key) and self._graffiti_versions.get(key) == version:
            return  # Ya está actualizado

        # Borrar textura vieja si existe
        old = self.graffiti_textures.pop(key, None)
        if old is not None:
            glDeleteTextures([old])

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        w, h = surf.get_size()
        # pygame almacena de arriba a abajo; OpenGL espera de abajo a arriba
        tex_data = pygame.image.tostring(surf, "RGBA", True)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.graffiti_textures[key] = tex_id
        self._graffiti_versions[key] = version

    # ------------------------------------------------------------------
    # Geometría
    # ------------------------------------------------------------------
    @staticmethod
    def _shaded(base_color, face_key):
        s = FACE_SHADE[face_key]
        return (base_color[0] * s, base_color[1] * s, base_color[2] * s)

    # ------------------------------------------------------------------
    def _draw_quad(self, verts, color):
        """Dibuja un quad GL_QUADS con color sólido."""
        glColor3f(*color)
        glBegin(GL_QUADS)
        for v in verts:
            glVertex3f(*v)
        glEnd()

    # ------------------------------------------------------------------
    def _draw_quad_textured(self, verts, tex_id, face_idx):
        """Dibuja quad con textura de graffiti encima (blending)."""
        UV_TABLE = [
            # face_idx 0 Norte
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            # face_idx 1 Sur
            [(1, 0), (0, 0), (0, 1), (1, 1)],
            # face_idx 2 Oeste
            [(0, 0), (1, 0), (1, 1), (0, 1)],
            # face_idx 3 Este
            [(1, 0), (0, 0), (0, 1), (1, 1)],
        ]
        uvs = UV_TABLE[face_idx] if face_idx < len(UV_TABLE) else UV_TABLE[0]

        normal = _calc_normal(verts)
        OFFSET = 0.015  # empujar ligeramente hacia la cámara

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1, 1, 1, 1)

        glBegin(GL_QUADS)
        for i, v in enumerate(verts):
            glTexCoord2f(*uvs[i])
            glVertex3f(v[0] + normal[0] * OFFSET,
                       v[1] + normal[1] * OFFSET,
                       v[2] + normal[2] * OFFSET)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    # ------------------------------------------------------------------
    def draw_wall(self, x, z, wall_type, camera):
        """Dibuja las caras visibles de un bloque de pared."""
        wx = x * TILE_SIZE
        wz = z * TILE_SIZE
        fy = self.floor_y
        cy = self.ceiling_y
        ts = TILE_SIZE
        base = WALL_COLORS.get(wall_type, WALL_COLORS[3])

        def face(verts, face_key, face_idx, graffiti_key):
            color = self._shaded(base, face_key)
            self._draw_quad(verts, color)
            # Graffiti
            gk = graffiti_key
            if gk in graffiti_walls:
                self._upload_graffiti_texture(gk)
                tex = self.graffiti_textures.get(gk)
                if tex:
                    self._draw_quad_textured(verts, tex, face_idx)

        # ── Norte (Z−) ────────────────────────────────────────────────
        if z == 0 or WORLD_MAP[z - 1][x] == 0:
            verts = [
                (wx,      fy, wz),
                (wx + ts, fy, wz),
                (wx + ts, cy, wz),
                (wx,      cy, wz),
            ]
            face(verts, 'N', 0, (x, z, 'N'))

        # ── Sur (Z+) ──────────────────────────────────────────────────
        if z == MAP_HEIGHT - 1 or WORLD_MAP[z + 1][x] == 0:
            verts = [
                (wx + ts, fy, wz + ts),
                (wx,      fy, wz + ts),
                (wx,      cy, wz + ts),
                (wx + ts, cy, wz + ts),
            ]
            face(verts, 'S', 1, (x, z, 'S'))

        # ── Oeste (X−) ────────────────────────────────────────────────
        if x == 0 or WORLD_MAP[z][x - 1] == 0:
            verts = [
                (wx, fy, wz + ts),
                (wx, fy, wz),
                (wx, cy, wz),
                (wx, cy, wz + ts),
            ]
            face(verts, 'W', 2, (x, z, 'W'))

        # ── Este (X+) ─────────────────────────────────────────────────
        if x == MAP_WIDTH - 1 or WORLD_MAP[z][x + 1] == 0:
            verts = [
                (wx + ts, fy, wz),
                (wx + ts, fy, wz + ts),
                (wx + ts, cy, wz + ts),
                (wx + ts, cy, wz),
            ]
            face(verts, 'E', 3, (x, z, 'E'))

        # ── Top del bloque (solo visible si hay hueco arriba) ─────────
        # Los bloques siempre tienen techo propio (interior del sólido),
        # pero solo se dibuja si no hay otro bloque encima (aquí siempre
        # los bloques van hasta el techo de la sala, así que lo omitimos
        # para ganar rendimiento — el techo de sala cubre ese hueco).

    # ------------------------------------------------------------------
    def draw_floor(self):
        """Suelo con patrón de tablero y transición suave."""
        glBegin(GL_QUADS)
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if WORLD_MAP[z][x] != 0:
                    continue
                wx = x * TILE_SIZE
                wz = z * TILE_SIZE

                if (x + z) % 2 == 0:
                    glColor3f(0.30, 0.30, 0.33)
                else:
                    glColor3f(0.35, 0.35, 0.38)

                glVertex3f(wx,            self.floor_y, wz)
                glVertex3f(wx + TILE_SIZE, self.floor_y, wz)
                glVertex3f(wx + TILE_SIZE, self.floor_y, wz + TILE_SIZE)
                glVertex3f(wx,            self.floor_y, wz + TILE_SIZE)
        glEnd()

    # ------------------------------------------------------------------
    def draw_ceiling(self):
        """Techo oscuro uniforme."""
        glBegin(GL_QUADS)
        glColor3f(0.20, 0.20, 0.25)
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if WORLD_MAP[z][x] != 0:
                    continue
                wx = x * TILE_SIZE
                wz = z * TILE_SIZE
                # CCW visto desde abajo → tapa hacia abajo
                glVertex3f(wx,            self.ceiling_y, wz)
                glVertex3f(wx,            self.ceiling_y, wz + TILE_SIZE)
                glVertex3f(wx + TILE_SIZE, self.ceiling_y, wz + TILE_SIZE)
                glVertex3f(wx + TILE_SIZE, self.ceiling_y, wz)
        glEnd()

    # ------------------------------------------------------------------
    def render_world(self, camera: Camera):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        camera.update_view()

        # Suelo y techo primero (sin depth write necesario, pintura de fondo)
        self.draw_floor()
        self.draw_ceiling()

        # Paredes con frustum culling
        for z in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                wall_type = WORLD_MAP[z][x]
                if wall_type == 0:
                    continue
                if not camera.tile_in_frustum(x, z):
                    continue
                self.draw_wall(x, z, wall_type, camera)

    # ------------------------------------------------------------------
    def cleanup(self):
        ids = list(self.graffiti_textures.values())
        if ids:
            glDeleteTextures(ids)
        self.graffiti_textures.clear()
        self._graffiti_versions.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Utilidad fuera de clase (evita self. en hot-path)
# ─────────────────────────────────────────────────────────────────────────────
def _calc_normal(verts):
    v0 = np.array(verts[0], dtype=np.float32)
    v1 = np.array(verts[1], dtype=np.float32)
    v2 = np.array(verts[2], dtype=np.float32)
    n = np.cross(v1 - v0, v2 - v0)
    length = np.linalg.norm(n)
    if length > 1e-6:
        n /= length
    return n