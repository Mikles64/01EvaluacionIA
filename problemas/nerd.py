"""Utilidades para usar una Nerd Font (iconos) en lugar de emojis.

Este módulo:
  1. Carga la fuente "Symbols Nerd Font" (incrustada en el repositorio) en el
     navegador mediante CSS @font-face, codificada en base64 para que funcione
     sin internet ni instalación previa.
  2. Define como constantes los iconos que usa la aplicación. Cada icono es un
     carácter del "área de uso privado" de Unicode que la Nerd Font sabe dibujar.

Así, en vez de escribir un emoji como el de un regalo se escribe `nerd.META`, y
el navegador muestra el glifo correspondiente de la Nerd Font.
"""

import base64
from pathlib import Path
import streamlit as st

# --- ICONOS (codepoints de Font Awesome incluidos en la Nerd Font) ---
# Frozen Lake
INICIO     = ""  # bandera a cuadros
HIELO      = ""  # copo de nieve
AGUJERO    = ""  # círculo (agujero)
META       = ""  # regalo (meta)
AGENTE     = ""  # persona (agente)
# Sokoban
PARED      = ""  # cuadrado relleno (pared)
OBJETIVO   = ""  # diana (objetivo)
CAJA       = ""  # cubo (caja)
TRABAJADOR = ""  # llave inglesa (trabajador)
CHECK      = ""  # marca de verificación en círculo
# Mensajes generales
ALERTA     = ""  # triángulo de advertencia
REINICIO   = ""  # flechas circulares (reinicio)
INFO       = ""  # i de información
IDEA       = ""  # bombilla (idea)

# Ruta a la fuente incrustada en el repositorio (carpeta assets/fonts).
_RUTA_FUENTE = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "SymbolsNerdFont-Regular.ttf"


def cargar_fuente():
    """Inyectar la Nerd Font en la página una sola vez por sesión. Se añade como
    última fuente de respaldo: el texto normal sigue con la fuente de Streamlit
    y solo los iconos (que esa fuente no tiene) se dibujan con la Nerd Font."""
    if st.session_state.get("_nerd_font_cargada"):
        return

    datos = base64.b64encode(_RUTA_FUENTE.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: 'SymbolsNF';
            src: url(data:font/ttf;base64,{datos}) format('truetype');
            font-display: swap;
        }}
        /* Añadir la Nerd Font como respaldo del tipo de letra heredado. */
        .stApp {{
            font-family: "Source Sans Pro", "Source Sans 3", sans-serif, 'SymbolsNF';
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_nerd_font_cargada"] = True


def icono(glifo, tam=30):
    """Devolver un fragmento HTML que dibuja un icono con la Nerd Font. Se usa
    dentro de las tablas del mapa para garantizar que se aplique la fuente."""
    return f"<span style='font-family:SymbolsNF; font-size:{tam}px;'>{glifo}</span>"
