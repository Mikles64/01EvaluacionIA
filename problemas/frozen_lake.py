import streamlit as st
from collections import deque
from problemas import nerd, traza

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

# Iconos (Nerd Font) que representan cada casilla para que el mapa se vea claro.
ICONOS = {
    'S': nerd.INICIO,   # Inicio
    'F': nerd.HIELO,    # Hielo seguro
    'H': nerd.AGUJERO,  # Agujero
    'G': nerd.META,     # Meta
    'A': nerd.AGENTE    # Agente
}


# --- HERRAMIENTAS PARA DESCRIBIR LA TRAZA ---

def _fmt(posiciones):
    """Formatear una colección de posiciones como texto legible."""
    posiciones = list(posiciones)
    if not posiciones:
        return "(vacío)"
    return ", ".join(f"({x},{y})" for x, y in posiciones)


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


def buscar(modo):
    """Ejecutar BFS o DFS guardando una TRAZA de cada iteración.

    - BFS usa una COLA (FIFO): saca primero el nodo más antiguo de OPEN.
    - DFS usa una PILA (LIFO): saca primero el nodo más reciente de OPEN.

    OPEN = frontera (nodos por explorar). CLOSED = visitados (ya procesados).
    Devolver (camino, traza). Cada paso de la traza incluye la posición actual,
    los conjuntos OPEN/CLOSED para dibujarlos y un texto explicativo.
    """
    es_bfs = (modo == "BFS")
    # La frontera (OPEN) guarda parejas (posición, camino hasta ella).
    frontera = deque([(INICIO, [INICIO])])
    visitados = set([INICIO])  # CLOSED: casillas ya vistas, para no repetirlas
    traza = []
    camino_final = None
    it = 0

    while frontera:
        it += 1
        # Sacar el siguiente nodo según la estrategia (FIFO en BFS, LIFO en DFS).
        if es_bfs:
            (x, y), camino = frontera.popleft()   # Más antiguo
        else:
            (x, y), camino = frontera.pop()       # Más reciente

        es_meta = MAPA_4x4[x][y] == 'G'
        nuevos = []

        # Si no es la meta, generar y agregar los vecinos válidos a la frontera.
        if not es_meta:
            for nx, ny in obtener_vecinos(x, y):
                if (nx, ny) not in visitados and MAPA_4x4[nx][ny] != 'H':
                    visitados.add((nx, ny))
                    frontera.append(((nx, ny), camino + [(nx, ny)]))
                    nuevos.append((nx, ny))

        # Posiciones que quedan en OPEN tras esta iteración (para dibujar/describir).
        open_pos = [p for p, _ in frontera]

        # Construir el texto explicativo de esta iteración.
        estructura = "COLA (FIFO)" if es_bfs else "PILA (LIFO)"
        extremo = "frente → fondo" if es_bfs else "cima → fondo"
        open_ordenada = open_pos if es_bfs else list(reversed(open_pos))
        lineas = [
            f"ITERACIÓN {it}  ·  {modo}",
            "",
            f"Nodo extraído de OPEN: ({x},{y})  [casilla '{MAPA_4x4[x][y]}']",
            f"¿Es la meta?: {'SÍ' if es_meta else 'no'}",
        ]
        if not es_meta:
            if nuevos:
                lineas.append(f"Vecinos válidos añadidos a OPEN: {_fmt(nuevos)}")
            else:
                lineas.append("Vecinos válidos añadidos a OPEN: (ninguno nuevo)")
        lineas += [
            "",
            f"OPEN  ({estructura}, {extremo}): {_fmt(open_ordenada)}",
            f"CLOSED (visitados): {_fmt(sorted(visitados))}",
        ]
        if es_meta:
            lineas += [
                "",
                f"¡META encontrada! Camino de {len(camino) - 1} pasos:",
                _fmt(camino),
            ]

        traza.append({
            "pos": (x, y),
            "visitados": set(visitados),
            "frontera": set(open_pos),
            "camino": set(camino) if es_meta else set(),
            "texto": "\n".join(lineas),
        })

        if es_meta:
            camino_final = camino
            break

    return camino_final, traza


# --- INTERFAZ STREAMLIT ---

def renderizar_mapa(posicion_agente, visitados=frozenset(), frontera=frozenset(), camino=frozenset()):
    """Construir el mapa como tabla HTML. Además del agente, resaltar las
    casillas de CLOSED (visitados), de OPEN (frontera) y del camino final."""
    html = "<table style='border-collapse: collapse; margin-left: auto; margin-right: auto;'>"
    for f in range(FILAS):
        html += "<tr>"
        for c in range(COLUMNAS):
            celda = MAPA_4x4[f][c]
            pos = (f, c)
            # Mostrar el agente si está en esta casilla; si no, el icono de la casilla.
            glifo = ICONOS['A'] if pos == posicion_agente else ICONOS[celda]
            contenido = nerd.icono(glifo)

            # Color base según el tipo de casilla.
            color = "#E0F7FA" if celda in ['S', 'F'] else "#FFEBEE" if celda == 'H' else "#E8F5E9"
            # Resaltados (de menor a mayor prioridad visual).
            if pos in camino:
                color = "#C8E6C9"   # Camino final: verde
            elif pos in visitados:
                color = "#ECEFF1"   # CLOSED: gris
            if pos in frontera:
                color = "#FFF59D"   # OPEN: amarillo
            borde = "3px solid #1976D2" if pos == posicion_agente else "1px solid #ccc"

            html += f"<td style='width:60px; height:60px; background-color:{color}; text-align:center; border:{borde};'>{contenido}</td>"
        html += "</tr>"
    html += "</table>"
    return html


def mostrar_interfaz():
    st.subheader("Búsqueda No Informada: Frozen Lake")
    st.write("El agente debe llegar a la meta cruzando el hielo seguro sin caer en los agujeros.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Configuración")
        algoritmo = st.radio(
            "Selecciona el algoritmo:",
            ["BFS (Búsqueda a lo ancho)", "DFS (Búsqueda en profundidad)"],
            key="fl_algoritmo",
        )
        st.caption("Amarillo = OPEN (frontera) · Gris = CLOSED (visitados) · "
                   "Verde = camino final · Borde azul = nodo actual.")
        ejecutar = st.button("Ejecutar Búsqueda", type="primary", key="fl_ejecutar")

    with col2:
        st.write("### Visualización del Entorno")
        mapa_placeholder = st.empty()

    # Al pulsar el botón, calcular la traza y guardarla para recorrerla luego.
    if ejecutar:
        modo = "BFS" if "BFS" in algoritmo else "DFS"
        camino, t = buscar(modo)
        st.session_state["fl_traza"] = t
        st.session_state["fl_camino"] = camino
        traza.nuevo_run("fl")

    t = st.session_state.get("fl_traza")
    if t:
        # Control para recorrer la traza iteración por iteración.
        idx = traza.selector("fl", len(t))
        paso = t[idx]
        # Dibujar el mapa correspondiente a la iteración seleccionada.
        mapa_placeholder.markdown(
            renderizar_mapa(paso["pos"], paso["visitados"], paso["frontera"], paso["camino"]),
            unsafe_allow_html=True,
        )
        camino = st.session_state.get("fl_camino")
        if camino:
            st.success(f"Solución encontrada: {len(camino) - 1} pasos · {len(t)} iteraciones (nodos expandidos).")
        else:
            st.error("No se encontró una ruta posible.")
        traza.caja(paso["texto"])
    else:
        # Sin ejecución todavía: mostrar el mapa en su estado inicial.
        mapa_placeholder.markdown(renderizar_mapa(INICIO), unsafe_allow_html=True)
