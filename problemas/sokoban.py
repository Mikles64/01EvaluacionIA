import streamlit as st
import heapq
import time

# --- DEFINICIÓN DEL ENTORNO ---
# #: Pared, ' ': Espacio, T: Objetivo (Target), B: Caja (Box), W: Trabajador (Worker)
MAPA_NIVEL = [
    "########",
    "#      #",
    "#  T   #",
    "## B W #",
    "#  B T #",
    "#      #",
    "########"
]

ICONOS = {
    '#': "🧱",
    ' ': "⬛",
    'T': "🎯",
    'B': "📦",
    'W': "👷",
    'X': "✅" # Caja sobre el objetivo
}

def parsear_mapa(mapa):
    """Separa los elementos estáticos (paredes, objetivos) de los dinámicos (cajas, trabajador)."""
    paredes = set()
    objetivos = set()
    cajas = []
    trabajador = None
    
    for y, fila in enumerate(mapa):
        for x, char in enumerate(fila):
            if char == '#': paredes.add((x, y))
            elif char == 'T': objetivos.add((x, y))
            elif char == 'B': cajas.append((x, y))
            elif char == 'W': trabajador = (x, y)
            
    return paredes, objetivos, trabajador, tuple(cajas)

# --- ALGORITMO A* (BÚSQUEDA INFORMADA) ---

def distancia_manhattan(p1, p2):
    """Heurística: Distancia en cuadrícula entre dos puntos."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def heuristica(cajas, objetivos):
    """Calcula la distancia de cada caja a su objetivo más cercano."""
    total = 0
    for c in cajas:
        if objetivos:
            # Encuentra la distancia mínima al objetivo más cercano para esta caja
            min_dist = min(distancia_manhattan(c, obj) for obj in objetivos)
            total += min_dist
    return total

def busqueda_informada(paredes, objetivos, inicio_trabajador, inicio_cajas, algoritmo="A*"):
    """Búsqueda informada para resolver Sokoban.

    - A* (A-Estrella): prioriza f = g + h (coste real + heurística). Garantiza
      la solución óptima si la heurística es admisible.
    - GBFS (Greedy Best-First Search): prioriza únicamente h (solo la
      heurística). Suele ser más rápido pero NO garantiza el camino óptimo.
    """
    # Cola de prioridad: (prioridad, contador, g_score, trabajador, cajas, camino_w, camino_c)
    # El contador rompe empates y evita comparar tuplas no ordenables.
    cola = []
    contador = 0
    h_inicial = heuristica(inicio_cajas, objetivos)
    heapq.heappush(cola, (h_inicial, contador, 0, inicio_trabajador, inicio_cajas,
                          [inicio_trabajador], [inicio_cajas]))

    # Set para evitar ciclos (Estado = trabajador + cajas)
    visitados = set()
    visitados.add((inicio_trabajador, inicio_cajas))
    nodos_explorados = 0

    movimientos = [(0, -1), (0, 1), (-1, 0), (1, 0)] # Arriba, Abajo, Izquierda, Derecha

    while cola:
        _, _, g, trabajador, cajas, camino_w, camino_c = heapq.heappop(cola)
        nodos_explorados += 1

        # ¿Condición de victoria? (Todas las cajas están en los objetivos)
        if set(cajas) == objetivos:
            return camino_w, camino_c, nodos_explorados

        wx, wy = trabajador

        for dx, dy in movimientos:
            nx, ny = wx + dx, wy + dy # Nueva posición del trabajador

            # Si el trabajador choca con una pared, movimiento inválido
            if (nx, ny) in paredes:
                continue

            nuevas_cajas = list(cajas)
            movimiento_valido = True

            # Si el trabajador empuja una caja
            if (nx, ny) in nuevas_cajas:
                idx_caja = nuevas_cajas.index((nx, ny))
                bx, by = nx + dx, ny + dy # Nueva posición de la caja empujada

                # Si la caja choca con una pared o con otra caja, movimiento inválido
                if (bx, by) in paredes or (bx, by) in nuevas_cajas:
                    movimiento_valido = False
                else:
                    nuevas_cajas[idx_caja] = (bx, by)

            if movimiento_valido:
                nuevas_cajas_tupla = tuple(nuevas_cajas)
                estado = ((nx, ny), nuevas_cajas_tupla)

                if estado not in visitados:
                    visitados.add(estado)
                    nuevo_g = g + 1
                    h = heuristica(nuevas_cajas_tupla, objetivos)
                    # A* usa f = g + h ; GBFS usa solo h (voraz)
                    prioridad = (nuevo_g + h) if algoritmo == "A*" else h
                    contador += 1

                    heapq.heappush(cola, (
                        prioridad,
                        contador,
                        nuevo_g,
                        (nx, ny),
                        nuevas_cajas_tupla,
                        camino_w + [(nx, ny)],
                        camino_c + [nuevas_cajas_tupla]
                    ))

    return None, None, nodos_explorados

# --- INTERFAZ STREAMLIT ---

def renderizar_mapa(ancho, alto, paredes, objetivos, trabajador, cajas):
    """Genera el HTML del mapa combinando las posiciones actuales."""
    html = "<table style='border-collapse: collapse; margin-left: auto; margin-right: auto;'>"
    for y in range(alto):
        html += "<tr>"
        for x in range(ancho):
            pos = (x, y)
            if pos in paredes:
                contenido = ICONOS['#']
                color = "#424242"
            elif pos in cajas and pos in objetivos:
                contenido = ICONOS['X']
                color = "#81C784"
            elif pos in cajas:
                contenido = ICONOS['B']
                color = "#FFB74D"
            elif pos == trabajador:
                contenido = ICONOS['W']
                color = "#64B5F6"
            elif pos in objetivos:
                contenido = ICONOS['T']
                color = "#E0E0E0"
            else:
                contenido = ICONOS[' ']
                color = "#FAFAFA"
                
            html += f"<td style='width:60px; height:60px; background-color:{color}; text-align:center; font-size:30px; border: 1px solid #ccc;'>{contenido}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def mostrar_interfaz():
    st.subheader("Búsqueda Informada: Sokoban")
    st.write("La búsqueda informada utiliza heurísticas para guiar al trabajador 👷 a empujar las cajas 📦 hacia los objetivos 🎯.")

    paredes, objetivos, inicio_trabajador, inicio_cajas = parsear_mapa(MAPA_NIVEL)
    alto = len(MAPA_NIVEL)
    ancho = len(MAPA_NIVEL[0])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Configuración")
        algoritmo = st.radio(
            "Selecciona el algoritmo:",
            ["A* (A-Estrella)", "GBFS (Voraz)"],
        )
        st.write("**Heurística:** Distancia Manhattan (caja → objetivo más cercano)")
        if "A*" in algoritmo:
            st.caption("A* = g + h · Garantiza la solución óptima.")
        else:
            st.caption("GBFS = h · Más rápido, pero no garantiza optimalidad.")
        velocidad = st.slider("Velocidad de animación", 0.1, 1.0, 0.4)

        ejecutar = st.button("Resolver Nivel", type="primary")

    with col2:
        st.write("### Visualización del Entorno")
        mapa_placeholder = st.empty()
        info_placeholder = st.empty()
        
        # Renderizado inicial
        mapa_placeholder.markdown(renderizar_mapa(ancho, alto, paredes, objetivos, inicio_trabajador, inicio_cajas), unsafe_allow_html=True)

    if ejecutar:
        clave = "A*" if "A*" in algoritmo else "GBFS"
        info_placeholder.info(f"Ejecutando algoritmo {clave}...")

        camino_w, camino_c, nodos = busqueda_informada(
            paredes, objetivos, inicio_trabajador, inicio_cajas, algoritmo=clave
        )

        if camino_w:
            # Animación
            for paso in range(len(camino_w)):
                trabajador_actual = camino_w[paso]
                cajas_actuales = camino_c[paso]
                
                mapa_placeholder.markdown(
                    renderizar_mapa(ancho, alto, paredes, objetivos, trabajador_actual, cajas_actuales), 
                    unsafe_allow_html=True
                )
                info_placeholder.success(f"Paso {paso}/{len(camino_w)-1} | Nodos evaluados en total por {clave}: {nodos}")
                time.sleep(velocidad)
            
            info_placeholder.success(f"¡Nivel resuelto óptimamente en {len(camino_w)-1} movimientos!")
        else:
            info_placeholder.error("No se encontró una solución posible.")