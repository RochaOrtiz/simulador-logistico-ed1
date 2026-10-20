import pytest

from controllers.app_controller import AppController
from models.logistic_engine import Almacen, LogisticEngine, Vehiculo
from views.responsive_components import (
    VehicleManagementCard,
    WarehouseManagementCard,
)


class FakePage:
    def __init__(self):
        self.update_count = 0

    def update(self):
        self.update_count += 1


@pytest.mark.parametrize(
    ("capacity", "expected_error"),
    [
        ("", "obligatoria"),
        ("abc", "número"),
        ("0", "número"),
        ("-1", "número"),
        ("inf", "número"),
        (True, "número"),
    ],
)
def test_controlador_rechaza_capacidad_invalida(capacity, expected_error):
    controller = AppController()

    with pytest.raises(ValueError, match=expected_error):
        controller.agregar_vehiculo("V1", capacity)

    assert controller.obtener_estado()["vehiculos"] == []


@pytest.mark.parametrize(
    ("code", "capacity", "state"),
    [
        (" ", "100", "Disponible"),
        ("V1", "100", " "),
    ],
)
def test_controlador_rechaza_campos_obligatorios_del_vehiculo(code, capacity, state):
    with pytest.raises(ValueError, match="obligatorio"):
        AppController().agregar_vehiculo(code, capacity, state)


def test_controlador_agrega_busca_y_elimina_vehiculo_por_codigo():
    controller = AppController()
    vehicle = controller.agregar_vehiculo(" V01 ", "1250", "En ruta")

    assert vehicle.codigo == "V01"
    assert vehicle.capacidad_maxima == 1250
    assert vehicle.estado == "En ruta"
    assert controller.buscar_vehiculo("v01") is vehicle
    assert controller.buscar_vehiculo("inexistente") is None

    with pytest.raises(ValueError, match="Ya existe"):
        controller.agregar_vehiculo("v01", "500")

    assert controller.eliminar_vehiculo(" V01 ") is vehicle
    assert controller.buscar_vehiculo("V01") is None
    assert controller.eliminar_vehiculo("V01") is None


@pytest.mark.parametrize(
    ("code", "name", "location"),
    [
        (" ", "Central", "Norte"),
        ("A1", " ", "Norte"),
        ("A1", "Central", " "),
    ],
)
def test_controlador_rechaza_campos_obligatorios_del_almacen(
    code,
    name,
    location,
):
    with pytest.raises(ValueError, match="obligatorio"):
        AppController().agregar_almacen(code, name, location)


def test_controlador_agrega_busca_y_elimina_almacen_por_codigo():
    controller = AppController()
    warehouse = controller.agregar_almacen(
        " A01 ",
        "Almacén Central",
        "Zona Norte",
    )

    assert warehouse.codigo == "A01"
    assert controller.buscar_almacen("a01") is warehouse
    assert controller.buscar_almacen("inexistente") is None

    with pytest.raises(ValueError, match="Ya existe"):
        controller.agregar_almacen("a01", "Otro", "Sur")

    assert controller.eliminar_almacen(" A01 ") is warehouse
    assert controller.buscar_almacen("A01") is None
    assert controller.eliminar_almacen("A01") is None


def test_motor_rechaza_codigos_duplicados_y_eliminacion_actualiza_lista_enlazada():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo(" V01 ", 100, "Disponible"))
    warehouse = engine.agregar_almacen(Almacen(" A01 ", "Central", "Norte"))

    with pytest.raises(ValueError, match="Ya existe"):
        engine.agregar_vehiculo(Vehiculo("v01", 200))
    with pytest.raises(ValueError, match="Ya existe"):
        engine.agregar_almacen(Almacen("a01", "Otro", "Sur"))

    assert vehicle.codigo == "V01"
    assert warehouse.codigo == "A01"
    assert engine.vehiculos.size == 1
    assert engine.almacenes.size == 1

    assert engine.eliminar_vehiculo("V01") is vehicle
    assert engine.vehiculos.head is None
    assert engine.vehiculos.tail is None
    assert engine.vehiculos.size == 0
    engine.deshacer_ultima_accion()
    assert engine.buscar_vehiculo("V01") is vehicle
    engine.rehacer_ultima_accion()
    assert engine.buscar_vehiculo("V01") is None

    assert engine.eliminar_almacen("A01") is warehouse
    assert engine.almacenes.head is None
    assert engine.almacenes.tail is None
    assert engine.almacenes.size == 0


def test_undo_de_eliminacion_restablece_el_orden_y_enlaces_de_recursos():
    engine = LogisticEngine()
    vehicles = [
        engine.agregar_vehiculo(Vehiculo(code, 100))
        for code in ("V1", "V2", "V3")
    ]
    warehouses = [
        engine.agregar_almacen(Almacen(code, code, "Zona"))
        for code in ("A1", "A2", "A3")
    ]

    engine.eliminar_vehiculo("V2")
    assert engine.listar_vehiculos() == [vehicles[0], vehicles[2]]
    engine.deshacer_ultima_accion()
    assert engine.listar_vehiculos() == vehicles
    assert engine.vehiculos.head.prev is None
    assert engine.vehiculos.head.next.prev is engine.vehiculos.head
    assert engine.vehiculos.tail.prev.next is engine.vehiculos.tail
    assert engine.vehiculos.tail.next is None

    engine.eliminar_almacen("A2")
    assert engine.listar_almacenes() == [warehouses[0], warehouses[2]]
    engine.deshacer_ultima_accion()
    assert engine.listar_almacenes() == warehouses
    assert engine.almacenes.head.prev is None
    assert engine.almacenes.head.next.prev is engine.almacenes.head
    assert engine.almacenes.tail.prev.next is engine.almacenes.tail
    assert engine.almacenes.tail.next is None


def test_tarjeta_vehiculos_conecta_operaciones_y_actualiza_estado():
    controller = AppController()
    page = FakePage()
    card = VehicleManagementCard(controller, [])
    card.build(page)

    card._fields["codigo"].value = "V1"
    card._fields["capacidad_maxima"].value = "1200"
    card._fields["estado"].value = "En ruta"
    card._on_add(None)

    assert card._selected_item.value == "V1"
    assert "estado=En ruta" in card._item_list.controls[0].content.value
    assert "capacidad_maxima=1200.0" in card._item_list.controls[0].content.value

    card._search_code.value = "v1"
    card._on_search(None)
    assert card._message.value == "Vehículo V1 encontrado."

    card._on_delete(None)
    assert controller.buscar_vehiculo("V1") is None
    assert card._item_list.controls[0].value == "No hay vehículos registrados."
    assert card._message.value == "Vehículo V1 eliminado correctamente."
    assert page.update_count == 3


def test_tarjeta_almacenes_conecta_operaciones_y_valida_campos():
    controller = AppController()
    page = FakePage()
    card = WarehouseManagementCard(controller, [])
    card.build(page)

    card._fields["codigo"].value = "A1"
    card._fields["nombre"].value = "Central"
    card._fields["ubicacion"].value = "Zona Norte"
    card._on_add(None)

    assert card._selected_item.value == "A1"
    assert (
        card._item_list.controls[0].content.value
        == "Código: A1\nNombre: Central\nUbicación: Zona Norte"
    )

    card._search_code.value = "a1"
    card._on_search(None)
    assert card._message.value == "Almacén A1 encontrado."

    card._on_delete(None)
    assert controller.buscar_almacen("A1") is None
    assert card._message.value == "Almacén A1 eliminado correctamente."
    assert page.update_count == 3

    card._fields["codigo"].value = ""
    card._fields["nombre"].value = "Otra"
    card._fields["ubicacion"].value = "Sur"
    card._on_add(None)
    assert card._message.value == "El campo código del almacén es obligatorio."


def test_navegacion_almacenes_vacia_y_con_un_solo_elemento():
    controller = AppController()
    empty_state = controller.obtener_estado_navegacion_almacenes()

    assert empty_state == {
        "almacen": None,
        "tiene_anterior": False,
        "tiene_siguiente": False,
    }
    assert controller.navegar_almacen_anterior() is None
    assert controller.navegar_almacen_siguiente() is None

    warehouse = controller.agregar_almacen("A1", "Central", "Norte")
    state = controller.obtener_estado_navegacion_almacenes()
    assert state == {
        "almacen": warehouse,
        "tiene_anterior": False,
        "tiene_siguiente": False,
    }
    assert controller.navegar_almacen_anterior() is warehouse
    assert controller.navegar_almacen_siguiente() is warehouse


def test_navegacion_almacenes_avanza_retrocede_y_respeta_limites():
    controller = AppController()
    warehouses = [
        controller.agregar_almacen(code, code, "Zona")
        for code in ("A1", "A2", "A3")
    ]

    assert controller.obtener_estado_navegacion_almacenes() == {
        "almacen": warehouses[0],
        "tiene_anterior": False,
        "tiene_siguiente": True,
    }
    assert controller.navegar_almacen_anterior() is warehouses[0]
    assert controller.navegar_almacen_siguiente() is warehouses[1]
    assert controller.navegar_almacen_siguiente() is warehouses[2]
    assert controller.navegar_almacen_siguiente() is warehouses[2]
    assert controller.obtener_estado_navegacion_almacenes() == {
        "almacen": warehouses[2],
        "tiene_anterior": True,
        "tiene_siguiente": False,
    }
    assert controller.navegar_almacen_anterior() is warehouses[1]
    assert controller.navegar_almacen_anterior() is warehouses[0]
    assert controller.navegar_almacen_anterior() is warehouses[0]


def test_registrar_almacen_mientras_se_navega_conserva_el_cursor_y_lo_extiende():
    controller = AppController()
    first = controller.agregar_almacen("A1", "Primero", "Norte")
    second = controller.agregar_almacen("A2", "Segundo", "Centro")
    controller.seleccionar_almacen("A1")

    third = controller.agregar_almacen("A3", "Tercero", "Sur")

    assert controller.obtener_estado_navegacion_almacenes()["almacen"] is first
    assert controller.navegar_almacen_siguiente() is second
    assert controller.navegar_almacen_siguiente() is third


@pytest.mark.parametrize(
    ("current_code", "deleted_code", "expected_code", "has_previous", "has_next"),
    [
        ("A1", "A1", "A2", False, True),
        ("A2", "A2", "A3", True, False),
        ("A3", "A3", "A2", True, False),
    ],
)
def test_eliminar_almacen_actual_mueve_el_cursor_al_vecino_disponible(
    current_code,
    deleted_code,
    expected_code,
    has_previous,
    has_next,
):
    controller = AppController()
    warehouses = [
        controller.agregar_almacen(code, code, "Zona")
        for code in ("A1", "A2", "A3")
    ]
    controller.seleccionar_almacen(current_code)

    assert controller.eliminar_almacen(deleted_code) is not None

    state = controller.obtener_estado_navegacion_almacenes()
    assert state["almacen"].codigo == expected_code
    assert state["tiene_anterior"] is has_previous
    assert state["tiene_siguiente"] is has_next
    assert len(controller.obtener_estado()["almacenes"]) == len(warehouses) - 1


def test_eliminar_ultimo_almacen_deja_cursor_vacio_y_undo_lo_reinicializa():
    controller = AppController()
    warehouse = controller.agregar_almacen("A1", "Central", "Norte")

    assert controller.eliminar_almacen("A1") is warehouse
    assert controller.obtener_estado_navegacion_almacenes()["almacen"] is None

    controller.deshacer()
    state = controller.obtener_estado_navegacion_almacenes()
    assert state["almacen"] is warehouse
    assert state["tiene_anterior"] is False
    assert state["tiene_siguiente"] is False


def test_tarjeta_almacenes_muestra_cursor_y_controla_botones_de_navegacion():
    controller = AppController()
    page = FakePage()
    card = WarehouseManagementCard(controller, [])
    card.build(page)

    assert card._current_summary.value == "No hay almacenes registrados."
    assert card._previous_button.disabled is True
    assert card._next_button.disabled is True

    first = controller.agregar_almacen("A1", "Central", "Norte")
    second = controller.agregar_almacen("A2", "Sucursal", "Sur")
    card._refresh_items()
    assert card._current_summary.value == "Almacén actual: A1 — Central | Norte"
    assert card._selected_item.value == first.codigo
    assert card._previous_button.disabled is True
    assert card._next_button.disabled is False

    card._on_next(None)
    assert card._current_summary.value == "Almacén actual: A2 — Sucursal | Sur"
    assert card._selected_item.value == second.codigo
    assert card._previous_button.disabled is False
    assert card._next_button.disabled is True

    card._on_previous(None)
    assert card._current_summary.value == "Almacén actual: A1 — Central | Norte"
    assert card._previous_button.disabled is True


def test_tarjeta_actualiza_cursor_al_registrar_y_eliminar_almacen():
    controller = AppController()
    first = controller.agregar_almacen("A1", "Central", "Norte")
    controller.agregar_almacen("A2", "Sucursal", "Centro")
    controller.seleccionar_almacen(first.codigo)
    page = FakePage()
    card = WarehouseManagementCard(controller, [])
    card.build(page)

    card._fields["codigo"].value = "A3"
    card._fields["nombre"].value = "Depósito"
    card._fields["ubicacion"].value = "Sur"
    card._on_add(None)
    assert card._current_summary.value == "Almacén actual: A3 — Depósito | Sur"

    card._on_delete(None)
    assert card._current_summary.value == "Almacén actual: A2 — Sucursal | Centro"
    assert card._selected_item.value == "A2"
    assert card._next_button.disabled is True
