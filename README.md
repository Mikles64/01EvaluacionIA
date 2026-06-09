# Visualizador de Algoritmos de Búsqueda (IA)

Aplicación interactiva construida con **Streamlit** que permite **visualizar y
comparar** algoritmos de búsqueda aplicados a cuatro tipos de problemas clásicos
de Inteligencia Artificial. Para cada problema puedes **seleccionar el algoritmo**,
**ejecutar el proceso** y **observar los pasos principales** de la búsqueda
animados paso a paso.

## Problemas y algoritmos

| Tipo de búsqueda | Problema | Algoritmos disponibles |
|---|---|---|
| **No informada** | Frozen Lake (laberinto determinista) | **BFS**, **DFS** |
| **Informada** | Sokoban | **GBFS** (voraz), **A\*** |
| **Local** | 8 Reinas | **Escalada Simple**, **Escalada Horizontal**, **Reinicio Aleatorio**, **Recocido Simulado** |
| **Adversaria** | Gato / Tic-Tac-Toe | **Minimax** (nodos **Max** y **Min**) |

### Detalles

- **BFS / DFS** (Frozen Lake): exploran el laberinto sin heurística. BFS garantiza
  el camino más corto; DFS profundiza por una rama antes de retroceder.
- **A\* / GBFS** (Sokoban): usan la heurística de *distancia Manhattan* de cada caja
  a su objetivo más cercano. A\* prioriza `f = g + h` (óptimo); GBFS prioriza solo
  `h` (más rápido, no necesariamente óptimo).
- **8 Reinas** (búsqueda local): la heurística es el número de pares de reinas en
  conflicto; el objetivo es llegar a 0.
  - *Escalada Simple*: se mueve al primer vecino que mejora.
  - *Escalada Horizontal*: permite movimientos laterales para escapar de mesetas.
  - *Reinicio Aleatorio*: reinicia desde estados aleatorios al quedar atascada.
  - *Recocido Simulado*: acepta movimientos peores con probabilidad `e^(-Δ/T)`.
- **Gato** (búsqueda adversaria): la IA usa **Minimax**, alternando nodos **MAX**
  (la IA maximiza) y **MIN** (el jugador minimiza) para jugar de forma óptima.

## Ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```

Luego abre la URL local que muestra Streamlit (por defecto http://localhost:8501).

## Estructura del proyecto

```
01EvaluacionIA/
├── app.py                  # Interfaz principal y enrutador de problemas
├── requirements.txt
└── problemas/
    ├── frozen_lake.py      # Búsqueda no informada (BFS, DFS)
    ├── sokoban.py          # Búsqueda informada (A*, GBFS)
    ├── reinas.py           # Búsqueda local (4 algoritmos)
    └── gato.py             # Búsqueda adversaria (Minimax)
```
