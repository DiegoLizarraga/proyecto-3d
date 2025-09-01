# Videojuego 3D estilo Doom - Python

Un videojuego 3D simple inspirado en el primer Doom, creado con Python y Pygame usando técnicas de raycasting.

## Características

- Vista 3D en primera persona usando raycasting
- Movimiento fluido por un laberinto 3D
- Minimapa en tiempo real
- Detección de colisiones
- Controles similares a los FPS clásicos

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

- **W** o **Flecha Arriba**: Avanzar
- **S** o **Flecha Abajo**: Retroceder  
- **A** o **Flecha Izquierda**: Girar a la izquierda
- **D** o **Flecha Derecha**: Girar a la derecha
- **ESC**: Salir del juego

## Cómo funciona

El juego utiliza **raycasting**, la misma técnica que usaba el Doom original. Para cada columna de píxeles en la pantalla:

1. Se lanza un "rayo" desde la posición del jugador
2. Se calcula dónde el rayo intersecta con una pared
3. Se dibuja una línea vertical proporcional a la distancia (más cerca = más alta)
4. Se aplica sombreado basado en la distancia para dar profundidad

## Estructura del proyecto

- `main.py`: Archivo principal con toda la lógica del juego
- `requirements.txt`: Dependencias de Python necesarias
- `README.md`: Este archivo con las instrucciones

## Personalización

Puedes modificar fácilmente:

- **Mapa**: Edita la variable `WORLD_MAP` en `main.py`
- **Velocidad**: Cambia `PLAYER_SPEED` y `TURN_SPEED`
- **Resolución**: Modifica `WINDOW_WIDTH` y `WINDOW_HEIGHT`
- **Campo de visión**: Ajusta `FOV`
- **Colores**: Cambia los valores RGB en las constantes de color

## Posibles mejoras

- Texturas en las paredes
- Enemigos y objetos
- Sonidos
- Más niveles
- Armas y disparos
- Puertas y interacciones