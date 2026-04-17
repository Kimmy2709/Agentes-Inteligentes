"""
mi_agente.py — Aquí defines tu agente.
╔══════════════════════════════════════════════╗
║  ✏️  EDITA ESTE ARCHIVO                      ║
╚══════════════════════════════════════════════╝

Tu agente debe:
    1. Heredar de la clase Agente
    2. Implementar el método decidir(percepcion)
    3. Retornar: 'arriba', 'abajo', 'izquierda' o 'derecha'

Lo que recibes en 'percepcion':
───────────────────────────────
percepcion = {
    'posicion':       (3, 5),          # Tu fila y columna actual
    'arriba':         'libre',         # Qué hay arriba
    'abajo':          'pared',         # Qué hay abajo
    'izquierda':      'libre',         # Qué hay a la izquierda
    'derecha':        None,            # None = fuera del mapa

    # OPCIONAL — brújula hacia la meta.
    # No es percepción real del entorno, es información global.
    # Usarla hace el ejercicio más fácil. No usarla es más realista.
    'direccion_meta': ('abajo', 'derecha'),
}

Valores posibles de cada dirección:
    'libre'  → puedes moverte ahí
    'pared'  → bloqueado
    'meta'   → ¡la meta! ve hacia allá
    None     → borde del mapa, no puedes ir

Si tu agente retorna un movimiento inválido (hacia pared o
fuera del mapa), simplemente se queda en su lugar.
"""

from entorno import Agente
from collections import deque

class MiAgente(Agente):
    """
    Tu agente de navegación.

    Implementa el método decidir() para que el agente
    llegue del punto A al punto B en el grid.
    """

    DELTAS = {
        'arriba':    (-1,  0),
        'abajo':     ( 1,  0),
        'izquierda': ( 0, -1),
        'derecha':   ( 0,  1),
    }

    def __init__(self):
        super().__init__(nombre="Agente BFS")
        self.plan = []
        self.mapa_local = {}
        self.meta = None
        self.pasos = 0
        self.historial = []
        self.visitadas = set()

    def al_iniciar(self):
        self.plan = []
        self.mapa_local = {}
        self.meta = None
        self.pasos = 0
        self.historial = []
        self.visitadas = set()

    def decidir(self, percepcion: dict)-> str:
        
        """
        Decide la siguiente acción del agente.
        
        Parámetros:
            percepcion – diccionario con lo que el agente puede ver

        Retorna:
            'arriba', 'abajo', 'izquierda' o 'derecha'
        """
        
        self.pasos += 1
        pos_actual = percepcion['posicion']
        self.historial.append(pos_actual)
        self.visitadas.add(pos_actual)

        self._actualizar_mapa(pos_actual, percepcion)

        # Si la meta es adyacente, ir directo
        for direccion in self.ACCIONES:
            if percepcion.get(direccion) == 'meta':
                return direccion

        # Validar si el plan actual sigue siendo válido
        if self.plan:
            siguiente = self.plan[0]
            if percepcion.get(siguiente) in ('pared', None):
                self.plan = []

        # Calcular nuevo plan si no hay uno
        if not self.plan:
            if self.meta is not None:
                self.plan = self._bfs_solo_conocidas(pos_actual)

            # Si BFS no encontró ruta, explorar inteligentemente
            if not self.plan:
                return self._explorar(pos_actual, percepcion)

        return self.plan.pop(0)
    
        
    # ─────────────────────────────────────────────────
    #  BFS — Búsqueda en Anchura 
    # ─────────────────────────────────────────────────
 
    def _bfs_solo_conocidas(self, inicio: tuple) -> list:
        """BFS que SOLO usa celdas confirmadas como libres."""
        if self.meta is None:
            return []

        cola = deque()
        cola.append((inicio, []))
        visitados = {inicio}

        while cola:
            pos, camino = cola.popleft()

            for direccion, (dr, dc) in self.DELTAS.items():
                vecino = (pos[0] + dr, pos[1] + dc)

                if vecino in visitados:
                    continue

                if vecino == self.meta:
                    return camino + [direccion]

                # Solo avanzar si la celda está CONFIRMADA como libre
                if self.mapa_local.get(vecino) == 'libre':
                    visitados.add(vecino)
                    cola.append((vecino, camino + [direccion]))

        return []
    
    # ─────────────────────────────────────────────────
    #  Explorar sin loop
    # ─────────────────────────────────────────────────
 
    def _explorar(self, pos_actual: tuple, percepcion: dict) -> str:
        """
        Exploración que evita loops: prioriza celdas no visitadas,
        luego se acerca a la meta, nunca repite si puede evitarlo.
        """
        vert, horiz = percepcion.get('direccion_meta', ('abajo', 'derecha'))

        # Separar opciones en: no visitadas vs visitadas
        no_visitadas = []
        visitadas_ok = []

        for direccion in self.ACCIONES:
            celda = percepcion.get(direccion)
            if celda not in ('libre', 'meta'):
                continue

            r, c = pos_actual
            dr, dc = self.DELTAS[direccion]
            vecino = (r + dr, c + dc)

            if vecino not in self.visitadas:
                no_visitadas.append(direccion)
            else:
                visitadas_ok.append(direccion)

    # Ordenar no_visitadas priorizando dirección hacia la meta
        def puntaje(d):
            score = 0
            if d == vert:
                score += 2
            if d == horiz:
                score += 1
            return -score  # negativo para ordenar de mayor a menor

        no_visitadas.sort(key=puntaje)
        visitadas_ok.sort(key=puntaje)

        # Primero intentar celdas no visitadas
        for direccion in no_visitadas:
            return direccion

        # Si todas fueron visitadas, ir hacia la meta de todas formas
        for direccion in visitadas_ok:
            return direccion

        return 'abajo'

    def _actualizar_mapa(self, pos: tuple, percepcion: dict):
        r, c = pos
        self.mapa_local[pos] = 'libre'

        for direccion, (dr, dc) in self.DELTAS.items():
            vecino = (r + dr, c + dc)
            estado = percepcion.get(direccion)

            if estado is None:
                self.mapa_local[vecino] = 'pared'
            elif estado == 'meta':
                self.mapa_local[vecino] = 'libre'
                self.meta = vecino
            elif estado == 'pared':
                self.mapa_local[vecino] = 'pared'
            elif estado == 'libre':
                if vecino not in self.mapa_local:
                    self.mapa_local[vecino] = 'libre'