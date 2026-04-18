"""
main.py — Ejecuta tu agente en el Grid World.

Uso:
    python main.py

Configuración:
    Modifica las variables de abajo para cambiar el mapa.
"""

from entorno import GridWorld
from mi_agente import MiAgente

# ── Configuración del mapa ───────────────────────
FILAS     = 10       # Alto del mapa
COLUMNAS  = 10       # Ancho del mapa
SEMILLA   = 60       # Cambiar para generar otro mapa
PAREDES   = 0.20     # Porcentaje de paredes (0.0 a 0.40)
VELOCIDAD = 1.15     # Segundos entre pasos (menor = más rápido)
MAX_PASOS = 50      # Máximo de pasos antes de rendirse
# ─────────────────────────────────────────────────

# Crear el mundo
mundo = GridWorld(
    filas=FILAS,
    columnas=COLUMNAS,
    semilla=SEMILLA,
    porcentaje_paredes=PAREDES,
)

# Mostrar mapa en consola
mundo.mostrar_mapa()

# Crear tu agente
agente = MiAgente()

# Ejecutar con animación
resultado = mundo.animar(agente, max_pasos=MAX_PASOS, velocidad=VELOCIDAD)