import streamlit as st
from problemas import gato, reinas, frozen_lake, sokoban, nerd

st.set_page_config(page_title="Visualizador de Búsqueda IA", layout="wide")

# Cargar la Nerd Font para poder usar iconos en lugar de emojis.
nerd.cargar_fuente()

st.title("Visualizador de Algoritmos de Búsqueda")

st.write(
    "Elige una **pestaña** según el tipo de búsqueda, selecciona el **algoritmo** "
    "y ejecuta el proceso. Debajo del diagrama aparece una **traza paso a paso**: "
    "usa el deslizador (o los botones Anterior/Siguiente) para avanzar iteración "
    "por iteración y leer qué hace el algoritmo (OPEN/CLOSED, pila/cola, g/h/f, "
    "conflictos, temperatura, valores minimax, etc.)."
)

# Leyenda de algoritmos disponibles, siempre visible en la barra lateral.
st.sidebar.header("Algoritmos por tipo de búsqueda")
st.sidebar.markdown(
    "- **No informada** (Frozen Lake): BFS, DFS\n"
    "- **Informada** (Sokoban): GBFS, A*\n"
    "- **Local** (8 Reinas): Escalada Simple, Escalada Horizontal, "
    "Reinicio Aleatorio, Recocido Simulado\n"
    "- **Adversaria** (Gato): Minimax (Max / Min)"
)

# Navegación por pestañas en la parte superior (un panel por problema).
tab_frozen, tab_sokoban, tab_reinas, tab_gato = st.tabs([
    "Frozen Lake (No informada)",
    "Sokoban (Informada)",
    "8 Reinas (Local)",
    "Gato / Tic-Tac-Toe (Adversaria)",
])

with tab_frozen:
    frozen_lake.mostrar_interfaz()
with tab_sokoban:
    sokoban.mostrar_interfaz()
with tab_reinas:
    reinas.mostrar_interfaz()
with tab_gato:
    gato.mostrar_interfaz()
