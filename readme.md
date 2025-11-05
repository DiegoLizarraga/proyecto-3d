# Videojuego 3D Estilo Half-Life - Graffiti Edition

Un videojuego 3D con motor real de OpenGL inspirado en Half-Life, creado con Python, Pygame y PyOpenGL. Incluye un sistema completo de graffiti para pintar en las paredes del mundo 3D.

![Screenshot del juego](screenshot.png)

## 🎮 Características Principales

### Motor 3D Real (OpenGL)
- **Geometría 3D verdadera** con paredes, suelos y techos renderizados en OpenGL
- **Iluminación dinámica** que sigue al jugador
- **Niebla atmosférica** para añadir profundidad y ambiente
- **Texturas procedurales** en paredes (ladrillos y piedra)
- **Culling de caras** para optimizar el rendimiento

### Sistema de Movimiento Avanzado
- **Control con mouse** para rotación suave de cámara (solo horizontal, sin mirar arriba/abajo)
- **Movimiento WASD** completo con strafe lateral
- **Sistema de stamina** con sprint limitado
- **Colisión circular** suave con las paredes
- **Velocidad ajustable** entre caminar y correr

### Sistema de Graffiti Completo
- **Modo pintura inmersivo** al presionar Z cerca de una pared
- **Múltiples herramientas**: lápiz, borrador, líneas, rectángulos, círculos y spray
- **8 colores diferentes** para elegir
- **Tamaño de pincel ajustable** (1-50 píxeles)
- **Alta resolución** (256x256) para graffitis detallados
- **Persistencia en el mundo 3D** - tus dibujos permanecen en las paredes
- **Graffiti por cara** - cada lado de la pared puede tener su propio diseño

### Interfaz y UI
- **Minimapa en tiempo real** con indicadores de posición y dirección
- **Barra de stamina** con colores de alerta
- **Crosshair central** para mejor puntería
- **Contador de graffitis** creados
- **Controles en pantalla** siempre visibles

## 📋 Requisitos

- Python 3.8 o superior
- Tarjeta gráfica con soporte OpenGL 2.0+
- 4GB RAM mínimo
- Sistema operativo: Windows, Linux o macOS

## 🔧 Instalación

1. **Clona o descarga el proyecto:**
   ```bash
   git clone <tu-repositorio>
   cd graffiti-3d-game
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Las dependencias incluyen:
   - `pygame==2.5.2` - Motor de juego base
   - `PyOpenGL==3.1.7` - Renderizado 3D
   - `PyOpenGL-accelerate==3.1.7` - Aceleración de rendimiento
   - `numpy>=1.24.0` - Operaciones matemáticas

3. **Ejecuta el juego:**
   ```bash
   python main.py
   ```

## 🎯 Controles

### Movimiento
- **Mouse**: Rotar cámara (solo horizontal)
- **W**: Avanzar
- **S**: Retroceder
- **A**: Moverse lateral izquierda (strafe)
- **D**: Moverse lateral derecha (strafe)
- **SHIFT**: Correr (consume stamina)
- **Flechas**: Control alternativo de rotación

### Sistema de Graffiti
- **Z**: Entrar en modo pintura (cerca de una pared)
- **C**: Limpiar todos los graffitis del mapa

### Modo Pintura (cuando presionas Z)
#### Herramientas:
- **P**: Lápiz (dibujo libre)
- **E**: Borrador
- **L**: Línea recta
- **R**: Rectángulo
- **O**: Círculo
- **S**: Spray (efecto aerosol)

#### Colores:
- **1-8**: Cambiar entre 8 colores predefinidos (rojo, azul, verde, amarillo, rosa, naranja, púrpura, cian)

#### Ajustes:
- **+/=**: Aumentar tamaño de pincel
- **-**: Disminuir tamaño de pincel
- **X**: Limpiar el canvas actual completamente

#### Salir:
- **ESC**: Salir del modo pintura y volver al juego

### General
- **ESC**: Salir del juego (cuando no estás en modo pintura)

## 🏗️ Estructura del Proyecto

```
graffiti-3d-game/
├── main.py              # Archivo principal, loop del juego
├── engine3d.py          # Motor de renderizado 3D con OpenGL
├── player3d.py          # Lógica del jugador y física
├── ui3d.py              # Sistema de UI compatible con OpenGL
├── paint_mode.py        # Sistema completo de graffiti
├── world.py             # Definición del mapa y texturas
├── settings.py          # Configuración y constantes
├── requirements.txt     # Dependencias
└── README.md           # Este archivo
```

## 🎨 Sistema de Graffiti - Detalles Técnicos

### Cómo Funciona
1. Al presionar **Z** cerca de una pared, el juego detecta qué cara de la pared estás mirando
2. Se crea una superficie de 256x256 píxeles para esa cara específica
3. Puedes dibujar en esta superficie con varias herramientas
4. El dibujo se convierte en textura OpenGL y se mapea sobre la pared
5. Cada cara de cada pared puede tener su propio graffiti independiente

### Características Avanzadas
- **Transparencia alfa**: Los graffitis respetan la transparencia
- **Blending correcto**: Se mezclan apropiadamente con las texturas de pared
- **Z-fighting prevention**: Los graffitis se renderizan con un pequeño offset
- **Caché de texturas**: Las texturas se generan una vez y se reutilizan

## ⚙️ Personalización

### Modificar el Mapa
Edita `WORLD_MAP` en `world.py`:
- `0` = espacio vacío
- `1` = pared de ladrillos (roja)
- `2` = pared de piedra (blanca)

### Ajustar Velocidades
En `settings.py`:
```python
PLAYER_SPEED = 2.5      # Velocidad caminando
RUN_SPEED = 4.5         # Velocidad corriendo
MOUSE_SENSITIVITY = 0.2  # Sensibilidad del mouse
```

### Cambiar Colores de Graffiti
En `settings.py`, modifica `SPRAY_COLORS`:
```python
SPRAY_COLORS = [RED, BLUE, GREEN, YELLOW, PINK, ORANGE, PURPLE, CYAN]
```

### Jugador y Movimiento
- **Velocidades**: Ajusta `PLAYER_SPEED` y `RUN_SPEED`
- **Stamina**: Modifica tasas de regeneración y consumo
- **Rotación**: Cambia `TURN_SPEED`

### Visuales
- **Resolución**: Modifica `WINDOW_WIDTH` y `WINDOW_HEIGHT`
- **Campo de visión**: Ajusta `FOV`
- **Calidad de renderizado**: Cambia `NUM_RAYS`
- **Colores**: Personaliza todas las constantes de color

## Ideas para Futuras Mejoras

- **Texturas** en las paredes en lugar de colores sólidos
- **Múltiples niveles** con escaleras o teleportadores
- **Objetos coleccionables** dispersos por el mapa
- **Sonidos ambientales** y efectos de audio
- **Puertas** que se pueden abrir y cerrar
- **Iluminación dinámica** con antorchas o lámparas
- **Partículas** y efectos visuales atmosféricos
- **Sistema de guardado** de progreso

## Rendimiento

- El juego está optimizado para correr a **60 FPS** en hardware moderno bueno falta optimizarlo
- El número de rayos puede ajustarse para mejor rendimiento en hardware más lento
- La resolución puede reducirse para mejorar el framerate

¡Disfruta explorando el mundo 3D!
