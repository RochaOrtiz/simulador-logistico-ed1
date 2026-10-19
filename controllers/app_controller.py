"""Controlador principal del simulador logístico."""

from math import isfinite

from models.logistic_engine import (
    Almacen,
    LogisticEngine,
    Paquete,
    Ruta,
    Vehiculo,
)


def _texto_obligatorio(valor, campo):
    """Valida y normaliza un campo de texto obligatorio."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo {campo} es obligatorio.")
    return valor.strip()


class AppController:
    """Conecta el modelo y la vista separando la lógica."""

    def __init__(self, engine=None):
        self.engine = engine if engine is not None else LogisticEngine()

    def agregar_paquete(self, codigo, destino, peso, prioridad):
        """Crea y registra un paquete en la cola de prioridad."""
        if peso is None or (isinstance(peso, str) and not peso.strip()):
            raise ValueError("El peso del paquete es obligatorio.")
        if prioridad is None or (isinstance(prioridad, str) and not prioridad.strip()):
            raise ValueError("La prioridad del paquete es obligatoria.")
        if isinstance(peso, bool):
            raise ValueError("El peso debe ser un número mayor que cero.")

        try:
            peso = float(peso)
        except (TypeError, ValueError) as error:
            raise ValueError("El peso debe ser un número mayor que cero.") from error

        if isinstance(prioridad, bool) or not isinstance(prioridad, (str, int)):
            raise ValueError("La prioridad debe ser un entero positivo.")
        try:
            prioridad = int(prioridad)
        except ValueError as error:
            raise ValueError("La prioridad debe ser un entero positivo.") from error

        paquete = Paquete(codigo, destino, peso, prioridad)
        self.engine.agregar_paquete(paquete)
        return paquete

    def buscar_paquete(self, codigo):
        """Busca un paquete por su código."""
        return self.engine.buscar_paquete(codigo)

    def eliminar_paquete(self, codigo):
        """Elimina un paquete por su código."""
        return self.engine.eliminar_paquete(codigo)

    def despachar_paquete(self, codigo_ruta):
        """Despacha el siguiente paquete prioritario hacia una ruta activa."""
        return self.engine.despachar_paquete(codigo_ruta)

    def agregar_vehiculo(self, codigo, capacidad_maxima, estado="Disponible"):
        """Valida y registra un vehículo en la lista enlazada."""
        codigo = _texto_obligatorio(codigo, "código del vehículo")
        estado = _texto_obligatorio(estado, "estado del vehículo")
        if capacidad_maxima is None or (
            isinstance(capacidad_maxima, str) and not capacidad_maxima.strip()
        ):
            raise ValueError("La capacidad máxima del vehículo es obligatoria.")
        if isinstance(capacidad_maxima, bool):
            raise ValueError("La capacidad máxima debe ser un número mayor que cero.")
        try:
            capacidad_maxima = float(capacidad_maxima)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "La capacidad máxima debe ser un número mayor que cero."
            ) from error
        if not isfinite(capacidad_maxima) or capacidad_maxima <= 0:
            raise ValueError("La capacidad máxima debe ser un número mayor que cero.")

        vehiculo = Vehiculo(codigo, capacidad_maxima, estado)
        self.engine.agregar_vehiculo(vehiculo)
        return vehiculo

    def buscar_vehiculo(self, codigo):
        """Busca un vehículo por su código."""
        return self.engine.buscar_vehiculo(codigo)

    def eliminar_vehiculo(self, codigo):
        """Elimina un vehículo por su código."""
        return self.engine.eliminar_vehiculo(codigo)

    def agregar_ruta(self, codigo, origen, destino, vehiculo=None, paradas=None):
        """Valida y registra una ruta en la cola circular."""
        codigo = _texto_obligatorio(codigo, "código de la ruta")
        origen = _texto_obligatorio(origen, "origen de la ruta")
        destino = _texto_obligatorio(destino, "destino de la ruta")
        if paradas is not None:
            if isinstance(paradas, str):
                paradas = paradas.split(",")
            paradas = list(paradas)
            if not paradas:
                raise ValueError("La ruta debe tener al menos una parada.")
            paradas = [
                _texto_obligatorio(parada, "nombre de parada")
                for parada in paradas
            ]

        if vehiculo is not None:
            codigo_vehiculo = (
                vehiculo.codigo if isinstance(vehiculo, Vehiculo) else vehiculo
            )
            vehiculo_registrado = self.engine.buscar_vehiculo(codigo_vehiculo)
            if vehiculo_registrado is None or (
                isinstance(vehiculo, Vehiculo) and vehiculo_registrado is not vehiculo
            ):
                raise ValueError("El vehículo asignado a la ruta no está registrado.")
            vehiculo = vehiculo_registrado

        ruta = Ruta(codigo, origen, destino, vehiculo, paradas)
        self.engine.agregar_ruta(ruta)
        return ruta

    def buscar_ruta(self, codigo):
        """Busca una ruta pendiente por código."""
        return self.engine.buscar_ruta(codigo)

    def asignar_vehiculo_a_ruta(self, codigo_ruta, codigo_vehiculo):
        """Asigna o cambia el vehículo de una ruta pendiente."""
        return self.engine.asignar_vehiculo_a_ruta(codigo_ruta, codigo_vehiculo)

    def desasignar_vehiculo_de_ruta(self, codigo_ruta):
        """Quita el vehículo asignado a una ruta pendiente."""
        return self.engine.desasignar_vehiculo_de_ruta(codigo_ruta)

    def avanzar_parada(self, codigo_ruta):
        """Avanza la posición actual de una ruta."""
        ruta = self.engine.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")
        return ruta.avanzar_parada()

    def retroceder_parada(self, codigo_ruta):
        """Retrocede la posición actual de una ruta."""
        ruta = self.engine.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")
        return ruta.retroceder_parada()

    def obtener_detalle_ruta(self, codigo_ruta):
        """Devuelve una instantánea de la ruta sin exponer nodos a la vista."""
        ruta = self.engine.buscar_ruta(codigo_ruta)
        if ruta is None:
            raise ValueError(f"No se encontró la ruta «{codigo_ruta}».")

        paradas = ruta.paradas.recorrer()
        indice_actual = None
        if ruta.paradas.current is not None:
            actual = ruta.paradas.head
            for indice, _ in enumerate(paradas):
                if actual is ruta.paradas.current:
                    indice_actual = indice
                    break
                actual = actual.next

        return {
            "codigo": ruta.codigo,
            "origen": ruta.origen,
            "destino": ruta.destino,
            "paradas": paradas,
            "indice_actual": indice_actual,
            "vehiculo": ruta.vehiculo,
            "paquetes": ruta.listar_paquetes(),
        }

    def agregar_almacen(self, codigo, nombre, ubicacion):
        """Valida y registra un almacén en la lista enlazada."""
        codigo = _texto_obligatorio(codigo, "código del almacén")
        nombre = _texto_obligatorio(nombre, "nombre del almacén")
        ubicacion = _texto_obligatorio(ubicacion, "ubicación del almacén")
        almacen = Almacen(codigo, nombre, ubicacion)
        self.engine.agregar_almacen(almacen)
        return almacen

    def buscar_almacen(self, codigo):
        """Busca un almacén por su código."""
        return self.engine.buscar_almacen(codigo)

    def eliminar_almacen(self, codigo):
        """Elimina un almacén por su código."""
        return self.engine.eliminar_almacen(codigo)

    def obtener_estado_navegacion_almacenes(self):
        """Devuelve el almacén actual y sus límites de navegación."""
        return self.engine.obtener_estado_navegacion_almacenes()

    def seleccionar_almacen(self, codigo):
        """Selecciona el almacén que se mostrará en la sección."""
        return self.engine.seleccionar_almacen(codigo)

    def navegar_almacen_anterior(self):
        """Navega al almacén anterior si está disponible."""
        return self.engine.navegar_almacen_anterior()

    def navegar_almacen_siguiente(self):
        """Navega al almacén siguiente si está disponible."""
        return self.engine.navegar_almacen_siguiente()

    def deshacer(self):
        """Deshace la última acción del gestor."""
        return self.engine.deshacer_ultima_accion()

    def rehacer(self):
        """Rehace la última acción deshecha."""
        return self.engine.rehacer_ultima_accion()

    def obtener_estado_historial(self):
        """Devuelve las acciones disponibles para deshacer y rehacer."""
        return self.engine.undo_redo_manager.obtener_estado()

    def describir_accion_historial(self, accion):
        """Devuelve una descripción legible de una acción del historial."""
        return self.engine.undo_redo_manager.describir_accion(accion)

    def obtener_estado(self):
        """Devuelve una vista resumida del estado del motor."""
        return {
            "paquetes": self.engine.listar_paquetes(),
            "vehiculos": self.engine.listar_vehiculos(),
            "rutas": self.engine.listar_rutas(),
            "almacenes": self.engine.listar_almacenes(),
        }
