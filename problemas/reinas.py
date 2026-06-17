import streamlit as st
import numpy as np
import random
import math
from problemas import nerd, traza

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


def _diferencia(viejo, nuevo):
    """Indicar qué reina se movió entre dos estados (columna y nueva fila)."""
    for col in range(N):
        if viejo[col] != nuevo[col]:
            return col, nuevo[col]
    return None, None


def _entrada(estado, texto):
    """Crear un paso de la traza: el estado a dibujar y su descripción."""
    return {"estado": estado.copy(), "texto": texto}


# --- ALGORITMOS DE BÚSQUEDA LOCAL ---
# "Búsqueda local" significa partir de una solución cualquiera e ir mejorándola
# poco a poco con pequeños cambios, sin recorrer todo el espacio de soluciones.
# Cada algoritmo devuelve una TRAZA: la lista de pasos, con estado y explicación.

def escalada_simple(estado_inicial):
    """Escalada Simple: en cada paso, moverse al PRIMER vecino que mejore (que
    tenga menos conflictos). Si ningún vecino mejora, se queda atascada en un
    "óptimo local"."""
    estado = list(estado_inicial)
    actual = contar_conflictos(estado)
    traza = [_entrada(estado, f"INICIO · Escalada Simple\n\nEstado: filas={estado}\nConflictos (h) = {actual}\n\nObjetivo: reducir h hasta 0.")]
    it = 0

    while actual > 0:
        it += 1
        revisados = 0
        movido = False
        for vecino in generar_vecinos(estado):
            revisados += 1
            valor = contar_conflictos(vecino)
            if valor < actual:  # Primer vecino que mejora: tomarlo de inmediato
                col, fila = _diferencia(estado, vecino)
                texto = (
                    f"ITERACIÓN {it} · Escalada Simple\n\n"
                    f"h actual = {actual}\n"
                    f"Revisar vecinos en orden y tomar el PRIMERO que mejore...\n"
                    f"  Tras revisar {revisados} vecino(s):\n"
                    f"  Mover la reina de la columna {col} a la fila {fila}.\n"
                    f"  Nuevo h = {valor}  (mejora en {actual - valor})"
                )
                estado, actual = vecino, valor
                traza.append(_entrada(estado, texto))
                movido = True
                break
        if not movido:  # Ningún vecino mejora
            traza.append(_entrada(estado, (
                f"ITERACIÓN {it} · Escalada Simple\n\n"
                f"h actual = {actual}\n"
                f"Ningún vecino tiene menos conflictos.\n"
                f"ÓPTIMO LOCAL: el algoritmo se detiene sin resolver."
            )))
            break

    if actual == 0:
        traza.append(_entrada(estado, f"FIN · ¡Solución encontrada! h = 0\nEstado final: filas={estado}"))
    return traza


def escalada_horizontal(estado_inicial, prefijo="", max_laterales=100):
    """Escalada con Movimientos Horizontales (laterales): toma el MEJOR vecino;
    si no hay mejora pero existe uno igual, da un paso "de lado" para cruzar
    mesetas (zonas planas con el mismo número de conflictos)."""
    estado = list(estado_inicial)
    actual = contar_conflictos(estado)
    traza = [_entrada(estado, f"{prefijo}INICIO · Escalada Horizontal\n\nEstado: filas={estado}\nConflictos (h) = {actual}")]
    laterales = 0
    it = 0

    while actual > 0:
        it += 1
        vecino, valor = mejor_vecino(estado)
        col, fila = _diferencia(estado, vecino)
        cabecera = f"{prefijo}ITERACIÓN {it} · Escalada Horizontal\n\nh actual = {actual}\nMejor vecino posible: h = {valor} (mover reina col {col} → fila {fila})\n"
        if valor < actual:  # Hay mejora: avanzar
            estado, actual = vecino, valor
            laterales = 0
            traza.append(_entrada(estado, cabecera + f"Decisión: MEJORA, se acepta. Nuevo h = {valor}."))
        elif valor == actual and laterales < max_laterales:
            # Paso lateral para atravesar la meseta (mismo h).
            estado, actual = vecino, valor
            laterales += 1
            traza.append(_entrada(estado, cabecera + f"Decisión: MESETA (mismo h). Paso lateral #{laterales}."))
        else:
            traza.append(_entrada(estado, cabecera + "Decisión: sin mejora ni paso lateral. ÓPTIMO LOCAL, se detiene."))
            break

    if actual == 0:
        traza.append(_entrada(estado, f"{prefijo}FIN · ¡Solución encontrada! h = 0\nEstado final: filas={estado}"))
    return traza


def reinicio_aleatorio(max_reinicios=50):
    """Reinicio Aleatorio: ejecutar la escalada horizontal y, si se atasca sin
    resolver, volver a empezar desde un tablero aleatorio. La traza encadena
    todos los intentos hasta resolver o agotar los reinicios."""
    traza = []
    for intento in range(1, max_reinicios + 1):
        inicio = list(np.random.randint(0, N, N))
        sub = escalada_horizontal(inicio, prefijo=f"[Reinicio #{intento}] ")
        traza.extend(sub)
        if contar_conflictos(sub[-1]["estado"]) == 0:  # Resuelto en este intento
            break
    return traza


def recocido_simulado(estado_inicial, temp_inicial=30.0, enfriamiento=0.95, max_iter=2000):
    """Recocido Simulado: a veces acepta movimientos PEORES para escapar de
    óptimos locales. La probabilidad de aceptar algo peor es e^(-Δ/T); la
    temperatura T baja con el tiempo, así explora al inicio y afina al final.
    La traza registra los movimientos aceptados."""
    estado = list(estado_inicial)
    actual = contar_conflictos(estado)
    traza = [_entrada(estado, f"INICIO · Recocido Simulado\n\nEstado: filas={estado}\nConflictos (h) = {actual}\nTemperatura inicial T = {temp_inicial}")]
    temp = temp_inicial
    it = 0

    for _ in range(max_iter):
        if actual == 0:
            break
        it += 1
        temp = max(temp * enfriamiento, 1e-3)

        # Elegir un vecino al azar (mover una reina a otra fila de su columna).
        col = random.randint(0, N - 1)
        fila = random.randint(0, N - 1)
        while fila == estado[col]:
            fila = random.randint(0, N - 1)
        vecino = estado.copy()
        vecino[col] = fila
        valor = contar_conflictos(vecino)
        delta = valor - actual  # < 0 mejora ; > 0 empeora

        if delta < 0:
            estado, actual = vecino, valor
            traza.append(_entrada(estado, (
                f"ITERACIÓN {it} · Recocido Simulado\n\n"
                f"T = {temp:.2f}\n"
                f"Vecino al azar: reina col {col} → fila {fila}  (h = {valor})\n"
                f"Δ = {delta} (mejora) → se acepta siempre."
            )))
        else:
            prob = math.exp(-delta / temp)
            if random.random() < prob:  # Aceptar un movimiento peor
                estado, actual = vecino, valor
                traza.append(_entrada(estado, (
                    f"ITERACIÓN {it} · Recocido Simulado\n\n"
                    f"T = {temp:.2f}\n"
                    f"Vecino al azar: reina col {col} → fila {fila}  (h = {valor})\n"
                    f"Δ = +{delta} (peor). Probabilidad de aceptar = e^(-Δ/T) = {prob:.2%}\n"
                    f"Resultado del sorteo: ACEPTADO (escapa de un óptimo local)."
                )))
        # Los movimientos peores rechazados no cambian el estado y se omiten de la traza.

    if actual == 0:
        traza.append(_entrada(estado, f"FIN · ¡Solución encontrada! h = 0\nEstado final: filas={estado}"))
    else:
        traza.append(_entrada(estado, f"FIN · Se agotaron las iteraciones. Mejor h alcanzado = {actual}"))
    return traza


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
            key="rn_algoritmo",
        )

        # Crear un tablero de partida nuevo y aleatorio cuando se pulse el botón.
        if st.button("Generar Estado Inicial Aleatorio", key="rn_generar"):
            st.session_state.reinas_estado = list(np.random.randint(0, N, N))
            st.session_state.pop("rn_traza", None)

        ejecutar = st.button("Ejecutar Búsqueda", type="primary", key="rn_ejecutar")

    with col2:
        st.write("### Visualización del Tablero")
        placeholder_tablero = st.empty()

    # Generar un estado inicial la primera vez que se abre la pantalla.
    if "reinas_estado" not in st.session_state:
        st.session_state.reinas_estado = list(np.random.randint(0, N, N))

    # Al pulsar el botón, calcular la traza del algoritmo elegido.
    if ejecutar:
        estado_inicial = st.session_state.reinas_estado
        if algoritmo == "Escalada Simple":
            t = escalada_simple(estado_inicial)
        elif algoritmo == "Escalada Horizontal":
            t = escalada_horizontal(estado_inicial)
        elif algoritmo == "Recocido Simulado":
            t = recocido_simulado(estado_inicial)
        else:
            t = reinicio_aleatorio()
        st.session_state["rn_traza"] = t
        traza.nuevo_run("rn")

    t = st.session_state.get("rn_traza")
    if t:
        idx = traza.selector("rn", len(t))
        paso = t[idx]
        placeholder_tablero.markdown(renderizar_tablero(paso["estado"]), unsafe_allow_html=True)
        final = contar_conflictos(t[-1]["estado"])
        if final == 0:
            st.success(f"{nerd.CHECK} ¡Solución encontrada! · {len(t)} pasos registrados.")
        else:
            st.error(f"{nerd.ALERTA} Terminó con {final} conflictos (óptimo local). Prueba otro algoritmo o genera otro estado inicial.")
        traza.caja(paso["texto"])
    else:
        # Sin ejecución todavía: mostrar el tablero inicial actual.
        placeholder_tablero.markdown(renderizar_tablero(st.session_state.reinas_estado), unsafe_allow_html=True)
        st.info(f"Conflictos iniciales: {contar_conflictos(st.session_state.reinas_estado)}")
