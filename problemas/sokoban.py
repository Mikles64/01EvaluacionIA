import streamlit as st
import heapq
from problemas import nerd, traza

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

# Iconos (Nerd Font) para dibujar cada elemento del mapa en pantalla.
ICONOS = {
    '#': nerd.PARED,
    ' ': "",            # Piso libre: sin icono
    'T': nerd.OBJETIVO,
    'B': nerd.CAJA,
    'W': nerd.TRABAJADOR,
    'X': nerd.CHECK     # Caja colocada correctamente sobre un objetivo
}

# Nombres de las cuatro direcciones, para describir los movimientos en la traza.
DIRECCIONES = [((0, -1), "arriba"), ((0, 1), "abajo"), ((-1, 0), "izquierda"), ((1, 0), "derecha")]


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
    """Resolver el nivel guardando una TRAZA de cada iteración. Diferencia entre
    los dos algoritmos:

    - A* (A-Estrella): ordena OPEN por f = g + h (g = pasos dados, h = lo que
      falta). Encuentra la solución MÁS CORTA.
    - GBFS (voraz): ordena OPEN solo por h. Suele ser más rápido, pero no
      garantiza la solución más corta.

    Devolver (camino_trabajador, camino_cajas, traza).
    """
    es_estrella = (algoritmo == "A*")
    etiqueta = "f = g + h" if es_estrella else "h"

    # OPEN es una cola de prioridad (heap). Cada elemento guarda:
    #   (prioridad, contador, g, trabajador, cajas, camino_w, camino_c).
    # El 'contador' desempata y evita comparar estados directamente.
    cola = []
    contador = 0
    h_inicial = heuristica(inicio_cajas, objetivos)
    heapq.heappush(cola, (h_inicial, contador, 0, inicio_trabajador, inicio_cajas,
                          [inicio_trabajador], [inicio_cajas]))

    # CLOSED: estados ya analizados (estado = trabajador + posición de las cajas).
    visitados = set([(inicio_trabajador, inicio_cajas)])
    traza = []
    it = 0

    while cola:
        it += 1
        prioridad, _, g, trabajador, cajas, camino_w, camino_c = heapq.heappop(cola)
        h = heuristica(cajas, objetivos)
        es_meta = set(cajas) == objetivos
        wx, wy = trabajador

        # Generar los sucesores y, de paso, describir cada intento de movimiento.
        sucesores = []
        if not es_meta:
            for (dx, dy), nombre in DIRECCIONES:
                nx, ny = wx + dx, wy + dy
                if (nx, ny) in paredes:
                    sucesores.append(f"  {nombre:9}→ pared, inválido")
                    continue

                nuevas_cajas = list(cajas)
                empuje = ""
                valido = True
                if (nx, ny) in nuevas_cajas:
                    idx_caja = nuevas_cajas.index((nx, ny))
                    bx, by = nx + dx, ny + dy
                    if (bx, by) in paredes or (bx, by) in nuevas_cajas:
                        valido = False
                    else:
                        nuevas_cajas[idx_caja] = (bx, by)
                        empuje = f" [empuja caja a ({bx},{by})]"

                if not valido:
                    sucesores.append(f"  {nombre:9}→ caja bloqueada, inválido")
                    continue

                cajas_t = tuple(nuevas_cajas)
                estado = ((nx, ny), cajas_t)
                if estado in visitados:
                    sucesores.append(f"  {nombre:9}→ ({nx},{ny}){empuje} · ya visitado")
                    continue

                visitados.add(estado)
                nuevo_g = g + 1
                nuevo_h = heuristica(cajas_t, objetivos)
                prio = (nuevo_g + nuevo_h) if es_estrella else nuevo_h
                contador += 1
                heapq.heappush(cola, (prio, contador, nuevo_g, (nx, ny), cajas_t,
                                      camino_w + [(nx, ny)], camino_c + [cajas_t]))
                detalle = f"g={nuevo_g} h={nuevo_h} f={nuevo_g + nuevo_h}" if es_estrella else f"h={nuevo_h}"
                sucesores.append(f"  {nombre:9}→ ({nx},{ny}){empuje} · {detalle} · NUEVO en OPEN")

        # Resumen de OPEN tras esta iteración (los de menor prioridad primero).
        mejores = heapq.nsmallest(5, cola)
        resumen_open = "; ".join(f"{etiqueta.split('=')[0].strip()}={t[0]}@{t[3]}" for t in mejores)

        # Construir el texto explicativo de la iteración.
        lineas = [
            f"ITERACIÓN {it}  ·  {algoritmo}  (OPEN ordenada por {etiqueta})",
            "",
            f"Nodo extraído de OPEN (mejor prioridad): trabajador={trabajador}",
            f"  g={g} (pasos dados)   h={h} (estimación)   f=g+h={g + h}",
            f"  cajas={list(cajas)}",
            f"¿Todas las cajas en objetivo?: {'SÍ' if es_meta else 'no'}",
        ]
        if not es_meta:
            lineas.append("Sucesores (movimientos del trabajador):")
            lineas += sucesores
        lineas += [
            "",
            f"OPEN: {len(cola)} estados. Menores: {resumen_open if resumen_open else '(vacío)'}",
            f"CLOSED: {len(visitados)} estados",
        ]
        if es_meta:
            lineas += ["", f"¡NIVEL RESUELTO en {len(camino_w) - 1} movimientos!"]

        traza.append({"trabajador": trabajador, "cajas": cajas, "texto": "\n".join(lineas)})

        if es_meta:
            return camino_w, camino_c, traza

    return None, None, traza  # No hay solución posible

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

            html += f"<td style='width:60px; height:60px; background-color:{color}; text-align:center; border: 1px solid #ccc;'>{nerd.icono(contenido)}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def mostrar_interfaz():
    st.subheader("Búsqueda Informada: Sokoban")
    st.write("La búsqueda informada utiliza heurísticas para guiar al trabajador a empujar las cajas hacia los objetivos.")

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
            key="sk_algoritmo",
        )
        st.write("**Heurística:** Distancia Manhattan (caja → objetivo más cercano)")
        if "A*" in algoritmo:
            st.caption("A* = g + h · Garantiza la solución óptima.")
        else:
            st.caption("GBFS = h · Más rápido, pero no garantiza optimalidad.")

        ejecutar = st.button("Resolver Nivel", type="primary", key="sk_ejecutar")

    with col2:
        st.write("### Visualización del Entorno")
        mapa_placeholder = st.empty()

    # Al pulsar el botón, calcular la traza completa y guardarla.
    if ejecutar:
        clave = "A*" if "A*" in algoritmo else "GBFS"
        camino_w, camino_c, t = busqueda_informada(
            paredes, objetivos, inicio_trabajador, inicio_cajas, algoritmo=clave
        )
        st.session_state["sk_traza"] = t
        st.session_state["sk_camino"] = camino_w
        traza.nuevo_run("sk")

    t = st.session_state.get("sk_traza")
    if t:
        idx = traza.selector("sk", len(t))
        paso = t[idx]
        # Dibujar el estado del nodo expandido en esta iteración.
        mapa_placeholder.markdown(
            renderizar_mapa(ancho, alto, paredes, objetivos, paso["trabajador"], paso["cajas"]),
            unsafe_allow_html=True,
        )
        camino = st.session_state.get("sk_camino")
        if camino:
            st.success(f"Nivel resuelto en {len(camino) - 1} movimientos · {len(t)} iteraciones (nodos expandidos).")
        else:
            st.error("No se encontró una solución posible.")
        traza.caja(paso["texto"])
    else:
        # Sin ejecución todavía: mostrar el nivel en su estado inicial.
        mapa_placeholder.markdown(
            renderizar_mapa(ancho, alto, paredes, objetivos, inicio_trabajador, inicio_cajas),
            unsafe_allow_html=True,
        )
