# Simulador de Centro Logístico de Distribución y Rutas de Despacho

## Descripción

Proyecto universitario para aplicar estructuras de datos implementadas manualmente
a la simulación de operaciones de un centro logístico. Durante la Semana 1 se
construyeron y probaron estructuras fundamentales que servirán como base para las
siguientes partes del simulador.

## Objetivo

Practicar estructuras de datos y algoritmos implementando sus operaciones, entendiendo
cómo organizan la información y verificando su comportamiento mediante pruebas
unitarias.

## Tecnologías utilizadas

- **Python:** implementación de las estructuras de datos.
- **Flet:** biblioteca utilizada para construir la interfaz.
- **pytest:** ejecución de las pruebas unitarias.

## Ejecución de la interfaz

Con Flet 1.0.3 instalado, el comando predeterminado conserva la ejecución en una
ventana de escritorio:

```powershell
python main.py
```

Para abrirla en el navegador de la misma computadora:

```powershell
python main.py --web
```

Para probar la vista desde un teléfono conectado a la misma red, se puede enlazar
el servidor a todas las interfaces de red:

```powershell
python main.py --web --host 0.0.0.0 --port 8550
```

En el teléfono se debe abrir `http://<IP-LOCAL-DE-LA-COMPUTADORA>:8550`, permitiendo
el acceso en el firewall si corresponde. Esto solo permite una prueba dentro de la
red local; no publica la aplicación en Internet. La vista ofrece navegación inferior
en anchos menores a 600 píxeles y una cuadrícula responsiva en pantallas mayores.

### Operaciones de paquetes

En la sección **Paquetes** se pueden registrar, buscar, eliminar y despachar paquetes.
El código y el destino son obligatorios; los códigos se recortan y se comparan sin
distinguir mayúsculas para impedir duplicados. El peso debe ser un número finito mayor
que cero y la prioridad un entero positivo. Como establece la cola de prioridad, un
número menor representa una prioridad mayor; **Despachar siguiente** retira el
paquete que encabeza la cola. La lista y los mensajes se actualizan desde el estado
del motor después de cada operación.

### Operaciones de vehículos y almacenes

En **Vehículos** se puede registrar un código, una capacidad máxima positiva y un
estado no vacío (el estado inicial sugerido es `Disponible`), buscar por código y
eliminar el elemento seleccionado. La lista muestra su capacidad y estado actuales.
En **Almacenes** se registran código, nombre y ubicación; también se puede buscar por
código y eliminar el elemento seleccionado. En ambas secciones los códigos se
recortan y se comparan sin distinguir mayúsculas para evitar duplicados. Los datos se
guardan en las listas doblemente enlazadas manuales del motor y la vista se refresca
tras cada operación.

### Rutas y recorrido

En **Rutas** se pueden registrar rutas con código, origen, destino y una o más
paradas separadas por comas; se puede buscar por código o seleccionar una ruta
registrada. La cola circular conserva su capacidad fija de 10 rutas y la interfaz
informa si está llena. Se puede asignar un vehículo registrado solo si está
`Disponible` y no está asignado a otra ruta activa. Al asignarlo pasa a `En ruta`;
al desasignarlo manualmente vuelve a `Disponible`. Un vehículo asignado no se puede
eliminar hasta que se desasigne de la ruta.

Los controles **Anterior** y **Siguiente** recorren las paradas usando la lista
doblemente enlazada circular. El estado mostrado es la posición de navegación y el
vehículo asociado. En **Paquetes**, se selecciona una ruta activa para **Despachar
siguiente**. El paquete prioritario sale de la cola pendiente y queda conservado en
la lista doblemente enlazada de paquetes de esa ruta. Una ruta sin vehículo asignado
no puede recibir nuevos paquetes; los que ya tenía permanecen asociados. Antes de
despachar, se compara el peso del paquete prioritario con la capacidad restante del
vehículo. Si no cabe, se conserva en la cola y no se intenta con paquetes posteriores.
No se gestionan entregas ni finalización de rutas.

### Historial, deshacer y rehacer

La sección **Historial** muestra las acciones disponibles y permite deshacerlas o
rehacerlas. El modelo conserva ambas pilas mediante la clase `Stack` enlazada. Si una
operación falla durante su callback, el registro permanece en su pila original; una
acción nueva registrada tras deshacer limpia la pila de rehacer.

Se pueden deshacer y rehacer altas y eliminaciones de paquetes, vehículos y almacenes,
además de la creación de rutas. El despacho de un paquete también es reversible: se
restaura la secuencia previa completa de la cola de prioridad, incluidos paquetes con
prioridades empatadas, y se revierte o restablece su asociación a la ruta elegida. La
vista actualiza sus secciones tras cada operación del historial.

La asignación/desasignación de vehículos y el movimiento entre paradas no se registran
en Undo/Redo. Por lo tanto, no aparecen como acciones reversibles en el historial.

## Día 4 — Empaquetado y distribución

### Ejecutable para Windows

Para este proyecto se usa `flet pack`, la opción basada en PyInstaller que empaqueta
el punto de entrada `main.py` en un ejecutable de escritorio. Es más ligera que
`flet build windows`, que compila una aplicación Flutter y requiere el toolchain
nativo de Windows (Visual Studio con la carga de trabajo Desktop development with
C++). `flet pack` no necesita ese compilador.

Las dependencias de empaquetado están separadas de las de ejecución en
`requirements-build.txt`: `flet-cli` proporciona el comando `flet pack` y PyInstaller
congela el programa y sus imports en el ejecutable. El entorno de compilación
comprobado usó Python 3.14.4, Flet/flet-cli 1.0.3 y PyInstaller 6.22.3 en Windows 11.

Desde PowerShell, en la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\flet.exe pack main.py `
  --name SimuladorLogistico `
  --product-name "Simulador Logistico" `
  --product-version 1.0.0 `
  --file-version 1.0.0.0 `
  --file-description "Simulador de Centro Logistico de Distribucion y Rutas de Despacho" `
  --company-name "Proyecto ED1"
```

El ejecutable se genera en `dist\SimuladorLogistico.exe`. La carpeta `build\` y el
archivo `SimuladorLogistico.spec` son auxiliares de PyInstaller; no son necesarios
para ejecutar el `.exe`. Para probarlo, ejecútalo desde el Explorador de archivos
o con `.\dist\SimuladorLogistico.exe`. El archivo no está firmado digitalmente, por
lo que Windows SmartScreen puede mostrar una advertencia al compartirlo.

### Aplicación web y publicación

El modo dinámico usa el servidor web de Flet/ASGI. Para abrirlo localmente en esta
computadora:

```powershell
.\.venv\Scripts\python.exe main.py --web --host 127.0.0.1 --port 8550
```

Abre `http://127.0.0.1:8550`. Para permitir el acceso desde otros dispositivos de
la misma red:

```powershell
.\.venv\Scripts\python.exe main.py --web --host 0.0.0.0 --port 8550
```

Luego abre `http://<IP-LOCAL-DE-LA-COMPUTADORA>:8550` en el otro dispositivo y
permite ese puerto en el firewall si Windows lo solicita. `0.0.0.0` escucha en las
interfaces de red disponibles; no es la dirección que se escribe en el navegador.

La publicación pública no se realiza con estos comandos locales. Requiere desplegar
el código en un servicio con Python compatible, un proceso de larga duración y
soporte de WebSockets. Configura el host como `0.0.0.0` y el puerto asignado por el
proveedor mediante `FLET_SERVER_IP` y `FLET_SERVER_PORT`, o pásalos explícitamente
con `--host` y `--port`. El proveedor debe terminar TLS/HTTPS y permitir el tráfico
WebSocket. Se necesita una cuenta/servicio de hosting si el proveedor la exige;
no se configuran ni incluyen credenciales en el proyecto. El simulador no está
desplegado públicamente.

### Android e iOS

Flet 1.0.3 permite construir Android con `flet build apk` o `flet build aab`. La
compilación requiere Android SDK y JDK 17; la CLI de Flet puede descargar e instalar
las herramientas compatibles si faltan. Para probar en un emulador o teléfono
Android se necesita además un emulador configurado o un dispositivo con depuración
USB habilitada. Un APK se instala para pruebas/distribución directa; un AAB está
orientado a tiendas como Google Play.

Comandos de compilación Android (una vez preparada la toolchain):

```powershell
.\.venv\Scripts\flet.exe build apk
.\.venv\Scripts\flet.exe build aab
```

No se generó un APK/AAB durante esta tarea: el entorno inspeccionado no tiene Android
SDK configurado, y `java` apunta a Java 21, no a JDK 17. Aunque Flet puede
descargar los componentes, eso instala herramientas grandes fuera del proyecto; se
deja la compilación pendiente de esa preparación. Para iOS, `flet build ipa` requiere
macOS y Xcode, así que no se puede producir desde este Windows.

La interfaz web responsiva también se puede abrir desde el navegador de un móvil,
pero eso no genera ni instala una aplicación nativa Android/iOS.

## Semana 1

La primera semana se enfocó en establecer las bases del proyecto y crear estructuras
de datos fundamentales sin depender de implementaciones automáticas de esas
estructuras.

### Día 1 — Python, Flet y bases del proyecto

Se preparó el entorno de desarrollo con Python, se configuró Flet como tecnología
del proyecto y se organizó inicialmente el trabajo. También se preparó la base para
implementar manualmente las estructuras de datos.

Se tuvo en cuenta el uso de interfaces o estructuras abstractas cuando fueran
apropiadas, junto con el estilo PEP 8, los docstrings y otras buenas prácticas. La
implementación de esta semana se centra en las clases concretas descritas abajo; no
añade una jerarquía de clases abstractas.

### Día 2 — DoublyLinkedList

Se implementó una lista doblemente enlazada utilizando `Node` y `DoublyLinkedList`.

- `Node` almacena `data` y las referencias `next` y `prev`.
- `DoublyLinkedList` mantiene `head` (primer nodo), `tail` (último nodo) y `size`
  (cantidad de nodos).
- `next` enlaza un nodo con el siguiente y `prev` con el anterior. Al insertar o
  eliminar nodos se actualizan las referencias vecinas para mantener la cadena en
  ambas direcciones.
- `insertar_inicio(data)` agrega un nodo antes del actual `head`.
- `insertar_final(data)` agrega un nodo después del actual `tail`.
- `eliminar(data)` busca y elimina la primera aparición del dato. Si la lista está
  vacía o el dato no existe, no altera la lista.
- `buscar(data)` recorre la lista y devuelve el nodo encontrado o `None`.
- En una lista vacía, una inserción establece tanto `head` como `tail`. Eliminar el
  único nodo deja ambos extremos en `None`.

Las inserciones al inicio y al final son O(1), porque se actualizan un número fijo
de referencias. `buscar` y `eliminar` son O(n) en el peor caso, porque primero
pueden tener que recorrer la lista para localizar el dato.

Se realizaron pruebas unitarias para las inserciones, la búsqueda y la eliminación
en distintos casos, incluidos extremos, nodo único y dato inexistente.

### Día 3 — Stack y UndoRedoManager

#### Stack

`Stack` es una pila LIFO (Last In, First Out): el último elemento agregado es el
primero que se retira. Está implementada con nodos enlazados que reutilizan la clase
`Node`.

- `top` señala el nodo que está en la cima.
- `size` indica la cantidad de elementos.
- `push(data)` agrega un nodo en la cima.
- `pop()` retira y devuelve el elemento de la cima; devuelve `None` si está vacía.
- `peek()` devuelve el elemento de la cima sin retirarlo; devuelve `None` si está
  vacía.
- `is_empty()` indica si la pila está vacía.
- `clear()` deja la pila vacía y su tamaño en cero.

Todas estas operaciones son O(1): trabajan con la cima y no recorren los nodos.

#### UndoRedoManager

`UndoRedoManager` utiliza dos objetos `Stack`:

- `undo_stack` guarda las acciones registradas y las que pueden pasarse entre pilas.
- `redo_stack` guarda las acciones que se retiraron de `undo_stack` mediante `undo`.
- `registrar_accion(accion)` agrega la acción a `undo_stack` y limpia `redo_stack`.
- `undo()` ejecuta el callback que revierte la acción y, solo si termina
  correctamente, la pasa de `undo_stack` a `redo_stack`.
- `redo()` ejecuta el callback que reaplica la acción y, solo si termina
  correctamente, la pasa de `redo_stack` a `undo_stack`.
- Si la pila correspondiente está vacía, `undo()` o `redo()` devuelve `None`.
- `obtener_estado()` entrega las descripciones y cantidades de ambas pilas para la
  interfaz, sin sustituir la estructura enlazada.

Una nueva acción limpia `redo_stack` porque, después de registrar un cambio nuevo,
las acciones deshechas pertenecen a una secuencia anterior y ya no forman la cadena
de rehacer vigente. El traslado entre pilas es O(1); ejecutar los callbacks tiene el
costo de la operación de modelo correspondiente. En el simulador, esta estructura proporciona una base para organizar un
historial de acciones; la clase mueve los valores entre pilas y no ejecuta por sí
misma la reversión de operaciones externas.

### Día 4 — PriorityQueue y CircularQueue

#### PriorityQueue

Una cola de prioridad retira primero el elemento con mayor prioridad, en vez de
atender únicamente el orden de llegada. `PriorityNode` almacena `data`, `priority`
y una referencia `next`. `PriorityQueue` es una lista enlazada ordenada que mantiene
`head` (primer elemento, el siguiente en salir) y `size` (cantidad de elementos).

La convención implementada es que un número menor representa una prioridad mayor.
Por ejemplo, prioridad 1 sale antes que prioridad 2, y prioridad 2 antes que
prioridad 3.

- `enqueue(data, priority)` inserta el nodo en la posición ordenada. Si su prioridad
  es mayor (número menor) que la del primero, lo coloca al inicio; de lo contrario,
  recorre la lista hasta encontrar su lugar. Los elementos con la misma prioridad
  se insertan después de los que ya tienen esa prioridad.
- `dequeue()` elimina y devuelve el nodo de `head`, que contiene la prioridad más
  alta; devuelve `None` si la cola está vacía.

`enqueue` es O(n) en el peor caso porque puede recorrer los nodos. `dequeue` es
O(1), ya que solo actualiza `head`. Esta estructura puede organizar pedidos del
centro logístico según la prioridad asignada.

#### CircularQueue — Cola Circular

`CircularQueue` es una cola FIFO (First In, First Out): el primer elemento en entrar
es el primero en salir. Usa un buffer de tamaño fijo y punteros circulares.

- `capacity` es la capacidad máxima.
- `buffer` es el arreglo de tamaño `capacity` donde se almacenan los elementos.
- `front` indica la posición del elemento más antiguo.
- `rear` indica la posición donde se insertará el siguiente elemento.
- `size` indica cuántos elementos contiene la cola actualmente.
- `enqueue(data)` inserta al final si no está llena. Si está llena, no inserta el
  elemento.
- `dequeue()` retira y devuelve el elemento más antiguo; devuelve `None` si está
  vacía. La posición retirada se limpia y puede reutilizarse.
- `peek()` consulta el elemento más antiguo sin retirarlo; devuelve `None` si está
  vacía.
- `is_empty()` e `is_full()` comprueban si la cola está vacía o llena.

Después de cada avance, se actualizan los índices mediante `% capacity`. El operador
`%` obtiene el resto de la división: por eso, cuando un índice alcanza `capacity`,
el siguiente índice vuelve a ser `0`. Se llama circular porque `front` y `rear`
pueden dar la vuelta al buffer, y las posiciones liberadas vuelven a estar
disponibles.

Ejemplo con capacidad 4:

```text
Estado inicial:
[ _ , _ , _ , _ ]
front = 0, rear = 0, size = 0

enqueue("A"), enqueue("B"), enqueue("C"):
[ A , B , C , _ ]
front = 0, rear = 3, size = 3

enqueue("D"):
[ A , B , C , D ]
front = 0, rear = 0, size = 4
```

Al insertar `"D"` en el índice 3, `rear` avanza como `(3 + 1) % 4` y vuelve al
índice 0. Si luego se retira `"A"`, esa posición queda libre; una inserción posterior
puede escribir allí. Las operaciones `enqueue`, `dequeue`, `peek`, `is_empty` e
`is_full` son O(1), pues no recorren el buffer: solo consultan o actualizan
posiciones, contadores y punteros. Una capacidad no positiva se rechaza al crear la
cola mediante `ValueError`.

La cola circular puede servir como buffer limitado para organizar un flujo de
vehículos o pedidos que espera procesamiento en el centro logístico.

### Día 5 — Pruebas unitarias

Se utilizaron pruebas unitarias con `pytest` para comprobar las operaciones de las
estructuras y sus estados importantes. Entre los aspectos probados se incluyen:

- estructuras vacías;
- inserción, eliminación y búsqueda;
- casos con un solo elemento y con varios elementos;
- inserciones al inicio y al final de la lista;
- operaciones `undo` y `redo`, incluida la limpieza de `redo` al registrar una
  acción nueva;
- orden de prioridad y extracción de una cola de prioridad vacía;
- límite de capacidad, FIFO y reutilización circular del buffer;
- estados vacíos y llenos, y otros casos extremos relevantes.

En la última ejecución de `pytest` sobre `tests/test_structures.py`, **39 pruebas
pasaron**.

## Complejidad de las estructuras

| Estructura | Operación | Complejidad | Explicación |
| --- | --- | --- | --- |
| DoublyLinkedList | `insertar_inicio`, `insertar_final` | O(1) | Actualiza referencias en un extremo. |
| DoublyLinkedList | `buscar`, `eliminar` | O(n) | Puede recorrer la lista para encontrar el dato. |
| Stack | `push`, `pop`, `peek`, `is_empty`, `clear` | O(1) | Trabaja directamente con `top` y el tamaño. |
| UndoRedoManager | `registrar_accion`, `undo`, `redo` | O(1) | Cada operación usa operaciones constantes de las pilas. |
| PriorityQueue | `enqueue` | O(n) | Puede recorrer la lista para ordenar el nuevo nodo. |
| PriorityQueue | `dequeue` | O(1) | Retira el primer nodo y actualiza `head`. |
| CircularQueue | `enqueue`, `dequeue`, `peek`, `is_empty`, `is_full` | O(1) | Consulta o actualiza posiciones y contadores sin recorrer elementos. |

O(1) representa tiempo constante respecto al número de elementos. O(n) representa
tiempo que puede crecer linealmente con la cantidad de elementos de la estructura.

## Relación con el sistema logístico

- **DoublyLinkedList:** puede servir como base para representar el inventario activo
  del almacén y recorrerlo en ambas direcciones.
- **Stack:** permite organizar operaciones o un historial que sigue el orden LIFO.
- **UndoRedoManager:** organiza el paso de acciones entre las pilas para deshacer y
  rehacer dentro del historial.
- **PriorityQueue:** organiza pedidos para que los de prioridad más alta se atiendan
  antes.
- **CircularQueue:** puede representar un buffer de capacidad limitada para el
  procesamiento de vehículos o pedidos.

Estas estructuras constituyen parte de la base del sistema. La integración de la
cola circular de rutas con el recorrido circular de paradas se describe a
continuación.

## Recorrido circular de reparto

`CircularDoublyLinkedList` reutiliza `Node` para enlazar cada parada con la siguiente
y la anterior, incluyendo el enlace de `tail` a `head` y de `head` a `tail`. Cada
`Ruta` mantiene su propio recorrido en `paradas`; si no se indican paradas
personalizadas, se inicializa con su origen y destino. `avanzar_parada()` y
`retroceder_parada()` actualizan el nodo actual y permiten dar la vuelta al ciclo.

Esta lista de paradas no sustituye `LogisticEngine.rutas`: esa estructura continúa
siendo una `CircularQueue` de capacidad 10 que administra rutas pendientes en orden
FIFO. La lista doblemente enlazada circular representa el recorrido dentro de una
ruta. La interfaz permite seleccionar una ruta pendiente y navegar por sus paradas
paso a paso; no ejecuta una animación automática.

## Estado de la Semana 1

Estructuras implementadas y probadas:

- DoublyLinkedList
- Stack
- UndoRedoManager
- PriorityQueue
- CircularQueue

La Semana 1 se enfocó en construir y validar las estructuras de datos fundamentales
antes de continuar con las siguientes partes del simulador.
