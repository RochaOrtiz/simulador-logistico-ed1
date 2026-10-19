from typing import Any


class Node:
    """Representa un nodo de una estructura enlazada."""

    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    """Representa una lista doblemente enlazada."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        """Indica si la lista no contiene elementos."""
        return self.head is None

    def insertar_inicio(self, data):
        """Inserta un nuevo nodo al inicio de la lista."""
        nuevo_nodo = Node(data)
        if self.head is None:
            self.head = nuevo_nodo
            self.tail = nuevo_nodo
        else:
            nuevo_nodo.next = self.head
            self.head.prev = nuevo_nodo
            self.head = nuevo_nodo
        self.size += 1
        
    def insertar_final(self, data):
        """Inserta un nuevo nodo al final de la lista."""
        nuevo_nodo = Node(data)
        if self.tail is None:
            self.head = nuevo_nodo
            self.tail = nuevo_nodo
        else:
            nuevo_nodo.prev = self.tail
            self.tail.next = nuevo_nodo
            self.tail = nuevo_nodo
        self.size += 1

    def eliminar(self, data):
        """Elimina el primer nodo que contiene el dato indicado."""

        actual = self.head

        while actual is not None:
            if actual.data == data:
                break

            actual = actual.next

        if actual is None:
            return

        if actual.prev is None and actual.next is None:
            self.head = None
            self.tail = None

        elif actual.prev is None:
            self.head = actual.next
            self.head.prev = None

        elif actual.next is None:
            self.tail = actual.prev
            self.tail.next = None

        else:
            actual.prev.next = actual.next
            actual.next.prev = actual.prev

        self.size -= 1

    def buscar(self, data):
        """Busca un nodo que contenga el dato indicado."""

        actual = self.head

        while actual is not None:
            if actual.data == data:
                return actual

            actual = actual.next

        return None


class CircularDoublyLinkedList:
    """Lista doblemente enlazada cuyos extremos están conectados entre sí."""

    def __init__(self) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None
        self.current: Node | None = None
        self.size = 0

    def is_empty(self) -> bool:
        """Indica si la lista no contiene elementos."""
        return self.size == 0

    def insertar_inicio(self, data: Any) -> None:
        """Inserta un nodo antes del actual primero."""
        nuevo_nodo = Node(data)
        if self.is_empty():
            nuevo_nodo.next = nuevo_nodo
            nuevo_nodo.prev = nuevo_nodo
            self.head = nuevo_nodo
            self.tail = nuevo_nodo
            self.current = nuevo_nodo
        else:
            nuevo_nodo.next = self.head
            nuevo_nodo.prev = self.tail
            self.head.prev = nuevo_nodo
            self.tail.next = nuevo_nodo
            self.head = nuevo_nodo
        self.size += 1

    def insertar_final(self, data: Any) -> None:
        """Inserta un nodo después del actual último."""
        if self.is_empty():
            nuevo_nodo = Node(data)
            nuevo_nodo.next = nuevo_nodo
            nuevo_nodo.prev = nuevo_nodo
            self.head = nuevo_nodo
            self.tail = nuevo_nodo
            self.current = nuevo_nodo
            self.size = 1
            return

        nuevo_nodo = Node(data)
        nuevo_nodo.prev = self.tail
        nuevo_nodo.next = self.head
        self.tail.next = nuevo_nodo
        self.head.prev = nuevo_nodo
        self.tail = nuevo_nodo
        self.size += 1

    def eliminar(self, data: Any) -> None:
        """Elimina la primera aparición del dato, si existe."""
        nodo = self.buscar(data)
        if nodo is None:
            return

        if self.size == 1:
            self.head = None
            self.tail = None
            self.current = None
        else:
            nodo.prev.next = nodo.next
            nodo.next.prev = nodo.prev

            if nodo is self.head:
                self.head = nodo.next
            if nodo is self.tail:
                self.tail = nodo.prev
            if nodo is self.current:
                self.current = nodo.next

        nodo.next = None
        nodo.prev = None
        self.size -= 1

    def buscar(self, data: Any) -> Node | None:
        """Devuelve el primer nodo con ese dato o None si no existe."""
        actual = self.head
        for _ in range(self.size):
            if actual.data == data:
                return actual
            actual = actual.next
        return None

    def recorrer(self) -> list[Any]:
        """Devuelve los datos desde head hasta tail sin entrar en un ciclo."""
        datos = []
        actual = self.head
        for _ in range(self.size):
            datos.append(actual.data)
            actual = actual.next
        return datos

    def avanzar(self) -> Node | None:
        """Mueve la posición actual al siguiente nodo y lo devuelve."""
        if self.current is not None:
            self.current = self.current.next
        return self.current

    def retroceder(self) -> Node | None:
        """Mueve la posición actual al nodo anterior y lo devuelve."""
        if self.current is not None:
            self.current = self.current.prev
        return self.current


class Stack:
    """Representa una pila basada en nodos enlazados."""

    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, data):
        """Agrega un nuevo nodo al tope de la pila."""
        nuevo_nodo = Node(data)
        nuevo_nodo.next = self.top
        self.top = nuevo_nodo
        self.size += 1

    def pop(self):
        """Elimina y devuelve el elemento que está en el tope."""

        if self.top is None:
            return None

        nodo = self.top
        self.top = self.top.next
        self.size -= 1

        return nodo.data    

    def peek(self):
        """Devuelve el elemento del tope sin eliminarlo."""

        if self.top is None:
            return None

        return self.top.data
    
    def is_empty(self):
        """Indica si la pila está vacía."""
        return self.top is None    

    def clear(self):
        """Vacía completamente la pila."""
        self.top = None
        self.size = 0    

class UndoRedoManager:
    """Gestiona las operaciones de deshacer y rehacer."""

    def __init__(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def registrar_accion(self, accion):
        """Registra una nueva acción en el historial."""
        self.undo_stack.push(accion)
        self.redo_stack.clear()

    @staticmethod
    def _ejecutar_callback(accion, nombre):
        if isinstance(accion, dict):
            callback = accion.get(nombre)
        else:
            callback = getattr(accion, nombre, None)

        if callable(callback) and callback() is False:
            raise RuntimeError(f"No se pudo ejecutar la acción de {nombre}.")

    @staticmethod
    def _describir_accion(accion):
        if not isinstance(accion, dict):
            return str(accion)

        nombres = {
            "agregar_paquete": "Agregar paquete",
            "eliminar_paquete": "Eliminar paquete",
            "despachar_paquete": "Despachar paquete",
            "agregar_vehiculo": "Agregar vehículo",
            "eliminar_vehiculo": "Eliminar vehículo",
            "agregar_almacen": "Agregar almacén",
            "eliminar_almacen": "Eliminar almacén",
            "agregar_ruta": "Crear ruta",
        }
        descripcion = nombres.get(accion.get("tipo"), accion.get("tipo", "Acción"))
        codigo = getattr(accion.get("datos"), "codigo", None)
        return f"{descripcion}: {codigo}" if codigo else descripcion

    describir_accion = _describir_accion

    @classmethod
    def _listar_pila(cls, pila):
        acciones = []
        actual = pila.top
        while actual is not None:
            acciones.append(cls._describir_accion(actual.data))
            actual = actual.next
        return acciones

    def obtener_estado(self):
        """Devuelve el contenido de ambas pilas, desde la acción más reciente."""
        return {
            "undo": self._listar_pila(self.undo_stack),
            "redo": self._listar_pila(self.redo_stack),
            "undo_count": self.undo_stack.size,
            "redo_count": self.redo_stack.size,
        }

    def undo(self):
        """Revierte la acción más reciente y la pasa a la pila de redo."""
        if self.undo_stack.is_empty():
            return None

        accion = self.undo_stack.peek()
        self._ejecutar_callback(accion, "undo")
        self.undo_stack.pop()
        self.redo_stack.push(accion)

        return accion

    def redo(self):
        """Vuelve a aplicar la última acción deshecha."""
        if self.redo_stack.is_empty():
            return None

        accion = self.redo_stack.peek()
        self._ejecutar_callback(accion, "redo")
        self.redo_stack.pop()
        self.undo_stack.push(accion)

        return accion

class PriorityNode:
    """Representa un nodo para una cola de prioridad."""

    def __init__(self, data, priority):
        self.data = data
        self.priority = priority
        self.next = None

class PriorityQueue:
    """Representa una cola de prioridad basada en nodos."""

    def __init__(self):
        self.head = None
        self.size = 0

    def is_empty(self):
        """Indica si la cola no contiene elementos."""
        return self.head is None

    def enqueue(self, data, priority):
        """Inserta un elemento respetando su prioridad."""
        nuevo_nodo = PriorityNode(data, priority)

        if self.head is None:
            self.head = nuevo_nodo
            self.size += 1
            return
        if priority < self.head.priority:
            nuevo_nodo.next = self.head
            self.head = nuevo_nodo
            self.size += 1
            return

        actual = self.head

        while actual.next is not None and actual.next.priority <= priority:
            actual = actual.next

        nuevo_nodo.next = actual.next
        actual.next = nuevo_nodo

        self.size += 1

    def dequeue(self):
        """Elimina y devuelve el elemento con mayor prioridad."""
        if self.head is None:
            return None

        nodo = self.head
        self.head = self.head.next
        self.size -= 1

        return nodo.data

class CircularQueue:
    """Representa una cola FIFO circular basada en un buffer de capacidad fija."""

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("La capacidad de la cola debe ser mayor que cero.")

        self.capacity = capacity
        self.buffer = [None] * capacity
        self.front = 0
        self.rear = 0
        self.size = 0

    def clear(self):
        """Vacía la cola y reutiliza espacio para nuevas inserciones."""
        self.buffer = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.size = 0

    def enqueue(self, data):
        """Inserta un elemento al final si la cola no está llena."""
        if self.is_full():
            return

        self.buffer[self.rear] = data
        self.rear = (self.rear + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        """Elimina y devuelve el elemento más antiguo de la cola."""
        if self.is_empty():
            return None

        data = self.buffer[self.front]
        self.buffer[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1

        return data

    def peek(self):
        """Devuelve el elemento más antiguo sin eliminarlo."""
        if self.is_empty():
            return None

        return self.buffer[self.front]

    def is_empty(self):
        """Indica si la cola está vacía."""
        return self.size == 0

    def is_full(self):
        """Indica si la cola alcanzó su capacidad máxima."""
        return self.size == self.capacity