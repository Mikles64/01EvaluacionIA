import streamlit as st
import numpy as np
import random
import math
import time

# --- LÓGICA DEL PROBLEMA DE LAS 8 REINAS ---
# Objetivo: colocar 8 reinas en un tablero de 8x8 sin que ninguna ataque a otra.
# Para simplificar, se usa una lista de 8 números:
#   la POSICIÓN en la lista es la COLUMNA y el VALOR guardado es la FILA.
# Ejemplo: estado[3] = 5 significa "en la columna 3 hay una reina en la fila 5".
# Así nunca puede haber dos reinas en la misma columna, y solo hay que vigilar
# las filas y las diagonales.

N = 8


def contar_conflictos(estado):
    """Contar cuántos pares de reinas se atacan entre sí. Este número es la
    "heurística": mide qué tan mala es una posición. El objetivo es llegar a 0
    (ninguna reina atacada). Solo se revisan filas y diagonales, porque las
    columnas ya son distintas por la forma de representar el tablero."""
    conflictos = 0
    for i in range(N):
        for j in range(i + 1, N):
            # Dos reinas se atacan si comparten fila...
            if estado[i] == estado[j]:
                conflictos += 1
            # ...o si están en la misma diagonal (igual distancia horizontal y vertical).
            elif abs(estado[i] - estado[j]) == abs(i - j):
                conflictos += 1
    return conflictos


def generar_vecinos(estado):
    """Generar todos los "vecinos" del estado actual. Un vecino es el tablero que
    resulta de mover UNA reina a otra fila dentro de su misma columna. Estas son
    las jugadas posibles que el algoritmo puede evaluar en cada paso."""
    vecinos = []
    for col in range(N):
        for fila in range(N):
            if fila != estado[col]:        # Mover la reina a una fila distinta
                vecino = estado.copy()
                vecino[col] = fila
                vecinos.append(vecino)
    return vecinos


def mejor_vecino(estado):
    """Devolver el vecino con MENOS conflictos de todos. Es decir, la mejor
    jugada posible en este paso (lo que se conoce como ascenso pronunciado)."""
    vecinos = generar_vecinos(estado)
    valores = [contar_conflictos(v) for v in vecinos]
    idx = int(np.argmin(valores))  # Índice del vecino con el valor más bajo
    return vecinos[idx], valores[idx]


# --- ALGORITMOS DE BÚSQUEDA LOCAL ---
# "Búsqueda local" significa partir de una solución cualquiera e ir mejorándola
# poco a poco con pequeños cambios, sin recorrer todo el espacio de soluciones.

def escalada_simple(estado_inicial, max_iter=1000):
    """Escalada Simple: en cada paso, moverse al PRIMER vecino que mejore (que
    tenga menos conflictos). Es rápida, pero si ningún vecino mejora se queda
    atascada en un "óptimo local" aunque no sea la solución perfecta.
    Devolver el historial de estados visitados para poder animarlo."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]

    for _ in range(max_iter):
        if actual == 0:                    # Conflictos = 0: solución encontrada
            break
        encontrado = False
        for vecino in generar_vecinos(estado):
            valor = contar_conflictos(vecino)
            if valor < actual:             # Primer vecino que mejora: tomarlo
                estado, actual = vecino, valor
                historial.append((estado.copy(), actual))
                encontrado = True
                break
        if not encontrado:                 # Ningún vecino mejora: quedarse atascado
            break
    return historial


def escalada_horizontal(estado_inicial, max_iter=1000, max_laterales=100):
    """Escalada con Movimientos Horizontales (laterales): como la escalada
    simple, pero cuando no hay ningún vecino mejor permite moverse a uno IGUAL.
    Esos pasos "de lado" ayudan a cruzar zonas planas (mesetas) donde varios
    estados tienen el mismo número de conflictos, y así encontrar más salidas."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]
    laterales = 0  # Cuántos pasos de lado seguidos se llevan, para no hacerlo infinito

    for _ in range(max_iter):
        if actual == 0:
            break
        vecino, valor = mejor_vecino(estado)
        if valor < actual:                 # Hay mejora: avanzar y reiniciar el contador
            estado, actual = vecino, valor
            laterales = 0
            historial.append((estado.copy(), actual))
        elif valor == actual and laterales < max_laterales:
            # Sin mejora pero hay un vecino igual: dar un paso lateral por la meseta.
            estado, actual = vecino, valor
            laterales += 1
            historial.append((estado.copy(), actual))
        else:
            break  # Ni mejora ni pasos laterales disponibles: detenerse
    return historial


def reinicio_aleatorio(max_reinicios=50, max_iter=1000):
    """Reinicio Aleatorio: ejecutar la escalada y, si se queda atascada sin
    resolver, volver a empezar desde un tablero nuevo al azar. Repetir hasta
    encontrar la solución o agotar los intentos. Probar varios puntos de
    partida hace mucho más probable hallar una solución perfecta."""
    historial_global = []
    for intento in range(max_reinicios):
        inicio = list(np.random.randint(0, N, N))   # Tablero inicial aleatorio
        historial = escalada_horizontal(inicio, max_iter)
        historial_global.append((intento + 1, historial))
        if historial[-1][1] == 0:          # El último estado tiene 0 conflictos
            break
    return historial_global


def recocido_simulado(estado_inicial, temp_inicial=30.0, enfriamiento=0.95, max_iter=2000):
    """Recocido Simulado: inspirado en cómo se enfría un metal. A veces acepta
    movimientos PEORES a propósito para escapar de óptimos locales. La
    probabilidad de aceptar algo peor depende de la "temperatura": al principio
    es alta (explora mucho) y va bajando (se vuelve más exigente). Fórmula de
    aceptación: e^(-diferencia / temperatura)."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]
    temp = temp_inicial

    for _ in range(max_iter):
        if actual == 0:
            break
        temp = max(temp * enfriamiento, 1e-3)  # Enfriar (nunca llega a cero exacto)

        # Elegir un vecino al azar moviendo una reina a otra fila de su columna.
        col = random.randint(0, N - 1)
        fila = random.randint(0, N - 1)
        while fila == estado[col]:
            fila = random.randint(0, N - 1)
        vecino = estado.copy()
        vecino[col] = fila
        valor = contar_conflictos(vecino)

        delta = valor - actual  # Negativo = el vecino es mejor; positivo = peor
        # Aceptar siempre si mejora; si empeora, aceptar solo con cierta probabilidad.
        if delta < 0 or random.random() < math.exp(-delta / temp):
            estado, actual = vecino, valor
            historial.append((estado.copy(), actual))
    return historial


# --- INTERFAZ STREAMLIT ---

def renderizar_tablero(estado):
    """Construir el tablero de ajedrez como tabla HTML, dibujando una reina (♛)
    en la fila correspondiente de cada columna y alternando los colores."""
    html = "<table style='border-collapse: collapse; margin-left:auto; margin-right:auto;'>"
    for fila in range(N):
        html += "<tr>"
        for col in range(N):
            color = "#F0D9B5" if (fila + col) % 2 == 0 else "#B58863"
            contenido = "♛" if estado[col] == fila else ""
            html += (
                f"<td style='width:48px; height:48px; background-color:{color}; "
                f"text-align:center; font-size:30px;'>{contenido}</td>"
            )
        html += "</tr>"
    html += "</table>"
    return html


def _animar(historial, placeholder_tablero, placeholder_info, velocidad, prefijo=""):
    """Mostrar uno a uno los estados del historial para ver cómo avanza la
    búsqueda. Devolver el número de conflictos del estado final."""
    total = len(historial)
    for paso, (estado, conflictos) in enumerate(historial):
        placeholder_tablero.markdown(renderizar_tablero(estado), unsafe_allow_html=True)
        estado_txt = "✅ ¡Solución sin conflictos!" if conflictos == 0 else f"Conflictos: {conflictos}"
        placeholder_info.info(f"{prefijo}Paso {paso}/{total - 1} | {estado_txt}")
        time.sleep(velocidad)  # Pausar para que la animación sea visible
    return historial[-1][1]


def mostrar_interfaz():
    st.subheader("Búsqueda Local: 8 Reinas")
    st.write(
        "Objetivo: colocar 8 reinas ♛ en un tablero de 8×8 sin que se ataquen "
        "(ninguna comparte fila, columna o diagonal). La **heurística** es el "
        "número de pares de reinas en conflicto; el objetivo es llegar a **0**."
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Configuración")
        algoritmo = st.selectbox(
            "Algoritmo de búsqueda local:",
            [
                "Escalada Simple",
                "Escalada Horizontal",
                "Reinicio Aleatorio",
                "Recocido Simulado",
            ],
        )
        velocidad = st.slider("Velocidad de animación (s)", 0.05, 1.0, 0.25)

        # Crear un tablero de partida nuevo y aleatorio cuando se pulse el botón.
        if st.button("Generar Estado Inicial Aleatorio"):
            st.session_state.reinas_estado = list(np.random.randint(0, N, N))

        ejecutar = st.button("Ejecutar Búsqueda", type="primary")

    with col2:
        st.write("### Visualización del Tablero")
        placeholder_tablero = st.empty()
        placeholder_info = st.empty()

        # Generar un estado inicial la primera vez que se abre la pantalla.
        if "reinas_estado" not in st.session_state:
            st.session_state.reinas_estado = list(np.random.randint(0, N, N))

        # Dibujar el tablero en su estado actual antes de buscar.
        placeholder_tablero.markdown(
            renderizar_tablero(st.session_state.reinas_estado), unsafe_allow_html=True
        )
        placeholder_info.info(
            f"Conflictos iniciales: {contar_conflictos(st.session_state.reinas_estado)}"
        )

    if ejecutar:
        estado_inicial = st.session_state.reinas_estado
        final = None

        # Ejecutar el algoritmo elegido y animar su recorrido paso a paso.
        if algoritmo == "Escalada Simple":
            historial = escalada_simple(estado_inicial)
            final = _animar(historial, placeholder_tablero, placeholder_info, velocidad)
            st.session_state.reinas_estado = historial[-1][0]
        elif algoritmo == "Escalada Horizontal":
            historial = escalada_horizontal(estado_inicial)
            final = _animar(historial, placeholder_tablero, placeholder_info, velocidad)
            st.session_state.reinas_estado = historial[-1][0]
        elif algoritmo == "Recocido Simulado":
            historial = recocido_simulado(estado_inicial)
            final = _animar(historial, placeholder_tablero, placeholder_info, velocidad)
            st.session_state.reinas_estado = historial[-1][0]
        else:  # Reinicio Aleatorio: animar cada intento, indicando el número de reinicio.
            historial_global = reinicio_aleatorio()
            for intento, historial in historial_global:
                final = _animar(
                    historial, placeholder_tablero, placeholder_info, velocidad,
                    prefijo=f"🔄 Reinicio #{intento} | ",
                )
            st.session_state.reinas_estado = historial_global[-1][1][-1][0]

        # Informar el resultado final: solución encontrada o atasco en óptimo local.
        if final == 0:
            placeholder_info.success("✅ ¡Solución encontrada! Las 8 reinas están a salvo.")
            st.balloons()
        else:
            placeholder_info.error(
                f"⚠️ El algoritmo se detuvo en un óptimo local con {final} conflictos. "
                "Prueba otro algoritmo o genera un nuevo estado inicial."
            )
