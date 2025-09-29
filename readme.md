# Videojuego 3D de Exploración - Python
<img width="1920" height="1080" alt="Komi_San_Maid_Outfit_Python" src="https://github.com/user-attachments/assets/7abf11c5-5c84-46af-b099-4163431b21e1" />


Un videojuego 3D mejorado inspirado en el primer Doom, creado con Python y Pygame usando técnicas de raycasting. Versión expandida con mapa más grande y sistema de stamina para correr.


## Características

- **Vista 3D en primera persona** usando raycasting avanzado
- **Mapa expansivo** de 20x20 con múltiples áreas para explorar
- **Sistema de movimiento mejorado** con capacidad de correr y movimiento lateral
- **Sistema de stamina** que limita el tiempo de carrera
- **Diferentes tipos de paredes** con colores distintivos
- **Minimapa detallado** en tiempo real con colores diferenciados
- **Interfaz de usuario** con barra de stamina e indicadores de estado
- **Detección de colisiones** suave y precisa
- **Efectos visuales** mejorados con gradientes en cielo y suelo

## Requisitos

- Python 3.7 o superior
- Pygame 2.5.2

## Instalación

1. **Clona o descarga los archivos del proyecto**

2. **Instala Pygame usando pip:**
   ```bash
   pip install -r requirements.txt
   ```
   
   O directamente:
   ```bash
   pip install pygame
   ```

3. **Ejecuta el juego:**
   ```bash
   python main.py
   ```

## Controles

### Movimiento Básico
- **W** o **Flecha Arriba**: Avanzar
- **S** o **Flecha Abajo**: Retroceder  
- **A** o **Flecha Izquierda**: Girar a la izquierda
- **D** o **Flecha Derecha**: Girar a la derecha

### Movimiento Avanzado
- **Q**: Moverse lateralmente a la izquierda (strafing)
- **E**: Moverse lateralmente a la derecha (strafing)
- **SHIFT** (mantener): Correr (consume stamina)

### Otros
- **ESC**: Salir del juego

## Nuevas Características

### Sistema de Stamina
- **Barra de stamina** visible en la esquina inferior derecha
- **Regeneración automática** cuando no estás corriendo
- **Indicador visual** de estado (caminando/corriendo)
- **Colores de alerta** cuando la stamina está baja

### Mapa Expandido
- **Tamaño 20x20** con múltiples salas y pasillos
- **Dos tipos de paredes**: básicas (grises) y especiales (marrones)
- **Diseño laberíntico** con múltiples rutas de exploración
- **Salas interconectadas** para una experiencia de exploración rica

### Mejoras Visuales
- **Gradientes** en cielo y suelo para mayor realismo
- **Sombreado mejorado** basado en distancia
- **Colores diferenciados** para tipos de pared
- **Minimapa detallado** con código de colores

## Cómo funciona

El juego utiliza **raycasting**, la misma técnica que usaba el Doom original, pero con mejoras:

1. **Para cada columna de píxeles** en la pantalla se lanza un "rayo"
2. **Se detecta el tipo de pared** que intersecta el rayo
3. **Se calcula la distancia** y se aplica corrección de "ojo de pez"
4. **Se dibuja una línea vertical** proporcional a la distancia
5. **Se aplican efectos visuales** como sombreado y colores específicos

## Estructura del proyecto

- `main.py`: Archivo principal con toda la lógica del juego mejorado
- `requirements.txt`: Dependencias de Python necesarias
- `README.md`: Este archivo con las instrucciones actualizadas

## Personalización

Puedes modificar fácilmente:

### Mapa y Mundo
- **Mapa**: Edita la variable `WORLD_MAP` en `main.py`
- **Colores de paredes**: Modifica el diccionario `WALL_COLORS`
- **Tamaño de tiles**: Cambia `TILE_SIZE`

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
