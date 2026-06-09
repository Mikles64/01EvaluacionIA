import streamlit as st
import time
from collections import deque

# --- DEFINICIÓN DEL ENTORNO ---
# El mapa es una cuadrícula de 4x4. Cada letra indica qué hay en esa casilla:
#   S = inicio (Start), F = hielo seguro (Frozen), H = agujero (Hole), G = meta (Goal).
# El objetivo es ir de S a G pisando solo hielo seguro, sin caer en un agujero.
MAPA_4x4 = [
    ['S', 'F', 'F', 'F'],
    ['F', 'H', 'F', 'H'],
    ['F', 'F', 'F', 'H'],
    ['H', 'F', 'F', 'G']
]

FILAS = len(MAPA_4x4)
COLUMNAS = len(MAPA_4x4[0])
INICIO = (0, 0)  # Posición (fila, columna) donde empieza el agente

# Emojis que representan cada casilla para que el mapa se vea más claro en pantalla.
ICONOS = {
    'S': "🧊",  # Inicio
    'F': "❄️",  # Hielo seguro
    'H': "🕳️",  # Agujero
    'G': "🎁",  # Meta
    'A': "🐧"   # Agente (pingüino)
}

# --- ALGORITMOS DE BÚSQUEDA NO INFORMADA ---
# "No informada" significa que el algoritmo no tiene pistas sobre dónde está la
# meta: explora el mapa a ciegas siguiendo una estrategia fija de orden.

def obtener_vecinos(x, y):
    """Devolver las casillas vecinas (derecha, abajo, izquierda, arriba) que
    siguen dentro del mapa. Sirve para saber a dónde se puede mover el agente."""
    movimientos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    vecinos = []
    for dx, dy in movimientos:
        nx, ny = x + dx, y + dy
        # Comprobar que la nueva casilla no se salga de los bordes del mapa.
        if 0 <= nx < FILAS and 0 <= ny < COLUMNAS:
            vecinos.append((nx, ny))
    return vecinos

def busqueda_bfs():
    """BFS (búsqueda en anchura): explorar el mapa por niveles, revisando primero
    las casillas más cercanas al inicio. Por eso siempre encuentra la ruta más
    corta. Usa una COLA: lo primero que entra es lo primero en salir (FIFO)."""
    # Cada elemento guarda la posición actual y el camino seguido hasta ella.
    cola = deque([(INICIO, [INICIO])])
    visitados = set([INICIO])  # Casillas ya vistas, para no repetirlas
    nodos_explorados = 0

    while cola:
        (x, y), camino = cola.popleft()  # Sacar el más antiguo (FIFO)
        nodos_explorados += 1

        # Si esta casilla es la meta, devolver el camino encontrado.
        if MAPA_4x4[x][y] == 'G':
            return camino, nodos_explorados

        # Agregar a la cola los vecinos seguros que aún no se hayan visitado.
        for nx, ny in obtener_vecinos(x, y):
            if (nx, ny) not in visitados and MAPA_4x4[nx][ny] != 'H':
                visitados.add((nx, ny))
                cola.append(((nx, ny), camino + [(nx, ny)]))

    return None, nodos_explorados  # No existe ruta posible

def busqueda_dfs():
    """DFS (búsqueda en profundidad): seguir un camino hasta el fondo antes de
    retroceder y probar otro. No garantiza la ruta más corta. Usa una PILA: lo
    último que entra es lo primero en salir (LIFO)."""
    # Cada elemento guarda la posición actual y el camino seguido hasta ella.
    pila = [(INICIO, [INICIO])]
    visitados = set([INICIO])
    nodos_explorados = 0

    while pila:
        (x, y), camino = pila.pop()  # Sacar el más reciente (LIFO)
        nodos_explorados += 1

        if MAPA_4x4[x][y] == 'G':
            return camino, nodos_explorados

        for nx, ny in obtener_vecinos(x, y):
            if (nx, ny) not in visitados and MAPA_4x4[nx][ny] != 'H':
                visitados.add((nx, ny))
                pila.append(((nx, ny), camino + [(nx, ny)]))

    return None, nodos_explorados

# --- INTERFAZ STREAMLIT ---

def renderizar_mapa(posicion_agente):
    """Construir el mapa como una tabla HTML, dibujando el pingüino en la
    posición indicada y cada casilla con su emoji y color de fondo."""
    html = "<table style='border-collapse: collapse; margin-left: auto; margin-right: auto;'>"
    for f in range(FILAS):
        html += "<tr>"
        for c in range(COLUMNAS):
            celda = MAPA_4x4[f][c]
            # Mostrar el agente si está en esta casilla; si no, el icono de la casilla.
            contenido = ICONOS['A'] if (f, c) == posicion_agente else ICONOS[celda]

            # Elegir el color de fondo según el tipo de casilla.
            color = "#E0F7FA" if celda in ['S', 'F'] else "#FFEBEE" if celda == 'H' else "#E8F5E9"

            html += f"<td style='width:60px; height:60px; background-color:{color}; text-align:center; font-size:30px; border: 1px solid #ccc;'>{contenido}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def mostrar_interfaz():
    st.subheader("Búsqueda No Informada: Frozen Lake")
    st.write("El pingüino 🐧 debe llegar al regalo 🎁 cruzando el hielo ❄️ sin caer en los agujeros 🕳️.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Configuración")
        algoritmo = st.radio("Selecciona el algoritmo:", ["BFS (Búsqueda a lo ancho)", "DFS (Búsqueda en profundidad)"])
        velocidad = st.slider("Velocidad de animación (segundos)", 0.1, 1.0, 0.4)

        ejecutar = st.button("Ejecutar Búsqueda", type="primary")

    with col2:
        st.write("### Visualización del Entorno")
        # Contenedores vacíos que se irán actualizando para animar la búsqueda.
        mapa_placeholder = st.empty()
        info_placeholder = st.empty()

        # Dibujar el mapa en su estado inicial.
        mapa_placeholder.markdown(renderizar_mapa(INICIO), unsafe_allow_html=True)

    if ejecutar:
        info_placeholder.info("Calculando ruta...")

        # Ejecutar el algoritmo elegido para obtener el camino hacia la meta.
        if "BFS" in algoritmo:
            camino, nodos = busqueda_bfs()
        else:
            camino, nodos = busqueda_dfs()

        if camino:
            # Recorrer el camino paso a paso, redibujando el mapa en cada posición.
            for paso, (px, py) in enumerate(camino):
                mapa_placeholder.markdown(renderizar_mapa((px, py)), unsafe_allow_html=True)
                info_placeholder.success(f"Paso {paso}/{len(camino)-1} | Nodos explorados en total: {nodos}")
                time.sleep(velocidad)  # Pausar para que la animación sea visible

            info_placeholder.success(f"¡Meta alcanzada en {len(camino)-1} pasos! (Algoritmo evaluó {nodos} nodos)")
        else:
            info_placeholder.error("No se encontró una ruta posible.")
