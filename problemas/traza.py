"""Control de "traza paso a paso" reutilizable por los cuatro problemas.

Cada algoritmo genera una lista de "iteraciones" (la traza). Este módulo ofrece:
  - `nuevo_run`: marcar que se acaba de ejecutar el algoritmo, para que el
    deslizador vuelva a empezar en la iteración 0.
  - `selector`: dibujar el deslizador (y botones) para elegir qué iteración ver.
  - `caja`: mostrar la descripción de esa iteración en una caja de texto.
"""

import streamlit as st


def nuevo_run(clave):
    """Aumentar el contador de ejecuciones de este problema. Sirve para que el
    deslizador se reinicie en 0 cada vez que se vuelve a ejecutar el algoritmo."""
    st.session_state[f"{clave}_run"] = st.session_state.get(f"{clave}_run", 0) + 1


def selector(clave, total):
    """Mostrar el control para recorrer la traza y devolver la iteración elegida.
    Combina botones Anterior/Siguiente con un deslizador (0 a total-1)."""
    run = st.session_state.get(f"{clave}_run", 0)
    key_idx = f"{clave}_idx_{run}"  # La 'run' en la clave reinicia el control al re-ejecutar

    if key_idx not in st.session_state:
        st.session_state[key_idx] = 0

    if total <= 1:
        return 0

    col_a, col_b, col_c = st.columns([1, 1, 6])
    with col_a:
        if st.button("◀ Anterior", key=f"{clave}_prev_{run}", use_container_width=True):
            st.session_state[key_idx] = max(0, st.session_state[key_idx] - 1)
    with col_b:
        if st.button("Siguiente ▶", key=f"{clave}_next_{run}", use_container_width=True):
            st.session_state[key_idx] = min(total - 1, st.session_state[key_idx] + 1)

    # El deslizador comparte estado con los botones a través de la misma clave.
    idx = st.slider("Iteración", 0, total - 1, key=key_idx)
    return idx


def caja(texto):
    """Mostrar la descripción de la iteración actual en una caja monoespaciada
    (ideal para listar OPEN, CLOSED, la pila/cola y los cálculos)."""
    st.markdown("#### ¿Qué está haciendo el algoritmo en esta iteración?")
    st.code(texto, language="text")
