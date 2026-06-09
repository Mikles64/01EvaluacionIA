import streamlit as st
import math

# --- LÓGICA DE MINIMAX ---
def verificar_ganador(tablero):
    lineas = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columnas
        [0, 4, 8], [2, 4, 6]             # Diagonales
    ]
    for linea in lineas:
        if tablero[linea[0]] == tablero[linea[1]] == tablero[linea[2]] and tablero[linea[0]] != " ":
            return tablero[linea[0]]
    if " " not in tablero:
        return "Empate"
    return None

def minimax(tablero, profundidad, es_maximizador):
    ganador = verificar_ganador(tablero)
    if ganador == "O": return 10 - profundidad
    if ganador == "X": return profundidad - 10
    if ganador == "Empate": return 0

    if es_maximizador:
        mejor_puntaje = -math.inf
        for i in range(9):
            if tablero[i] == " ":
                tablero[i] = "O"
                puntaje = minimax(tablero, profundidad + 1, False)
                tablero[i] = " "
                mejor_puntaje = max(puntaje, mejor_puntaje)
        return mejor_puntaje
    else:
        mejor_puntaje = math.inf
        for i in range(9):
            if tablero[i] == " ":
                tablero[i] = "X"
                puntaje = minimax(tablero, profundidad + 1, True)
                tablero[i] = " "
                mejor_puntaje = min(puntaje, mejor_puntaje)
        return mejor_puntaje

def mejor_movimiento(tablero):
    mejor_puntaje = -math.inf
    movimiento = None
    for i in range(9):
        if tablero[i] == " ":
            tablero[i] = "O" # La IA juega como 'O'
            puntaje = minimax(tablero, 0, False)
            tablero[i] = " "
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
        "🧠 **MAX** = turno de la IA (O) · **MIN** = turno del jugador (X). "
        "La IA es imbatible: lo mejor que puedes lograr es un empate."
    )

    if 'tablero_gato' not in st.session_state:
        st.session_state.tablero_gato = [" "] * 9
        st.session_state.ganador_gato = None

    def jugar(idx):
        if st.session_state.tablero_gato[idx] == " " and not st.session_state.ganador_gato:
            # Turno del jugador
            st.session_state.tablero_gato[idx] = "X"
            st.session_state.ganador_gato = verificar_ganador(st.session_state.tablero_gato)
            
            # Turno de la IA
            if not st.session_state.ganador_gato:
                mov = mejor_movimiento(st.session_state.tablero_gato)
                if mov is not None:
                    st.session_state.tablero_gato[mov] = "O"
                    st.session_state.ganador_gato = verificar_ganador(st.session_state.tablero_gato)

    # Dibujar tablero
    cols = st.columns([1,1,1, 3]) # El 3 es para dejar espacio en blanco a la derecha
    
    for i in range(9):
        with cols[i % 3]:
            # Usamos botones para la cuadrícula
            st.button(
                st.session_state.tablero_gato[i] if st.session_state.tablero_gato[i] != " " else "  ", 
                key=f"btn_{i}", 
                on_click=jugar, 
                args=(i,),
                use_container_width=True
            )

    if st.session_state.ganador_gato:
        if st.session_state.ganador_gato == "Empate":
            st.warning("¡Es un empate!")
        else:
            st.success(f"Ganador: {st.session_state.ganador_gato}")
        
        if st.button("Reiniciar Juego"):
            st.session_state.tablero_gato = [" "] * 9
            st.session_state.ganador_gato = None
            st.rerun()