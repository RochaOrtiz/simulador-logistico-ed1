"""Entidades del dominio del simulador logístico."""

from collections.abc import Iterable
from math import isfinite
from numbers import Real
from typing import Any

from models.structures import CircularDoublyLinkedList, DoublyLinkedList

"""---------------------------------------------------------------"""
class Paquete:
    """Representa un paquete que debe ser despachado."""

    def __init__(self, codigo, destino, peso, prioridad):
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código del paquete es obligatorio.")
        if not isinstance(destino, str) or not destino.strip():
            raise ValueError("El destino del paquete es obligatorio.")
        if isinstance(peso, bool) or not isinstance(peso, Real):
            raise ValueError("El peso debe ser un número mayor que cero.")
        if not isfinite(peso) or peso <= 0:
            raise ValueError("El peso debe ser un número mayor que cero.")
        if isinstance(prioridad, bool) or not isinstance(prioridad, int) or prioridad <= 0:
            raise ValueError("La prioridad debe ser un entero positivo.")

        self.codigo = codigo.strip()
        self.destino = destino.strip()
        self.prioridad = prioridad
        self.peso = peso

    def __repr__(self):
        return f"Paquete(codigo={self.codigo}, destino={self.destino}, prioridad={self.prioridad})"

"""---------------------------------------------------------------"""
class Vehiculo:
    """Representa un vehículo de transporte."""

    def __init__(self, codigo, capacidad_maxima, estado="Disponible"):
        self.codigo = codigo
        self.capacidad_maxima = capacidad_maxima
        self.estado = estado

    def __repr__(self):
        return f"Vehiculo(codigo={self.codigo}, capacidad_maxima={self.capacidad_maxima}, estado={self.estado})"

"""---------------------------------------------------------------"""
class Ruta:
    """Representa una ruta de despacho."""

    def __init__(
        self,
        codigo,
        origen,
        destino,
        vehiculo=None,
        paradas: Iterable[Any] | None = None,
    ):
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código de la ruta es obligatorio.")
        if not isinstance(origen, str) or not origen.strip():
            raise ValueError("El origen de la ruta es obligatorio.")
        if not isinstance(destino, str) or not destino.strip():
            raise ValueError("El destino de la ruta es obligatorio.")

        self.codigo = codigo.strip()
        self.origen = origen.strip()
        self.destino = destino.strip()
        self.vehiculo = vehiculo
        self.paquetes = DoublyLinkedList()
        self.paradas = CircularDoublyLinkedList()
        paradas_iniciales = [origen, destino] if paradas is None else paradas
        for parada in paradas_iniciales:
            if not isinstance(parada, str) or not parada.strip():
                raise ValueError("Cada parada de la ruta debe contener texto.")
            self.paradas.insertar_final(parada.strip())

    def listar_paquetes(self):
        """Devuelve los paquetes asociados a la ruta en orden de despacho."""
        paquetes = []
        actual = self.paquetes.head
        while actual is not None:
            paquetes.append(actual.data)
            actual = actual.next
        return paquetes

    def calcular_peso_total_paquetes(self):
        """Suma el peso de los paquetes recorriendo la lista enlazada."""
        peso_total = 0
        actual = self.paquetes.head
        while actual is not None:
            peso_total += actual.data.peso
            actual = actual.next
        return peso_total

    def avanzar_parada(self):
        """Avanza a la siguiente parada de la ruta."""
        return self.paradas.avanzar()

    def retroceder_parada(self):
        """Retrocede a la parada anterior de la ruta."""
        return self.paradas.retroceder()

    def __repr__(self):
        return f"Ruta(codigo={self.codigo}, origen={self.origen}, destino={self.destino})"
"""---------------------------------------------------------------"""

class Almacen:
    """Representa un almacén del centro logístico."""

    def __init__(self, codigo, nombre, ubicacion):
        self.codigo = codigo
        self.nombre = nombre
        self.ubicacion = ubicacion

    def __repr__(self):
        return f"Almacen(codigo={self.codigo}, nombre={self.nombre}, ubicacion={self.ubicacion})"
