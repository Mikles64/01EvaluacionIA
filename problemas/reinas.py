import streamlit as st
import numpy as np
import random
import math
import time

# --- LÓGICA DEL PROBLEMA DE LAS 8 REINAS ---
# Representación: un arreglo de 8 enteros.
#   El índice representa la COLUMNA y el valor representa la FILA de la reina.
# Esto garantiza que nunca haya dos reinas en la misma columna.

N = 8


def contar_conflictos(estado):
    """Heurística: número de pares de reinas que se atacan entre sí.
    Solo es necesario revisar filas y diagonales (las columnas son únicas)."""
    conflictos = 0
    for i in range(N):
        for j in range(i + 1, N):
            # Misma fila
            if estado[i] == estado[j]:
                conflictos += 1
            # Misma diagonal
            elif abs(estado[i] - estado[j]) == abs(i - j):
                conflictos += 1
    return conflictos


def generar_vecinos(estado):
    """Genera todos los estados vecinos moviendo una reina dentro de su columna."""
    vecinos = []
    for col in range(N):
        for fila in range(N):
            if fila != estado[col]:
                vecino = estado.copy()
                vecino[col] = fila
                vecinos.append(vecino)
    return vecinos


def mejor_vecino(estado):
    """Devuelve el vecino con menor número de conflictos (ascenso pronunciado)."""
    vecinos = generar_vecinos(estado)
    valores = [contar_conflictos(v) for v in vecinos]
    idx = int(np.argmin(valores))
    return vecinos[idx], valores[idx]


# --- ALGORITMOS DE BÚSQUEDA LOCAL ---

def escalada_simple(estado_inicial, max_iter=1000):
    """Escalada Simple: en cada paso se mueve al PRIMER vecino que mejore
    estrictamente el estado actual. Se detiene en un óptimo (local o global)."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]

    for _ in range(max_iter):
        if actual == 0:
            break
        encontrado = False
        for vecino in generar_vecinos(estado):
            valor = contar_conflictos(vecino)
            if valor < actual:  # Primer vecino que mejora
                estado, actual = vecino, valor
                historial.append((estado.copy(), actual))
                encontrado = True
                break
        if not encontrado:  # Óptimo local: ningún vecino mejora
            break
    return historial


def escalada_horizontal(estado_inicial, max_iter=1000, max_laterales=100):
    """Escalada con Movimientos Horizontales (laterales): permite desplazarse
    a vecinos con el MISMO valor para escapar de mesetas (plateaus)."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]
    laterales = 0

    for _ in range(max_iter):
        if actual == 0:
            break
        vecino, valor = mejor_vecino(estado)
        if valor < actual:
            estado, actual = vecino, valor
            laterales = 0
            historial.append((estado.copy(), actual))
        elif valor == actual and laterales < max_laterales:
            # Movimiento lateral para atravesar la meseta
            estado, actual = vecino, valor
            laterales += 1
            historial.append((estado.copy(), actual))
        else:
            break  # No hay mejora ni laterales disponibles
    return historial


def reinicio_aleatorio(max_reinicios=50, max_iter=1000):
    """Reinicio Aleatorio: ejecuta escalada repetidamente desde estados
    aleatorios hasta resolver el problema o agotar los reinicios."""
    historial_global = []
    for intento in range(max_reinicios):
        inicio = list(np.random.randint(0, N, N))
        historial = escalada_horizontal(inicio, max_iter)
        # Marcamos el reinicio en el historial global
        historial_global.append((intento + 1, historial))
        if historial[-1][1] == 0:  # Solución encontrada
            break
    return historial_global


def recocido_simulado(estado_inicial, temp_inicial=30.0, enfriamiento=0.95, max_iter=2000):
    """Recocido Simulado: acepta movimientos peores con probabilidad
    e^(-Δ/T) para escapar de óptimos locales. La temperatura T disminuye."""
    estado = estado_inicial.copy()
    actual = contar_conflictos(estado)
    historial = [(estado.copy(), actual)]
    temp = temp_inicial

    for _ in range(max_iter):
        if actual == 0:
            break
        temp = max(temp * enfriamiento, 1e-3)
        # Elegimos un vecino al azar
        col = random.randint(0, N - 1)
        fila = random.randint(0, N - 1)
        while fila == estado[col]:
            fila = random.randint(0, N - 1)
        vecino = estado.copy()
        vecino[col] = fila
        valor = contar_conflictos(vecino)

        delta = valor - actual
        if delta < 0 or random.random() < math.exp(-delta / temp):
            estado, actual = vecino, valor
            historial.append((estado.copy(), actual))
    return historial


# --- INTERFAZ STREAMLIT ---

def renderizar_tablero(estado):
    """Genera el HTML del tablero de ajedrez con las reinas colocadas."""
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
    """Anima un historial de (estado, conflictos)."""
    total = len(historial)
    for paso, (estado, conflictos) in enumerate(historial):
        placeholder_tablero.markdown(renderizar_tablero(estado), unsafe_allow_html=True)
        estado_txt = "✅ ¡Solución sin conflictos!" if conflictos == 0 else f"Conflictos: {conflictos}"
        placeholder_info.info(f"{prefijo}Paso {paso}/{total - 1} | {estado_txt}")
        time.sleep(velocidad)
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

        if st.button("Generar Estado Inicial Aleatorio"):
            st.session_state.reinas_estado = list(np.random.randint(0, N, N))

        ejecutar = st.button("Ejecutar Búsqueda", type="primary")

    with col2:
        st.write("### Visualización del Tablero")
        placeholder_tablero = st.empty()
        placeholder_info = st.empty()

        if "reinas_estado" not in st.session_state:
            st.session_state.reinas_estado = list(np.random.randint(0, N, N))

        # Render inicial
        placeholder_tablero.markdown(
            renderizar_tablero(st.session_state.reinas_estado), unsafe_allow_html=True
        )
        placeholder_info.info(
            f"Conflictos iniciales: {contar_conflictos(st.session_state.reinas_estado)}"
        )

    if ejecutar:
        estado_inicial = st.session_state.reinas_estado
        final = None

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
        else:  # Reinicio Aleatorio
            historial_global = reinicio_aleatorio()
            for intento, historial in historial_global:
                final = _animar(
                    historial, placeholder_tablero, placeholder_info, velocidad,
                    prefijo=f"🔄 Reinicio #{intento} | ",
                )
            st.session_state.reinas_estado = historial_global[-1][1][-1][0]

        # Mensaje final
        if final == 0:
            placeholder_info.success("✅ ¡Solución encontrada! Las 8 reinas están a salvo.")
            st.balloons()
        else:
            placeholder_info.error(
                f"⚠️ El algoritmo se detuvo en un óptimo local con {final} conflictos. "
                "Prueba otro algoritmo o genera un nuevo estado inicial."
            )
