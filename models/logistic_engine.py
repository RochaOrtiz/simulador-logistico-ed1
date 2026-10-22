from models.entities import Almacen, Paquete, Ruta, Vehiculo
from models.structures import (
    DoublyLinkedList,
    PriorityQueue,
    CircularQueue,
    UndoRedoManager,
)

"""Motor logístico del simulador de distribución."""

from math import isfinite
from numbers import Real

"""---------------------------------------------------------------"""
def _buscar_entidad_por_codigo(estructura, codigo, nombre_entidad):
    """Busca una entidad en una lista enlazada usando un código normalizado."""
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError(f"El código del {nombre_entidad} es obligatorio.")

    codigo_buscado = codigo.strip().casefold()
    actual = estructura.head
    while actual is not None:
        if actual.data.codigo.strip().casefold() == codigo_buscado:
            return actual.data
        actual = actual.next
    return None

"""---------------------------------------------------------------"""
class LogisticEngine:
    """Motor logístico que gestiona paquetes, vehículos, rutas y almacenes."""

    def __init__(self):
        self.paquetes = PriorityQueue()
        self.vehiculos = DoublyLinkedList()
        self.rutas = CircularQueue(10) 
        self.almacenes = DoublyLinkedList()
        self._almacen_actual = None
        self.undo_redo_manager = UndoRedoManager()

    def _agregar_paquete_sin_historial(self, paquete):
        """Inserta un paquete sin registrar la acción en el historial."""
        if paquete is None:
            raise ValueError("El paquete no puede ser None.")
        self.paquetes.enqueue(paquete, paquete.prioridad)

    def _eliminar_paquete_sin_historial(self, paquete):
        """Elimina un paquete de la cola sin registrar la acción."""
        actual = self.paquetes.head
        anterior = None
        while actual is not None:
            if actual.data is paquete:
                if anterior is None:
                    self.paquetes.head = actual.next
                else:
                    anterior.next = actual.next
                actual.next = None
                self.paquetes.size -= 1
                return True
            anterior = actual
            actual = actual.next

        return False

    def _restaurar_cola_paquetes_sin_historial(self, paquetes):
        """Restaura exactamente el orden previo de la cola de prioridad."""
        self.paquetes.head = None
        self.paquetes.size = 0
        for paquete in paquetes:
            self.paquetes.enqueue(paquete, paquete.prioridad)

    def _quitar_paquete_de_ruta_sin_historial(self, ruta, paquete):
        """Quita por identidad un paquete de la lista de una ruta."""
        nodo = ruta.paquetes.buscar(paquete)
        if nodo is None:
            return False
        ruta.paquetes.eliminar(paquete)
        return True

    def _validar_ruta_activa_para_despacho(self, codigo_ruta):
        """Devuelve una ruta válida y activa o falla antes de alterar paquetes."""
        ruta = self.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")
        if not isinstance(ruta, Ruta):
            raise ValueError("La ruta seleccionada no es válida.")
        vehiculo = ruta.vehiculo
        if not isinstance(vehiculo, Vehiculo):
            raise ValueError(f"La ruta «{ruta.codigo}» no tiene vehículo asignado.")
        try:
            vehiculo_registrado = self.buscar_vehiculo(vehiculo.codigo)
        except (AttributeError, ValueError) as error:
            raise ValueError(
                f"La ruta «{ruta.codigo}» tiene un vehículo no válido."
            ) from error
        if vehiculo_registrado is not vehiculo or (
            not isinstance(vehiculo.estado, str)
            or vehiculo.estado.strip().casefold() != "en ruta"
        ):
            raise ValueError(
                f"La ruta «{ruta.codigo}» no tiene un vehículo activo válido."
            )
        if any(
            otra_ruta is not ruta and otra_ruta.vehiculo is vehiculo
            for otra_ruta in self.listar_rutas()
        ):
            raise ValueError(
                f"El vehículo «{vehiculo.codigo}» está asignado a varias rutas."
            )
        return ruta

    @staticmethod
    def _validar_capacidad_para_paquete(ruta, paquete):
        
        vehiculo = ruta.vehiculo
        capacidad_maxima = vehiculo.capacidad_maxima
        if (
            isinstance(capacidad_maxima, bool)
            or not isinstance(capacidad_maxima, Real)
            or not isfinite(capacidad_maxima)
            or capacidad_maxima <= 0
        ):
            raise ValueError(
                f"El vehículo «{vehiculo.codigo}» tiene una capacidad máxima no válida."
            )
        if (
            isinstance(paquete.peso, bool)
            or not isinstance(paquete.peso, Real)
            or not isfinite(paquete.peso)
            or paquete.peso <= 0
        ):
            raise ValueError(
                f"El paquete «{paquete.codigo}» tiene un peso no válido."
            )

        peso_actual = ruta.calcular_peso_total_paquetes()
        if not isfinite(peso_actual) or peso_actual < 0:
            raise ValueError(
                f"La carga actual de la ruta «{ruta.codigo}» no es válida."
            )
        capacidad_restante = capacidad_maxima - peso_actual
        if paquete.peso > capacidad_restante:
            raise ValueError(
                f"El paquete «{paquete.codigo}» ({paquete.peso:g} kg) no cabe "
                f"en la capacidad restante del vehículo «{vehiculo.codigo}» "
                f"({capacidad_restante:g} kg). Se requiere un vehículo con "
                "capacidad suficiente o una decisión del usuario."
            )

    def _rehacer_despacho_sin_historial(self, ruta, paquete):
        """Vuelve a vincular el paquete y retirarlo de la cola pendiente."""
        if self._validar_ruta_activa_para_despacho(ruta.codigo) is not ruta:
            return False
        if ruta.paquetes.buscar(paquete) is not None:
            return False
        self._validar_capacidad_para_paquete(ruta, paquete)
        if not self._eliminar_paquete_sin_historial(paquete):
            return False
        ruta.paquetes.insertar_final(paquete)
        return True

    def _deshacer_despacho_sin_historial(self, ruta, paquete, paquetes_anteriores):
        """Desvincula el paquete y restaura el orden previo de la cola."""
        if not self._quitar_paquete_de_ruta_sin_historial(ruta, paquete):
            return False
        self._restaurar_cola_paquetes_sin_historial(paquetes_anteriores)
        return True

    def _agregar_vehiculo_sin_historial(self, vehiculo):
        """Inserta un vehículo a la lista sin registrar la acción."""
        if vehiculo is None:
            raise ValueError("El vehículo no puede ser None.")
        self.vehiculos.insertar_final(vehiculo)

    def _eliminar_vehiculo_sin_historial(self, vehiculo):
        """Elimina un vehículo de la lista sin registrar la acción."""
        if vehiculo is None:
            return False
        if self._vehiculo_asignado_a_ruta(vehiculo):
            return False
        if self.vehiculos.buscar(vehiculo) is None:
            return False
        self.vehiculos.eliminar(vehiculo)
        return True

    def _vehiculo_asignado_a_ruta(self, vehiculo):
        """Indica si un vehículo está asignado actualmente a alguna ruta."""
        return any(ruta.vehiculo is vehiculo for ruta in self.listar_rutas())

    def _restaurar_lista_enlazada_sin_historial(self, estructura, elementos):
        """Restaura el orden previo de una lista enlazada sin crear historial."""
        while estructura.head is not None:
            estructura.eliminar(estructura.head.data)
        for elemento in elementos:
            estructura.insertar_final(elemento)

    def _agregar_ruta_sin_historial(self, ruta):
        """Inserta una ruta en la cola circular sin registrar la acción."""
        if not isinstance(ruta, Ruta):
            raise ValueError("Se debe agregar una ruta válida.")
        if self.rutas.is_full():
            raise ValueError(
                f"La cola de rutas está llena (capacidad: {self.rutas.capacity})."
            )
        self.rutas.enqueue(ruta)

    def _validar_vehiculo_para_ruta(self, vehiculo, ruta_actual=None):
        """Valida que el vehículo registrado pueda quedar activo en una ruta."""
        if self.buscar_vehiculo(vehiculo.codigo) is not vehiculo:
            raise ValueError("El vehículo asignado a la ruta no está registrado.")
        if any(
            ruta is not ruta_actual and ruta.vehiculo is vehiculo
            for ruta in self.listar_rutas()
        ):
            raise ValueError(
                f"El vehículo «{vehiculo.codigo}» ya está asignado a una ruta."
            )
        self._validar_vehiculo_disponible(vehiculo)

    def _agregar_ruta_con_vehiculo_sin_historial(self, ruta):
        """Agrega una ruta y marca como ocupado su vehículo, si lo tiene."""
        vehiculo = ruta.vehiculo
        if vehiculo is not None:
            self._validar_vehiculo_para_ruta(vehiculo)
        self._agregar_ruta_sin_historial(ruta)
        if vehiculo is not None:
            vehiculo.estado = "En ruta"

    def _eliminar_ruta_sin_historial(self, ruta):
        """Elimina una ruta de la cola circular sin registrar la acción."""
        if ruta is None or self.rutas.is_empty():
            return False

        elementos = []
        encontrado = False
        while not self.rutas.is_empty():
            elemento = self.rutas.dequeue()
            if elemento is ruta and not encontrado:
                encontrado = True
            else:
                elementos.append(elemento)

        self.rutas.clear()
        for elemento in elementos:
            self.rutas.enqueue(elemento)
        return encontrado

    def _eliminar_ruta_y_liberar_vehiculo_sin_historial(self, ruta):
        """Elimina una ruta y libera su vehículo si ya no tiene otra asignación."""
        if not self._eliminar_ruta_sin_historial(ruta):
            return False
        vehiculo = ruta.vehiculo
        if vehiculo is not None and not self._vehiculo_asignado_a_ruta(vehiculo):
            vehiculo.estado = "Disponible"
        return True

    def _agregar_almacen_sin_historial(self, almacen):
        """Inserta un almacén a la lista sin registrar la acción."""
        if almacen is None:
            raise ValueError("El almacén no puede ser None.")
        self.almacenes.insertar_final(almacen)
        if self._almacen_actual is None:
            self._almacen_actual = almacen

    def _eliminar_almacen_sin_historial(self, almacen):
        """Elimina un almacén de la lista sin registrar la acción."""
        if almacen is None:
            return False
        nodo = self.almacenes.buscar(almacen)
        if nodo is None:
            return False
        if self._almacen_actual is almacen:
            siguiente = nodo.next
            anterior = nodo.prev
            self._almacen_actual = (
                siguiente.data if siguiente is not None
                else anterior.data if anterior is not None
                else None
            )
        self.almacenes.eliminar(almacen)
        return True

    def _restaurar_almacenes_sin_historial(self, almacenes):
        """Restaura almacenes y conserva un cursor que apunte a la lista."""
        self._restaurar_lista_enlazada_sin_historial(self.almacenes, almacenes)
        if (
            self._almacen_actual is None
            or self.almacenes.buscar(self._almacen_actual) is None
        ):
            self._almacen_actual = (
                self.almacenes.head.data if self.almacenes.head is not None else None
            )


    def agregar_paquete(self, paquete):
        """Agrega un paquete a la cola de prioridad."""
        if not isinstance(paquete, Paquete):
            raise ValueError("Se debe agregar un paquete válido.")
        if self.buscar_paquete(paquete.codigo) is not None:
            raise ValueError(f"Ya existe un paquete con el código «{paquete.codigo}».")
        self._agregar_paquete_sin_historial(paquete)
        self.undo_redo_manager.registrar_accion({
            "tipo": "agregar_paquete",
            "datos": paquete,
            "redo": lambda: self._agregar_paquete_sin_historial(paquete),
            "undo": lambda: self._eliminar_paquete_sin_historial(paquete),
        })
        return paquete

    def buscar_paquete(self, codigo):
        """Busca un paquete por código y devuelve None si no existe."""
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código del paquete es obligatorio.")

        codigo_buscado = codigo.strip().casefold()
        actual = self.paquetes.head
        while actual is not None:
            if actual.data.codigo.casefold() == codigo_buscado:
                return actual.data
            actual = actual.next
        return None

    def eliminar_paquete(self, codigo):
        """Elimina el paquete indicado por código y lo devuelve si existe."""
        paquete = self.buscar_paquete(codigo)
        if paquete is None:
            return None
        paquetes_anteriores = tuple(self.listar_paquetes())
        if not self._eliminar_paquete_sin_historial(paquete):
            return None

        self.undo_redo_manager.registrar_accion({
            "tipo": "eliminar_paquete",
            "datos": paquete,
            "redo": lambda: self._eliminar_paquete_sin_historial(paquete),
            "undo": lambda: self._restaurar_cola_paquetes_sin_historial(
                paquetes_anteriores
            ),
        })
        return paquete

    def despachar_paquete(self, codigo_ruta):
        """Despacha el paquete prioritario y lo asocia a una ruta activa."""
        ruta = self._validar_ruta_activa_para_despacho(codigo_ruta)
        paquetes_anteriores = tuple(self.listar_paquetes())
        paquete_siguiente = self.obtener_paquete_siguiente()
        if paquete_siguiente is None:
            return None
        self._validar_capacidad_para_paquete(ruta, paquete_siguiente)

        paquete = self.paquetes.dequeue()
        ruta.paquetes.insertar_final(paquete)
        self.undo_redo_manager.registrar_accion({
            "tipo": "despachar_paquete",
            "datos": paquete,
            "redo": lambda: self._rehacer_despacho_sin_historial(ruta, paquete),
            "undo": lambda: self._deshacer_despacho_sin_historial(
                ruta,
                paquete,
                paquetes_anteriores,
            ),
        })
        return paquete
    

    def agregar_vehiculo(self, vehiculo):
        """Agrega un vehículo a la lista de vehículos."""
        if not isinstance(vehiculo, Vehiculo):
            raise ValueError("Se debe agregar un vehículo válido.")
        if not isinstance(vehiculo.codigo, str) or not vehiculo.codigo.strip():
            raise ValueError("El código del vehículo es obligatorio.")
        vehiculo.codigo = vehiculo.codigo.strip()
        if self.buscar_vehiculo(vehiculo.codigo) is not None:
            raise ValueError(f"Ya existe un vehículo con el código «{vehiculo.codigo}».")
        self._agregar_vehiculo_sin_historial(vehiculo)
        self.undo_redo_manager.registrar_accion({
            "tipo": "agregar_vehiculo",
            "datos": vehiculo,
            "redo": lambda: self._agregar_vehiculo_sin_historial(vehiculo),
            "undo": lambda: self._eliminar_vehiculo_sin_historial(vehiculo),
        })
        return vehiculo

    def buscar_vehiculo(self, codigo):
        """Busca un vehículo por código y devuelve None si no existe."""
        return _buscar_entidad_por_codigo(self.vehiculos, codigo, "vehículo")

    def eliminar_vehiculo(self, codigo):
        """Elimina el vehículo indicado por código y lo devuelve si existe."""
        vehiculo = self.buscar_vehiculo(codigo)
        if vehiculo is None:
            return None
        if self._vehiculo_asignado_a_ruta(vehiculo):
            raise ValueError(
                f"No se puede eliminar el vehículo «{vehiculo.codigo}» "
                "porque está asignado a una ruta."
            )
        vehiculos_anteriores = tuple(self.listar_vehiculos())
        if not self._eliminar_vehiculo_sin_historial(vehiculo):
            return None

        self.undo_redo_manager.registrar_accion({
            "tipo": "eliminar_vehiculo",
            "datos": vehiculo,
            "redo": lambda: self._eliminar_vehiculo_sin_historial(vehiculo),
            "undo": lambda: self._restaurar_lista_enlazada_sin_historial(
                self.vehiculos,
                vehiculos_anteriores,
            ),
        })
        return vehiculo

    def agregar_ruta(self, ruta):
        """Agrega una ruta a la cola circular de rutas."""
        if not isinstance(ruta, Ruta):
            raise ValueError("Se debe agregar una ruta válida.")
        if self.buscar_ruta(ruta.codigo) is not None:
            raise ValueError(f"Ya existe una ruta con el código «{ruta.codigo}».")
        self._agregar_ruta_con_vehiculo_sin_historial(ruta)
        self.undo_redo_manager.registrar_accion({
            "tipo": "agregar_ruta",
            "datos": ruta,
            "redo": lambda: self._agregar_ruta_con_vehiculo_sin_historial(ruta),
            "undo": lambda: self._eliminar_ruta_y_liberar_vehiculo_sin_historial(
                ruta
            ),
        })
        return ruta

    def buscar_ruta(self, codigo):
        """Busca una ruta pendiente por código."""
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código de la ruta es obligatorio.")

        codigo_buscado = codigo.strip().casefold()
        for ruta in self.listar_rutas():
            if ruta.codigo.casefold() == codigo_buscado:
                return ruta
        return None

    @staticmethod
    def _validar_vehiculo_disponible(vehiculo):
        if not isinstance(vehiculo.estado, str) or (
            vehiculo.estado.strip().casefold() != "disponible"
        ):
            raise ValueError(
                f"El vehículo «{vehiculo.codigo}» no está disponible."
            )

    def asignar_vehiculo_a_ruta(self, codigo_ruta, codigo_vehiculo):
        """Asigna o cambia el vehículo de una ruta registrada."""
        ruta = self.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")

        vehiculo = self.buscar_vehiculo(codigo_vehiculo)
        if vehiculo is None:
            raise ValueError(f"No se encontró el vehículo «{codigo_vehiculo}».")
        if ruta.vehiculo is vehiculo:
            return ruta
        self._validar_vehiculo_para_ruta(vehiculo, ruta)
        vehiculo_anterior = ruta.vehiculo
        ruta.vehiculo = vehiculo
        vehiculo.estado = "En ruta"
        if (
            vehiculo_anterior is not None
            and not self._vehiculo_asignado_a_ruta(vehiculo_anterior)
        ):
            vehiculo_anterior.estado = "Disponible"
        return ruta

    def desasignar_vehiculo_de_ruta(self, codigo_ruta):
        """Retira el vehículo asignado a una ruta registrada."""
        ruta = self.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")
        vehiculo = ruta.vehiculo
        ruta.vehiculo = None
        if vehiculo is not None and not self._vehiculo_asignado_a_ruta(vehiculo):
            vehiculo.estado = "Disponible"
        return ruta

    def agregar_almacen(self, almacen):
        """Agrega un almacén a la lista de almacenes."""
        if not isinstance(almacen, Almacen):
            raise ValueError("Se debe agregar un almacén válido.")
        if not isinstance(almacen.codigo, str) or not almacen.codigo.strip():
            raise ValueError("El código del almacén es obligatorio.")
        almacen.codigo = almacen.codigo.strip()
        if self.buscar_almacen(almacen.codigo) is not None:
            raise ValueError(f"Ya existe un almacén con el código «{almacen.codigo}».")
        self._agregar_almacen_sin_historial(almacen)
        self.undo_redo_manager.registrar_accion({
            "tipo": "agregar_almacen",
            "datos": almacen,
            "redo": lambda: self._agregar_almacen_sin_historial(almacen),
            "undo": lambda: self._eliminar_almacen_sin_historial(almacen),
        })
        return almacen

    def buscar_almacen(self, codigo):
        """Busca un almacén por código y devuelve None si no existe."""
        return _buscar_entidad_por_codigo(self.almacenes, codigo, "almacén")

    def eliminar_almacen(self, codigo):
        """Elimina el almacén indicado por código y lo devuelve si existe."""
        almacen = self.buscar_almacen(codigo)
        if almacen is None:
            return None
        almacenes_anteriores = tuple(self.listar_almacenes())
        if not self._eliminar_almacen_sin_historial(almacen):
            return None

        self.undo_redo_manager.registrar_accion({
            "tipo": "eliminar_almacen",
            "datos": almacen,
            "redo": lambda: self._eliminar_almacen_sin_historial(almacen),
            "undo": lambda: self._restaurar_almacenes_sin_historial(
                almacenes_anteriores
            ),
        })
        return almacen

    def _nodo_almacen_actual(self):
        if self.almacenes.head is None:
            self._almacen_actual = None
            return None

        nodo = (
            self.almacenes.buscar(self._almacen_actual)
            if self._almacen_actual is not None
            else None
        )
        if nodo is None:
            nodo = self.almacenes.head
            self._almacen_actual = nodo.data
        return nodo

    def obtener_estado_navegacion_almacenes(self):
        """Devuelve el almacén actual y si hay vecinos en cada dirección."""
        nodo = self._nodo_almacen_actual()
        return {
            "almacen": nodo.data if nodo is not None else None,
            "tiene_anterior": nodo is not None and nodo.prev is not None,
            "tiene_siguiente": nodo is not None and nodo.next is not None,
        }

    def seleccionar_almacen(self, codigo):
        """Establece el almacén actual por su código."""
        almacen = self.buscar_almacen(codigo)
        if almacen is None:
            raise ValueError(f"No se encontró el almacén «{codigo}».")
        self._almacen_actual = almacen
        return almacen

    def navegar_almacen_anterior(self):
        """Mueve el cursor al almacén anterior, si existe."""
        nodo = self._nodo_almacen_actual()
        if nodo is not None and nodo.prev is not None:
            self._almacen_actual = nodo.prev.data
        return self._almacen_actual

    def navegar_almacen_siguiente(self):
        """Mueve el cursor al almacén siguiente, si existe."""
        nodo = self._nodo_almacen_actual()
        if nodo is not None and nodo.next is not None:
            self._almacen_actual = nodo.next.data
        return self._almacen_actual

    def deshacer_ultima_accion(self):
        """Deshace la última acción registrada."""
        return self.undo_redo_manager.undo()

    def rehacer_ultima_accion(self):
        """Rehace la última acción deshecha."""
        return self.undo_redo_manager.redo()

    def listar_paquetes(self):
        """Devuelve los paquetes ordenados por prioridad, de mayor a menor."""
        resultado = []
        actual = self.paquetes.head
        while actual is not None:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

    def listar_vehiculos(self):
        """Devuelve los vehículos registrados."""
        resultado = []
        actual = self.vehiculos.head
        while actual is not None:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

    def listar_rutas(self):
        """Devuelve las rutas registradas en orden de llegada."""
        resultado = []
        for indice in range(self.rutas.size):
            posicion = (self.rutas.front + indice) % self.rutas.capacity
            resultado.append(self.rutas.buffer[posicion])
        return [ruta for ruta in resultado if ruta is not None]

    def listar_almacenes(self):
        """Devuelve los almacenes registrados."""
        resultado = []
        actual = self.almacenes.head
        while actual is not None:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

    def obtener_paquete_siguiente(self):
        """Retorna el próximo paquete a despachar sin eliminarlo."""
        if self.paquetes.is_empty():
            return None
        return self.paquetes.head.data


LogistEngine = LogisticEngine
