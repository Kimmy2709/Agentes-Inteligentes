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

from collections import deque
from entorno import Agente


class MiAgente(Agente):
    """
    Agente basado en utilidad.
    Funcion de utilidad: U = -pasos (camino mas corto).
    Algoritmo: BFS con cola FIFO. Replanifica cada vez que
    descubre celdas nuevas para mantener la ruta optima.
    """

    DELTAS = {
        'arriba':    (-1,  0),
        'abajo':     ( 1,  0),
        'izquierda': ( 0, -1),
        'derecha':   ( 0,  1),
    }

    def __init__(self):
        super().__init__(nombre="Agente BFS — Basado en Utilidad")
        self.plan         = []
        self.mapa         = {}
        self.meta         = None
        self.visitadas    = set()
        self.celdas_antes = 0

    def al_iniciar(self):
        self.plan         = []
        self.mapa         = {}
        self.meta         = None
        self.visitadas    = set()
        self.celdas_antes = 0

  
    def decidir(self, percepcion: dict) -> str:
        pos = percepcion['posicion']
        self.visitadas.add(pos)

        # Paso 1: aprender del entorno con lo que vemos ahora
        self._registrar_percepcion(pos, percepcion)

        # Paso 2: si la meta esta justo al lado, ir directo
        for direccion in self.ACCIONES:
            if percepcion[direccion] == 'meta':
                return direccion

        # Paso 3: si aprendimos celdas nuevas, replanificar
        celdas_ahora = len(self.mapa)
        if celdas_ahora > self.celdas_antes:
            self.celdas_antes = celdas_ahora
            self.plan = self._bfs(pos)

        # Paso 4: verificar que el plan sigue siendo valido
        if self.plan and percepcion[self.plan[0]] in ('pared', None):
            self.plan = self._bfs(pos)

        # Paso 5: ejecutar siguiente accion del plan
        if self.plan:
            return self.plan.pop(0)

        # Paso 6: explorar si BFS no encontro ruta aun
        return self._explorar(pos, percepcion)

    # ------------------------------------------------------------------
    # BFS — Busqueda de Anchura con Cola 
    # ------------------------------------------------------------------
    def _bfs(self, inicio):
        """
        Busca el camino mas corto desde inicio hasta self.meta.
        Solo avanza por celdas confirmadas como libres.
        Retorna lista de acciones o [] si no hay camino.
        """
        if self.meta is None:
            return []

        cola = deque()
        cola.append((inicio, []))
        vistos = {inicio}

        while cola:
            pos, acciones = cola.popleft()  # FIFO

            for direccion, (df, dc) in self.DELTAS.items():
                vecino = (pos[0] + df, pos[1] + dc)

                if vecino in vistos:
                    continue

                if vecino == self.meta:
                    return acciones + [direccion]  # Camino encontrado

                if self.mapa.get(vecino) == 'libre':
                    vistos.add(vecino)
                    cola.append((vecino, acciones + [direccion]))

        return []  # Sin camino actual

    # ------------------------------------------------------------------
    # Registrar lo que se ve en cada paso
    # ------------------------------------------------------------------
    def _registrar_percepcion(self, pos, percepcion):
        """
        Actualiza el mapa interno con las celdas adyacentes visibles
        El agente solo ve 4 celdas
        """
        f, c = pos
        self.mapa[pos] = 'libre'  # La celda donde estoy es libre

        for direccion, (df, dc) in self.DELTAS.items():
            vecino = (f + df, c + dc)
            estado = percepcion[direccion]

            if estado == 'meta':
                self.mapa[vecino] = 'libre'
                self.meta = vecino        
            elif estado in ('pared', None):
                self.mapa[vecino] = 'pared'  # Pared 
            elif estado == 'libre':
                if vecino not in self.mapa:
                    self.mapa[vecino] = 'libre'

    # ------------------------------------------------------------------
    # exploracioon cuando BFS no tiene ruta todavia
    # ------------------------------------------------------------------
    def _explorar(self, pos, percepcion):
        """
        Se usa cuando aun no conocemos suficiente del mapa.
        Prioriza celdas no visitadas y se acerca a la meta con la brujula.
        """
        vert, horiz = percepcion['direccion_meta']

        # Ordenams direcciones
        orden = []
        if vert  != 'ninguna': orden.append(vert)
        if horiz != 'ninguna': orden.append(horiz)
        for d in self.ACCIONES:
            if d not in orden: orden.append(d)

        f, c         = pos
        no_visitadas = []
        visitadas    = []

        for d in orden:
            if percepcion[d] not in ('libre', 'meta'):
                continue
            df, dc = self.DELTAS[d]
            vecino = (f + df, c + dc)
            if vecino not in self.visitadas:
                no_visitadas.append(d)
            else:
                visitadas.append(d)

        # ir a celdas nuevas
        if no_visitadas: return no_visitadas[0]
        if visitadas:    return visitadas[0]
        return 'abajo'