# Simulador de Logística Inteligente y Despacho de Recursos

Proyecto universitario de **Estructuras de Datos 1**. El simulador modela la
gestión de paquetes, vehículos, almacenes y rutas de despacho mediante estructuras
de datos implementadas en el propio proyecto. Incluye una interfaz gráfica en
Flet y un historial de operaciones con opciones para deshacer y rehacer acciones
compatibles.

## Tabla de contenido

- [Simulador de Logística Inteligente y Despacho de Recursos](#simulador-de-logística-inteligente-y-despacho-de-recursos)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Problema y objetivo](#problema-y-objetivo)
  - [Funcionalidades implementadas](#funcionalidades-implementadas)
    - [Paquetes](#paquetes)
    - [Vehículos](#vehículos)
    - [Rutas](#rutas)
    - [Almacenes](#almacenes)
    - [Historial](#historial)
  - [Tecnologías y requisitos](#tecnologías-y-requisitos)
  - [Instalación y ejecución en Windows](#instalación-y-ejecución-en-windows)
  - [Ejecución de las pruebas](#ejecución-de-las-pruebas)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Arquitectura](#arquitectura)
  - [Estructuras de datos](#estructuras-de-datos)
  - [Estado y mejoras futuras](#estado-y-mejoras-futuras)
    - [Implementado](#implementado)
    - [Posibles mejoras (no implementadas)](#posibles-mejoras-no-implementadas)
  - [Capturas de pantalla](#capturas-de-pantalla)

## Problema y objetivo

La organización de un centro de distribución requiere administrar pedidos con
distinta prioridad, asignar vehículos a rutas y consultar el avance de los
recorridos. El objetivo del proyecto es representar estas operaciones y mostrar
cómo distintas estructuras de datos pueden resolver necesidades concretas de
organización, navegación y control de cambios.

El simulador es una aplicación académica local. Los datos se mantienen en memoria
durante la ejecución; el proyecto no implementa persistencia en archivos ni en una
base de datos.

## Funcionalidades implementadas

La interfaz presenta cinco módulos: **Paquetes**, **Vehículos**, **Rutas**,
**Almacenes** e **Historial**.

### Paquetes

- Agregar, buscar y eliminar paquetes por código.
- Ordenar los paquetes pendientes por prioridad. Un valor numérico menor representa
  una prioridad más alta; los elementos con igual prioridad conservan el orden de
  llegada.
- Despachar el paquete prioritario a una ruta con un vehículo asignado.
- Validar la capacidad restante del vehículo antes del despacho. Si el paquete de
  mayor prioridad no cabe, el despacho se rechaza y no se prueba un paquete posterior.
- Conservar los paquetes despachados asociados a su ruta.

### Vehículos

- Registrar, buscar y eliminar vehículos.
- Asignar un vehículo disponible a una ruta y cambiar su estado a `En ruta`.
- Liberar un vehículo al desasignarlo; no se permite eliminar un vehículo que siga
  asignado a una ruta.

### Rutas

- Crear y buscar rutas, con paradas personalizadas o con origen y destino como
  recorrido inicial.
- Asignar o desasignar un vehículo y navegar por las paradas en ambas direcciones.
- Consultar el vehículo, la posición del recorrido y los paquetes despachados.
- Administrar hasta **10 rutas** en una cola circular de capacidad fija. La interfaz
  permite seleccionar una ruta registrada; el código no implementa la finalización
  o entrega de rutas.

### Almacenes

- Registrar, buscar y eliminar almacenes.
- Seleccionar un almacén y recorrer la lista con los controles **Anterior** y
  **Siguiente**.

### Historial

- Consultar las acciones disponibles y ejecutar **Deshacer** y **Rehacer**.
- El historial incluye altas y eliminaciones de paquetes, vehículos y almacenes,
  creación de rutas y despacho de paquetes.
- Al registrar una acción nueva después de deshacer, se limpia la pila de rehacer.
- La asignación/desasignación de vehículos y el movimiento entre paradas no se
  registran como acciones reversibles.

La vista usa tema claro y diseño responsivo. En ventanas estrechas se muestra una
barra de navegación inferior; en anchos mayores las secciones se distribuyen en
una cuadrícula.

## Tecnologías y requisitos

- **Python 3.10 o posterior.** La dependencia Flet 1.0.3 declara Python 3.10 como
  versión mínima.
- **Flet 1.0.3** y **flet-web 1.0.3** para la aplicación de escritorio y su modo web.
- **pytest 9.1.1** para ejecutar las pruebas.
- **PowerShell** para los comandos de esta guía en Windows.

Las dependencias de ejecución y pruebas están fijadas en `requirements.txt`.
`requirements-build.txt` contiene dependencias adicionales para empaquetar un
ejecutable de Windows; no se requieren para ejecutar la aplicación desde Python.

## Instalación y ejecución en Windows

Abre PowerShell en la carpeta del proyecto (la que contiene `main.py`) y sigue
estos pasos:

1. Crea un entorno virtual:

   ```powershell
   python -m venv .venv
   ```

2. Activa el entorno virtual:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación por la política de ejecución, puedes usar
   el intérprete del entorno directamente en los pasos siguientes, por ejemplo
   `.\.venv\Scripts\python.exe`.

3. Instala las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Inicia la aplicación de escritorio:

   ```powershell
   python main.py
   ```

Para abrirla en el navegador local:

```powershell
python main.py --web
```

`main.py` también acepta `--host` y `--port`. Por ejemplo, para escuchar en la
red local en el puerto 8550:

```powershell
python main.py --web --host 0.0.0.0 --port 8550
```

En otro dispositivo de la misma red, abre `http://<IP-LOCAL-DE-LA-COMPUTADORA>:8550`.
Puede ser necesario permitir el puerto en el firewall. Este comando no publica la
aplicación en Internet.

## Ejecución de las pruebas

Con el entorno virtual activado y desde la carpeta del proyecto, ejecuta:

```powershell
python -m pytest
```

También puedes ejecutar un archivo de pruebas específico, por ejemplo:

```powershell
python -m pytest tests/test_undo_redo.py
```

La suite cubre las estructuras de datos, las operaciones del motor, los flujos de
paquetes, la gestión de recursos, la visualización de rutas y el historial.

## Estructura del proyecto

```text
Proyecto/
├── .gitignore
├── main.py
├── requirements.txt
├── requirements-build.txt
├── SimuladorLogistico.spec
├── models/
│   ├── __init__.py
│   ├── logistic_engine.py
│   └── structures.py
├── controllers/
│   ├── __init__.py
│   └── app_controller.py
├── views/
│   ├── __init__.py
│   ├── desktop_view.py
│   ├── responsive_components.py
│   └── theme.py
└── tests/
    ├── __init__.py
    ├── test_logistic_engine.py
    ├── test_package_flow.py
    ├── test_resource_management.py
    ├── test_route_visualization.py
    ├── test_structures.py
    └── test_undo_redo.py
```

Archivos principales:

- `main.py`: procesa los argumentos de ejecución y crea el controlador y la vista.
- `models/logistic_engine.py`: define las entidades `Paquete`, `Vehiculo`, `Ruta`
  y `Almacen`, además del motor `LogisticEngine` y las reglas de operación.
- `models/structures.py`: implementa las estructuras de datos utilizadas por el
  modelo.
- `controllers/app_controller.py`: valida y normaliza entradas, expone operaciones
  del motor y entrega datos a la vista.
- `views/desktop_view.py`: crea la página Flet, las secciones y la disposición
  responsiva.
- `views/responsive_components.py`: implementa los componentes de paquetes,
  vehículos, rutas, almacenes e historial.
- `views/theme.py`: define la paleta de colores de la interfaz.
- `tests/`: contiene las pruebas automatizadas del modelo, las estructuras y los
  flujos de interfaz.
- `requirements-build.txt` y `SimuladorLogistico.spec`: configuración auxiliar para
  empaquetado; no son necesarios para la ejecución normal desde Python.

## Arquitectura

El proyecto separa responsabilidades siguiendo una organización **Model–View–
Controller (MVC)**:

- **Model (`models/`)**: `LogisticEngine` administra el estado del simulador y
  aplica las reglas de paquetes, vehículos, rutas y almacenes. Las clases de
  `structures.py` proporcionan las estructuras donde se guardan los datos.
- **View (`views/`)**: `DesktopView` construye la aplicación Flet y los componentes
  de cada módulo. La vista recoge la interacción, muestra el estado y solicita
  refrescos cuando el modelo cambia.
- **Controller (`controllers/`)**: `AppController` sirve de intermediario entre la
  vista y el motor. Valida entradas, construye entidades y ofrece operaciones para
  actualizar o consultar el modelo.

La vista no sustituye las estructuras del modelo por controles de interfaz: obtiene
el estado a través del controlador y refresca los componentes después de las
operaciones.

## Estructuras de datos

Las estructuras se implementan en `models/structures.py` y se utilizan en el motor
de `models/logistic_engine.py` de la siguiente manera:

| Estructura | Uso en el simulador |
| --- | --- |
| `DoublyLinkedList` | Guarda vehículos y almacenes. Cada `Ruta` usa otra lista de este tipo para conservar los paquetes despachados. |
| `CircularDoublyLinkedList` | Guarda las paradas de una ruta y permite avanzar o retroceder cíclicamente. |
| `PriorityQueue` | Mantiene los paquetes pendientes ordenados por prioridad; el motor extrae el de mayor prioridad para despacharlo. |
| `CircularQueue` | Mantiene las rutas en orden FIFO con una capacidad fija de 10. |
| `Stack` | Proporciona el almacenamiento enlazado LIFO para las pilas de acciones. |
| `UndoRedoManager` | Combina dos `Stack` para administrar callbacks de deshacer y rehacer. |

`Node` es el nodo enlazado general utilizado por las listas y la pila.
`PriorityNode` almacena el dato, su prioridad y el enlace siguiente de la cola de
prioridad. No se usa una cola circular de vehículos en el flujo actual: la cola
circular del motor corresponde a las rutas.

## Estado y mejoras futuras

### Implementado

- Interfaz Flet con módulos de paquetes, vehículos, rutas, almacenes e historial.
- Reglas de validación, prioridad, capacidad de transporte y asignación de
  vehículos.
- Recorrido circular de paradas y navegación de almacenes.
- Pruebas automatizadas para las estructuras y los flujos principales.

### Posibles mejoras (no implementadas)

- Persistir el estado entre ejecuciones mediante archivos o una base de datos.
- Incorporar entrega de paquetes, finalización de rutas y liberación asociada de
  recursos.
- Registrar en el historial los cambios de asignación de vehículos y navegación
  de paradas.
- Añadir capturas de pantalla y documentación de uso visual.

## Capturas de pantalla

No hay capturas de pantalla disponibles en el repositorio. Esta sección queda
reservada para agregarlas cuando se generen, por ejemplo, en una carpeta
`docs/imagenes/`.
