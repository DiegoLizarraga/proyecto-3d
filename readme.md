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

### Ajustar Rendimiento
- **Reducir niebla**: Modifica `GL_FOG_END` en `engine3d.py`
- **Resolución de graffiti**: Cambia `GRAFFITI_SIZE` en `settings.py`
- **FPS target**: Modifica `FPS` en `settings.py`

## 🐛 Solución de Problemas

### El juego no inicia
- Verifica que OpenGL esté instalado: `python -c "from OpenGL import GL"`
- Actualiza tus drivers de tarjeta gráfica
- Comprueba que tienes Python 3.8+

### Rendimiento bajo
- Reduce `GRAFFITI_SIZE` en `settings.py`
- Cierra otros programas que usen GPU
- Verifica que estés usando la tarjeta gráfica dedicada (no integrada)

### Mouse no responde bien
- Ajusta `MOUSE_SENSITIVITY` en `settings.py`
- Verifica que el juego tenga el foco de la ventana

### Graffitis no aparecen
- Asegúrate de estar cerca de la pared (dentro de `SPRAY_RANGE`)
- Presiona Z mientras miras directamente a la pared
- Verifica que la pared no esté en el límite del mapa

## 🚀 Mejoras Futuras

- [ ] **Texturas de imagen** cargadas desde archivos
- [ ] **Sistema de guardado** de graffitis entre sesiones
- [ ] **Multijugador** para colaborar en graffitis
- [ ] **Galería** de graffitis guardados
- [ ] **Más herramientas**: cubeta de relleno, texto, selección
- [ ] **Capas** en el editor de graffiti
- [ ] **Efectos de partículas** al pintar
- [ ] **Sonidos** ambientales y de spray
- [ ] **Enemigos IA** para añadir desafío
- [ ] **Múltiples niveles** con diferentes ambientes
- [ ] **Física de objetos** interactivos
- [ ] **Iluminación dinámica** avanzada con sombras

## 📝 Notas de Desarrollo

### Diferencias con el Sistema Raycasting Original
Este juego ha sido completamente reescrito desde un sistema de raycasting 2.5D (estilo Doom) a un motor 3D completo con OpenGL (estilo Half-Life):

**Antes (Raycasting):**
- Vista pseudo-3D generada por rayos
- Solo rotación 2D
- Paredes como sprites verticales
- Limitado a geometría ortogonal

**Ahora (OpenGL):**
- Geometría 3D verdadera
- Control de cámara FPS completo (horizontal)
- Paredes, suelos y techos como polígonos 3D
- Iluminación y efectos avanzados
- Mejor rendimiento con hardware moderno

### Arquitectura del Motor
El motor sigue un patrón de **Entity-Component-System simplificado**:
- `Player3D`: Entidad del jugador con física y controles
- `Camera`: Componente de vista 3D
- `Renderer3D`: Sistema de renderizado
- `UI3D`: Sistema de interfaz overlay

## 📜 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT. Siéntete libre de modificarlo, mejorarlo y compartirlo.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el juego:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/MiMejora`)
3. Commit tus cambios (`git commit -m 'Agrega MiMejora'`)
4. Push a la rama (`git push origin feature/MiMejora`)
5. Abre un Pull Request

## 👨‍💻 Créditos

Desarrollado con Python, Pygame y PyOpenGL.
Inspirado en los clásicos FPS de los 90s como Half-Life y Counter-Strike.

---

**¡Diviértete creando graffitis en el mundo 3D!** 🎨🎮