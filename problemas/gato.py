import streamlit as st
import math
from problemas import nerd

# --- LÓGICA DE MINIMAX ---
# El tablero se representa como una lista de 9 casillas (índices 0 a 8), donde
# cada casilla contiene "X", "O" o " " (vacía). Posiciones en el tablero:
#   0 | 1 | 2
#   3 | 4 | 5
#   6 | 7 | 8

def verificar_ganador(tablero):
    """Revisar si la partida ya terminó. Devolver "X" u "O" si alguien completó
    una línea, "Empate" si el tablero está lleno sin ganador, o None si el
    juego sigue en curso."""
    # Las 8 combinaciones de tres casillas que forman una línea ganadora.
    lineas = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
        [0, 4, 8], [2, 4, 6]              # Diagonales
    ]
    # Si las tres casillas de una línea son iguales y no están vacías, hay ganador.
    for linea in lineas:
        if tablero[linea[0]] == tablero[linea[1]] == tablero[linea[2]] and tablero[linea[0]] != " ":
            return tablero[linea[0]]
    if " " not in tablero:
        return "Empate"
    return None

def minimax(tablero, profundidad, es_maximizador):
    """Calcular qué tan buena es una jugada explorando TODAS las partidas
    posibles a partir de ella. La IA (O) intenta MAXIMIZAR el puntaje y supone
    que el rival (X) intenta MINIMIZARLO. La 'profundidad' (cuántas jugadas
    faltaron) hace que la IA prefiera ganar pronto y perder lo más tarde posible.
    Es una función recursiva: se llama a sí misma para simular cada turno."""
    ganador = verificar_ganador(tablero)
    # Casos finales: asignar un puntaje según quién gane (o empate).
    if ganador == "O": return 10 - profundidad   # Bueno para la IA
    if ganador == "X": return profundidad - 10   # Malo para la IA
    if ganador == "Empate": return 0

    if es_maximizador:
        # Turno de la IA (O): buscar el puntaje MÁS ALTO entre las jugadas posibles.
        mejor_puntaje = -math.inf
        for i in range(9):
            if tablero[i] == " ":          # Probar cada casilla libre...
                tablero[i] = "O"
                puntaje = minimax(tablero, profundidad + 1, False)
                tablero[i] = " "           # ...y deshacer la prueba.
                mejor_puntaje = max(puntaje, mejor_puntaje)
        return mejor_puntaje
    else:
        # Turno del jugador (X): suponer que elige el puntaje MÁS BAJO para la IA.
        mejor_puntaje = math.inf
        for i in range(9):
            if tablero[i] == " ":
                tablero[i] = "X"
                puntaje = minimax(tablero, profundidad + 1, True)
                tablero[i] = " "
                mejor_puntaje = min(puntaje, mejor_puntaje)
        return mejor_puntaje

def mejor_movimiento(tablero):
    """Decidir la mejor casilla para la IA: probar cada casilla libre, evaluarla
    con minimax y quedarse con la de mayor puntaje."""
    mejor_puntaje = -math.inf
    movimiento = None
    for i in range(9):
        if tablero[i] == " ":
            tablero[i] = "O"  # La IA juega como 'O'
            puntaje = minimax(tablero, 0, False)
            tablero[i] = " "  # Deshacer la prueba para no alterar el tablero real
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                movimiento = i
    return movimiento

# --- INTERFAZ STREAMLIT ---
def mostrar_interfaz():
    st.subheader("Búsqueda Adversaria: Minimax (Gato)")
    st.write(
        "Juegas como **X**. La IA juega como **O** con el algoritmo **Minimax**, "
        "que alterna nodos **MAX** (la IA maximiza su puntaje) y nodos **MIN** "
        "(asume que tú minimizas su puntaje) para explorar todos los estados "
        "futuros y elegir la jugada óptima."
    )
    st.info(
        f"{nerd.IDEA} **MAX** = turno de la IA (O) · **MIN** = turno del jugador (X). "
        "La IA es imbatible: lo mejor que puedes lograr es un empate."
    )

    # 'session_state' guarda los datos entre clics para que el juego no se reinicie.
    if 'tablero_gato' not in st.session_state:
        st.session_state.tablero_gato = [" "] * 9
        st.session_state.ganador_gato = None

    def jugar(idx):
        """Procesar el clic del jugador en la casilla 'idx' y responder con la IA."""
        if st.session_state.tablero_gato[idx] == " " and not st.session_state.ganador_gato:
            # Turno del jugador: colocar la X y revisar si ya ganó.
            st.session_state.tablero_gato[idx] = "X"
            st.session_state.ganador_gato = verificar_ganador(st.session_state.tablero_gato)

            # Turno de la IA: calcular su mejor jugada y colocarla.
            if not st.session_state.ganador_gato:
                mov = mejor_movimiento(st.session_state.tablero_gato)
                if mov is not None:
                    st.session_state.tablero_gato[mov] = "O"
                    st.session_state.ganador_gato = verificar_ganador(st.session_state.tablero_gato)

    # Dibujar el tablero como una cuadrícula de botones (3 columnas + espacio a la derecha).
    cols = st.columns([1, 1, 1, 3])

    for i in range(9):
        with cols[i % 3]:  # Repartir las 9 casillas en las 3 primeras columnas
            # Cada casilla es un botón; al pulsarlo se ejecuta 'jugar' con su índice.
            st.button(
                st.session_state.tablero_gato[i] if st.session_state.tablero_gato[i] != " " else "  ",
                key=f"btn_{i}",
                on_click=jugar,
                args=(i,),
                use_container_width=True
            )

    # Mostrar el resultado cuando la partida termina y ofrecer reiniciar.
    if st.session_state.ganador_gato:
        if st.session_state.ganador_gato == "Empate":
            st.warning("¡Es un empate!")
        else:
            st.success(f"Ganador: {st.session_state.ganador_gato}")

        if st.button("Reiniciar Juego", key="gato_reiniciar"):
            st.session_state.tablero_gato = [" "] * 9
            st.session_state.ganador_gato = None
            st.rerun()
