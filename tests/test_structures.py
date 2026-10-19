from models.structures import (
    CircularDoublyLinkedList,
    Node,
    DoublyLinkedList,
    Stack,
    UndoRedoManager,
    PriorityNode,
    PriorityQueue,
    CircularQueue,
)

def test_crear_nodo():
    """Prueba la creación de un nodo."""
    nodo = Node(10)
    assert nodo.data == 10
    assert nodo.next is None
    assert nodo.prev is None

def test_insertar_inicio():
    """Prueba la inserción de un nodo al inicio de la lista doblemente enlazada."""
    lista = DoublyLinkedList()
    lista.insertar_inicio(10)
    assert lista.head.data == 10
    assert lista.tail.data == 10
    assert lista.size == 1

    lista.insertar_inicio(20)
    assert lista.head.data == 20
    assert lista.tail.data == 10
    assert lista.size == 2

def test_insertar_final():
    """Prueba la inserción de un nodo al final de la lista doblemente enlazada."""
    lista = DoublyLinkedList()
    lista.insertar_final(10)
    assert lista.head.data == 10
    assert lista.tail.data == 10
    assert lista.size == 1

    lista.insertar_final(20)
    assert lista.head.data == 10
    assert lista.tail.data == 20
    assert lista.size == 2

def test_lista_vacia_buscar_y_eliminar():
    """Buscar y eliminar en una lista vacía no debe cambiar su estado."""
    lista = DoublyLinkedList()

    assert lista.is_empty() is True
    assert lista.buscar(10) is None
    lista.eliminar(10)

    assert lista.head is None
    assert lista.tail is None
    assert lista.size == 0

def test_conexiones_bidireccionales_tras_insertar():
    """Las inserciones deben mantener enlaces next y prev en ambos extremos."""
    lista = DoublyLinkedList()
    lista.insertar_inicio(20)
    lista.insertar_final(30)
    lista.insertar_inicio(10)

    assert lista.head.data == 10
    assert lista.head.prev is None
    assert lista.head.next.data == 20
    assert lista.head.next.prev is lista.head
    assert lista.tail.data == 30
    assert lista.tail.next is None
    assert lista.tail.prev.data == 20
    assert lista.tail.prev.next is lista.tail
    assert lista.size == 3

def test_eliminar_unico():
    """Prueba eliminar el único nodo de la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.eliminar(10)

    assert lista.head is None
    assert lista.tail is None
    assert lista.size == 0

def test_eliminar_inicio():
    """Prueba eliminar el primer nodo de la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    lista.eliminar(10)

    assert lista.head.data == 20
    assert lista.head.prev is None
    assert lista.tail.data == 30
    assert lista.size == 2

def test_eliminar_final():
    """Prueba eliminar el último nodo de la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    lista.eliminar(30)

    assert lista.head.data == 10
    assert lista.tail.data == 20
    assert lista.tail.next is None
    assert lista.size == 2

def test_eliminar_medio():
    """Prueba eliminar un nodo del medio de la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    lista.eliminar(20)

    assert lista.head.data == 10
    assert lista.tail.data == 30
    assert lista.head.next.data == 30
    assert lista.tail.prev.data == 10
    assert lista.size == 2

def test_eliminar_inexistente():
    """Prueba eliminar un dato que no existe."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    lista.eliminar(99)

    assert lista.head.data == 10
    assert lista.tail.data == 30
    assert lista.size == 3

def test_eliminar_solo_la_primera_aparicion():
    """Eliminar un dato duplicado debe quitar solo su primera aparición."""
    lista = DoublyLinkedList()
    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(20)
    lista.insertar_final(30)

    lista.eliminar(20)

    assert lista.head.data == 10
    assert lista.head.next.data == 20
    assert lista.head.next.prev is lista.head
    assert lista.head.next.next.data == 30
    assert lista.head.next.next.prev is lista.head.next
    assert lista.tail.data == 30
    assert lista.tail.next is None
    assert lista.size == 3

def test_buscar_existente():
    """Prueba buscar un dato que existe en la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    nodo = lista.buscar(20)

    assert nodo is not None
    assert nodo.data == 20

def test_buscar_inexistente():
    """Prueba buscar un dato que no existe en la lista."""
    lista = DoublyLinkedList()

    lista.insertar_final(10)
    lista.insertar_final(20)
    lista.insertar_final(30)

    nodo = lista.buscar(99)

    assert nodo is None

def test_lista_doblemente_enlazada_circular_vacia():
    """Las operaciones sobre una lista circular vacía deben ser seguras."""
    lista = CircularDoublyLinkedList()

    assert lista.is_empty() is True
    assert lista.recorrer() == []
    assert lista.buscar("A") is None
    assert lista.avanzar() is None
    assert lista.retroceder() is None
    lista.eliminar("A")
    assert lista.head is None
    assert lista.tail is None
    assert lista.current is None
    assert lista.size == 0

def test_lista_circular_con_un_nodo_se_enlaza_consigo_mismo():
    """El único nodo debe ser head, tail y su propio anterior y siguiente."""
    lista = CircularDoublyLinkedList()
    lista.insertar_final("Base")

    assert lista.head is lista.tail
    assert lista.head.next is lista.head
    assert lista.head.prev is lista.head
    assert lista.current is lista.head
    assert lista.avanzar() is lista.head
    assert lista.retroceder() is lista.head
    assert lista.recorrer() == ["Base"]

    lista.eliminar("Base")
    assert lista.is_empty() is True
    assert lista.head is None
    assert lista.tail is None
    assert lista.current is None
    assert lista.size == 0

def test_lista_circular_enlaces_y_navegacion_en_ambas_direcciones():
    """La lista debe cerrar el ciclo y envolver al avanzar o retroceder."""
    lista = CircularDoublyLinkedList()
    lista.insertar_final("A")
    lista.insertar_final("B")
    lista.insertar_final("C")

    assert lista.recorrer() == ["A", "B", "C"]
    assert lista.head.prev is lista.tail
    assert lista.tail.next is lista.head
    assert lista.head.next.prev is lista.head
    assert lista.tail.prev.next is lista.tail
    assert lista.avanzar().data == "B"
    assert lista.avanzar().data == "C"
    assert lista.avanzar().data == "A"
    assert lista.retroceder().data == "C"
    assert lista.retroceder().data == "B"

def test_lista_circular_insercion_y_eliminacion_conservan_enlaces():
    """Las modificaciones deben mantener los enlaces circulares y el tamaño."""
    lista = CircularDoublyLinkedList()
    lista.insertar_inicio("B")
    lista.insertar_inicio("A")
    lista.insertar_final("C")
    lista.insertar_final("D")

    assert lista.recorrer() == ["A", "B", "C", "D"]
    assert lista.head.prev is lista.tail
    assert lista.tail.next is lista.head

    lista.eliminar("A")
    assert lista.recorrer() == ["B", "C", "D"]
    assert lista.head.data == "B"
    assert lista.head.prev is lista.tail
    assert lista.tail.next is lista.head

    lista.eliminar("C")
    assert lista.recorrer() == ["B", "D"]
    assert lista.head.next.prev is lista.head
    assert lista.tail.prev.next is lista.tail

    lista.eliminar("D")
    assert lista.recorrer() == ["B"]
    assert lista.head is lista.tail
    assert lista.head.next is lista.head
    assert lista.head.prev is lista.head
    assert lista.size == 1

def test_crear_stack():
    """Prueba la creación de una pila vacía."""
    pila = Stack()

    assert pila.top is None
    assert pila.size == 0

def test_stack_push():
    """Prueba agregar elementos a la pila."""
    pila = Stack()

    pila.push(10)
    pila.push(20)
    pila.push(30)

    assert pila.top.data == 30
    assert pila.top.next.data == 20
    assert pila.top.next.next.data == 10
    assert pila.size == 3

def test_stack_pop():
    """Prueba eliminar el elemento del tope de la pila."""
    pila = Stack()

    pila.push(10)
    pila.push(20)
    pila.push(30)

    resultado = pila.pop()

    assert resultado == 30
    assert pila.top.data == 20
    assert pila.top.next.data == 10
    assert pila.size == 2

def test_stack_pop_vacia():
    """Prueba hacer pop en una pila vacía."""
    pila = Stack()

    resultado = pila.pop()

    assert resultado is None
    assert pila.top is None
    assert pila.size == 0

def test_stack_peek():
    """Prueba consultar el elemento del tope sin eliminarlo."""
    pila = Stack()

    pila.push(10)
    pila.push(20)
    pila.push(30)

    resultado = pila.peek()

    assert resultado == 30
    assert pila.top.data == 30
    assert pila.size == 3

def test_stack_peek_vacia():
    """Prueba consultar el tope de una pila vacía."""
    pila = Stack()

    resultado = pila.peek()

    assert resultado is None
    assert pila.top is None
    assert pila.size == 0

def test_stack_is_empty_vacia():
    """Prueba is_empty con una pila vacía."""
    pila = Stack()

    assert pila.is_empty() is True   

def test_stack_is_empty_con_elementos():
    """Prueba is_empty con una pila que contiene elementos."""
    pila = Stack()

    pila.push(10)

    assert pila.is_empty() is False

def test_crear_undo_redo_manager():
    """Prueba la creación del administrador de Undo y Redo."""
    manager = UndoRedoManager()

    assert manager.undo_stack.is_empty() is True
    assert manager.redo_stack.is_empty() is True

def test_registrar_accion():
    """Prueba registrar una acción en el historial."""
    manager = UndoRedoManager()

    manager.registrar_accion("Cargar paquete A")

    assert manager.undo_stack.peek() == "Cargar paquete A"
    assert manager.undo_stack.size == 1

def test_undo():
    """Prueba deshacer la última acción."""
    manager = UndoRedoManager()

    manager.registrar_accion("Cargar paquete A")
    manager.registrar_accion("Cargar paquete B")

    resultado = manager.undo()

    assert resultado == "Cargar paquete B"
    assert manager.undo_stack.peek() == "Cargar paquete A"
    assert manager.redo_stack.peek() == "Cargar paquete B"
    assert manager.undo_stack.size == 1
    assert manager.redo_stack.size == 1

def test_redo():
    """Prueba rehacer la última acción deshecha."""
    manager = UndoRedoManager()

    manager.registrar_accion("Cargar paquete A")
    manager.registrar_accion("Cargar paquete B")

    manager.undo()

    resultado = manager.redo()

    assert resultado == "Cargar paquete B"
    assert manager.undo_stack.peek() == "Cargar paquete B"
    assert manager.redo_stack.is_empty() is True

def test_undo_vacio():
    """Prueba hacer undo cuando no hay acciones."""
    manager = UndoRedoManager()

    resultado = manager.undo()

    assert resultado is None

def test_redo_vacio():
    """Prueba hacer redo cuando no hay acciones deshechas."""
    manager = UndoRedoManager()

    resultado = manager.redo()

    assert resultado is None

def test_nueva_accion_limpia_redo():
    """Prueba que una nueva acción vacía la pila de redo."""
    manager = UndoRedoManager()

    manager.registrar_accion("Acción A")
    manager.registrar_accion("Acción B")

    manager.undo()

    assert manager.redo_stack.peek() == "Acción B"

    manager.registrar_accion("Acción C")

    assert manager.undo_stack.peek() == "Acción C"
    assert manager.redo_stack.is_empty() is True

def test_priority_node():
    """Prueba la creación de un nodo con prioridad."""
    nodo = PriorityNode("Pedido A", 1)

    assert nodo.data == "Pedido A"
    assert nodo.priority == 1
    assert nodo.next is None

def test_priority_queue_enqueue_vacia():
    """Prueba insertar un elemento en una cola de prioridad vacía."""
    queue = PriorityQueue()

    queue.enqueue("Pedido A", 2)

    assert queue.head.data == "Pedido A"
    assert queue.head.priority == 2
    assert queue.head.next is None
    assert queue.size == 1

def test_priority_queue_enqueue_mayor_prioridad():
    """Prueba insertar un elemento con mayor prioridad que el primero."""
    queue = PriorityQueue()

    queue.enqueue("Pedido A", 2)
    queue.enqueue("Pedido B", 1)

    assert queue.head.data == "Pedido B"
    assert queue.head.priority == 1
    assert queue.head.next.data == "Pedido A"
    assert queue.head.next.priority == 2
    assert queue.size == 2

def test_priority_queue_enqueue_medio():
    """Prueba insertar un elemento en medio según su prioridad."""
    queue = PriorityQueue()

    queue.enqueue("Pedido A", 1)
    queue.enqueue("Pedido C", 3)
    queue.enqueue("Pedido B", 2)

    assert queue.head.data == "Pedido A"
    assert queue.head.next.data == "Pedido B"
    assert queue.head.next.next.data == "Pedido C"
    assert queue.size == 3

def test_priority_queue_enqueue_final():
    """Prueba insertar un elemento al final de la cola."""
    queue = PriorityQueue()

    queue.enqueue("Pedido A", 1)
    queue.enqueue("Pedido B", 2)
    queue.enqueue("Pedido C", 3)

    assert queue.head.data == "Pedido A"
    assert queue.head.next.data == "Pedido B"
    assert queue.head.next.next.data == "Pedido C"
    assert queue.head.next.next.next is None
    assert queue.size == 3

def test_priority_queue_dequeue_vacia():
    """Prueba retirar un elemento de una cola vacía."""
    queue = PriorityQueue()

    resultado = queue.dequeue()

    assert resultado is None
    assert queue.size == 0

def test_priority_queue_dequeue():
    """Prueba retirar el elemento con mayor prioridad."""
    queue = PriorityQueue()

    queue.enqueue("Pedido A", 3)
    queue.enqueue("Pedido B", 1)
    queue.enqueue("Pedido C", 2)

    resultado = queue.dequeue()

    assert resultado == "Pedido B"
    assert queue.head.data == "Pedido C"
    assert queue.head.priority == 2
    assert queue.size == 2

def test_circular_queue_inicialmente_vacia():
    """Prueba la creación de una cola circular vacía."""
    queue = CircularQueue(3)

    assert queue.capacity == 3
    assert queue.buffer == [None, None, None]
    assert queue.front == 0
    assert queue.rear == 0
    assert queue.size == 0
    assert queue.is_empty() is True

def test_circular_queue_enqueue_y_peek():
    """Prueba insertar elementos y consultar el primero sin retirarlo."""
    queue = CircularQueue(3)

    queue.enqueue("A")
    assert queue.peek() == "A"
    assert queue.size == 1

    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.peek() == "A"
    assert queue.size == 3
    assert queue.is_empty() is False

def test_circular_queue_dequeue_fifo():
    """Prueba que los elementos se retiren en orden FIFO."""
    queue = CircularQueue(3)
    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.dequeue() == "C"
    assert queue.size == 0
    assert queue.is_empty() is True

def test_circular_queue_dequeue_vacia():
    """Prueba retirar un elemento de una cola vacía."""
    queue = CircularQueue(3)

    assert queue.dequeue() is None
    assert queue.size == 0

def test_circular_queue_no_inserta_cuando_esta_llena():
    """Prueba que una cola llena rechace nuevas inserciones."""
    queue = CircularQueue(3)
    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.is_full() is True
    queue.enqueue("D")

    assert queue.size == 3
    assert queue.is_full() is True
    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.dequeue() == "C"

def test_circular_queue_reutiliza_buffer_circular():
    """Prueba volver al inicio del buffer y reutilizar posiciones liberadas."""
    queue = CircularQueue(3)
    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.front == 2

    queue.enqueue("D")
    queue.enqueue("E")

    assert queue.rear == 2
    assert queue.size == 3
    assert queue.is_full() is True
    assert queue.dequeue() == "C"
    assert queue.dequeue() == "D"
    assert queue.dequeue() == "E"
    assert queue.front == 2

def test_circular_queue_reinicia_front_tras_el_ultimo_elemento():
    """Prueba el avance circular de front y la transición al quedar vacía."""
    queue = CircularQueue(3)
    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.dequeue() == "C"
    assert queue.front == 0
    assert queue.size == 0
    assert queue.peek() is None



from models.logistic_engine import Paquete, Vehiculo, Ruta, Almacen


def test_crear_paquete():
    paquete = Paquete("P001", "Santa Cruz", 5, 1)

    assert paquete.codigo == "P001"
    assert paquete.destino == "Santa Cruz"
    assert paquete.peso == 5
    assert paquete.prioridad == 1


def test_crear_vehiculo():
    vehiculo = Vehiculo("V001", 100)

    assert vehiculo.codigo == "V001"
    assert vehiculo.capacidad_maxima == 100
    assert vehiculo.estado == "Disponible"


def test_crear_ruta():
    ruta = Ruta("R001", "La Paz", "Santa Cruz")

    assert ruta.codigo == "R001"
    assert ruta.origen == "La Paz"
    assert ruta.destino == "Santa Cruz"
    assert ruta.vehiculo is None


def test_crear_almacen():
    almacen = Almacen("A001", "Almacén Central", "Santa Cruz")

    assert almacen.codigo == "A001"
    assert almacen.nombre == "Almacén Central"
    assert almacen.ubicacion == "Santa Cruz"
