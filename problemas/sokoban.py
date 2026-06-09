import streamlit as st
import heapq
import time

# --- DEFINICIÓN DEL ENTORNO ---
# El nivel se describe con texto. Cada carácter representa un elemento:
#   # = pared,  (espacio) = piso libre,  T = objetivo (Target),
#   B = caja (Box),  W = trabajador (Worker).
# Meta del juego: el trabajador debe empujar cada caja hasta quedar sobre un objetivo.
MAPA_NIVEL = [
    "########",
    "#      #",
    "#  T   #",
    "## B W #",
    "#  B T #",
    "#      #",
    "########"
]

# Emojis para dibujar cada elemento del mapa en pantalla.
ICONOS = {
    '#': "🧱",
    ' ': "⬛",
    'T': "🎯",
    'B': "📦",
    'W': "👷",
    'X': "✅"  # Caja colocada correctamente sobre un objetivo
}

def parsear_mapa(mapa):
    """Leer el mapa de texto y separar los elementos FIJOS (paredes y objetivos,
    que nunca se mueven) de los MÓVILES (cajas y trabajador). Cada posición se
    guarda como una pareja (x, y) = (columna, fila)."""
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

# --- BÚSQUEDA INFORMADA (A* y GBFS) ---
# "Informada" significa que el algoritmo usa una pista (heurística) que estima
# cuánto falta para resolver el nivel, y así explora primero las opciones que
# parecen más prometedoras en lugar de probar a ciegas.

def distancia_manhattan(p1, p2):
    """Calcular la distancia entre dos casillas contando pasos horizontales y
    verticales (sin diagonales), como moverse por las calles de una ciudad."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def heuristica(cajas, objetivos):
    """Estimar cuánto falta para ganar: sumar, por cada caja, la distancia al
    objetivo más cercano. Un valor bajo sugiere que el estado está cerca de la
    solución. No cuenta paredes ni empujones, por eso es solo una estimación."""
    total = 0
    for c in cajas:
        if objetivos:
            min_dist = min(distancia_manhattan(c, obj) for obj in objetivos)
            total += min_dist
    return total

def busqueda_informada(paredes, objetivos, inicio_trabajador, inicio_cajas, algoritmo="A*"):
    """Resolver el nivel probando movimientos y quedándose siempre con el estado
    más prometedor según la heurística. Diferencia entre los dos algoritmos:

    - A* (A-Estrella): ordena por f = g + h, donde g = pasos ya dados y
      h = estimación de lo que falta. Equilibra avanzar y acercarse, por lo que
      encuentra la solución MÁS CORTA.
    - GBFS (voraz): ordena solo por h (lo que falta). Suele ser más rápido,
      pero puede tomar caminos largos porque ignora los pasos ya dados.
    """
    # 'cola' es una cola de prioridad: siempre saca primero el estado más
    # prometedor. Cada elemento guarda:
    #   (prioridad, contador, g, trabajador, cajas, camino_trabajador, camino_cajas).
    # El 'contador' solo sirve para desempatar y evitar comparar estados directamente.
    cola = []
    contador = 0
    h_inicial = heuristica(inicio_cajas, objetivos)
    heapq.heappush(cola, (h_inicial, contador, 0, inicio_trabajador, inicio_cajas,
                          [inicio_trabajador], [inicio_cajas]))

    # 'visitados' recuerda los estados ya analizados para no repetir trabajo.
    # Un estado = posición del trabajador + posición de todas las cajas.
    visitados = set()
    visitados.add((inicio_trabajador, inicio_cajas))
    nodos_explorados = 0

    movimientos = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Arriba, abajo, izquierda, derecha

    while cola:
        # Sacar el estado más prometedor pendiente de explorar.
        _, _, g, trabajador, cajas, camino_w, camino_c = heapq.heappop(cola)
        nodos_explorados += 1

        # ¿Ganamos? Sucede cuando todas las cajas están sobre los objetivos.
        if set(cajas) == objetivos:
            return camino_w, camino_c, nodos_explorados

        wx, wy = trabajador

        # Probar las cuatro direcciones de movimiento del trabajador.
        for dx, dy in movimientos:
            nx, ny = wx + dx, wy + dy  # Casilla a la que intentaría moverse

            # Contra una pared no se puede avanzar.
            if (nx, ny) in paredes:
                continue

            nuevas_cajas = list(cajas)
            movimiento_valido = True

            # Si en esa casilla hay una caja, el trabajador intenta empujarla.
            if (nx, ny) in nuevas_cajas:
                idx_caja = nuevas_cajas.index((nx, ny))
                bx, by = nx + dx, ny + dy  # Casilla a la que iría la caja empujada

                # La caja no se puede empujar contra una pared u otra caja.
                if (bx, by) in paredes or (bx, by) in nuevas_cajas:
                    movimiento_valido = False
                else:
                    nuevas_cajas[idx_caja] = (bx, by)

            if movimiento_valido:
                nuevas_cajas_tupla = tuple(nuevas_cajas)
                estado = ((nx, ny), nuevas_cajas_tupla)

                # Si este estado es nuevo, calcular su prioridad y agregarlo a la cola.
                if estado not in visitados:
                    visitados.add(estado)
                    nuevo_g = g + 1  # Un paso más recorrido
                    h = heuristica(nuevas_cajas_tupla, objetivos)
                    # Aquí está la única diferencia entre los dos algoritmos:
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

    return None, None, nodos_explorados  # No hay solución posible

# --- INTERFAZ STREAMLIT ---

def renderizar_mapa(ancho, alto, paredes, objetivos, trabajador, cajas):
    """Construir el mapa como tabla HTML, dibujando en cada casilla el elemento
    que le corresponde (pared, caja, trabajador, objetivo o piso) con su color."""
    html = "<table style='border-collapse: collapse; margin-left: auto; margin-right: auto;'>"
    for y in range(alto):
        html += "<tr>"
        for x in range(ancho):
            pos = (x, y)
            # El orden de las comprobaciones define qué se dibuja si coinciden varios.
            if pos in paredes:
                contenido = ICONOS['#']
                color = "#424242"
            elif pos in cajas and pos in objetivos:
                contenido = ICONOS['X']   # Caja ya colocada en su objetivo
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

    # Leer el nivel y averiguar sus dimensiones.
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

        # Dibujar el nivel en su estado inicial antes de resolverlo.
        mapa_placeholder.markdown(renderizar_mapa(ancho, alto, paredes, objetivos, inicio_trabajador, inicio_cajas), unsafe_allow_html=True)

    if ejecutar:
        clave = "A*" if "A*" in algoritmo else "GBFS"
        info_placeholder.info(f"Ejecutando algoritmo {clave}...")

        # Calcular la secuencia de movimientos que resuelve el nivel.
        camino_w, camino_c, nodos = busqueda_informada(
            paredes, objetivos, inicio_trabajador, inicio_cajas, algoritmo=clave
        )

        if camino_w:
            # Recorrer la solución paso a paso, redibujando el mapa en cada movimiento.
            for paso in range(len(camino_w)):
                trabajador_actual = camino_w[paso]
                cajas_actuales = camino_c[paso]

                mapa_placeholder.markdown(
                    renderizar_mapa(ancho, alto, paredes, objetivos, trabajador_actual, cajas_actuales),
                    unsafe_allow_html=True
                )
                info_placeholder.success(f"Paso {paso}/{len(camino_w)-1} | Nodos evaluados en total por {clave}: {nodos}")
                time.sleep(velocidad)  # Pausar para que la animación sea visible

            info_placeholder.success(f"¡Nivel resuelto óptimamente en {len(camino_w)-1} movimientos!")
        else:
            info_placeholder.error("No se encontró una solución posible.")
