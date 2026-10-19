import pytest

from controllers.app_controller import AppController
from models.logistic_engine import Almacen, LogisticEngine, Paquete, Ruta, Vehiculo
from models.structures import UndoRedoManager
from views.desktop_view import DesktopView


class FakePage:
    def __init__(self):
        self.width = 1200
        self.update_count = 0
        self.controls = []

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.update_count += 1


def test_undo_y_redo_ejecutan_callbacks_sin_deshacer_pilas_antes_de_tiempo():
    state = {"value": 1}
    manager = UndoRedoManager()
    manager.registrar_accion({
        "tipo": "test",
        "undo": lambda: state.update(value=0),
        "redo": lambda: state.update(value=1),
    })

    action = manager.undo()
    assert action["tipo"] == "test"
    assert state["value"] == 0
    assert manager.undo_stack.size == 0
    assert manager.redo_stack.size == 1

    manager.redo()
    assert state["value"] == 1
    assert manager.undo_stack.size == 1
    assert manager.redo_stack.size == 0


def test_pilas_vacias_no_alteran_el_estado_y_exponen_habilitacion_correcta():
    controller = AppController()

    assert controller.deshacer() is None
    assert controller.rehacer() is None
    assert controller.obtener_estado_historial() == {
        "undo": [],
        "redo": [],
        "undo_count": 0,
        "redo_count": 0,
    }


def test_fallo_de_callback_conserva_la_accion_en_su_pila():
    manager = UndoRedoManager()
    action = {
        "undo": lambda: False,
        "redo": lambda: False,
    }
    manager.registrar_accion(action)

    with pytest.raises(RuntimeError, match="No se pudo ejecutar"):
        manager.undo()

    assert manager.undo_stack.peek() is action
    assert manager.undo_stack.size == 1
    assert manager.redo_stack.is_empty()


def test_acciones_multiples_se_deshacen_y_rehacen_en_orden_y_actualizan_modelo():
    engine = LogisticEngine()
    package = engine.agregar_paquete(Paquete("P1", "Centro", 2, 1))
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    warehouse = engine.agregar_almacen(Almacen("A1", "Central", "Norte"))

    assert engine.paquetes.size == 1
    assert engine.vehiculos.size == 1
    assert engine.almacenes.size == 1

    undone_warehouse = engine.deshacer_ultima_accion()
    undone_vehicle = engine.deshacer_ultima_accion()
    undone_package = engine.deshacer_ultima_accion()
    assert [undone_warehouse["tipo"], undone_vehicle["tipo"], undone_package["tipo"]] == [
        "agregar_almacen",
        "agregar_vehiculo",
        "agregar_paquete",
    ]
    assert engine.listar_paquetes() == []
    assert engine.vehiculos.size == 0
    assert engine.almacenes.size == 0

    redone_package = engine.rehacer_ultima_accion()
    redone_vehicle = engine.rehacer_ultima_accion()
    redone_warehouse = engine.rehacer_ultima_accion()
    assert [redone_package["tipo"], redone_vehicle["tipo"], redone_warehouse["tipo"]] == [
        "agregar_paquete",
        "agregar_vehiculo",
        "agregar_almacen",
    ]
    assert engine.listar_paquetes() == [package]
    assert engine.listar_vehiculos() == [vehicle]
    assert engine.listar_almacenes() == [warehouse]
    assert engine.paquetes.size == 1
    assert engine.vehiculos.size == 1
    assert engine.almacenes.size == 1


def test_undo_delete_restores_priority_and_tie_order_for_packages():
    engine = LogisticEngine()
    packages = [
        engine.agregar_paquete(Paquete(code, "Centro", 1, priority))
        for code, priority in (
            ("P1", 1),
            ("P2", 2),
            ("P3", 2),
            ("P4", 3),
        )
    ]

    engine.eliminar_paquete("P2")
    assert engine.listar_paquetes() == [packages[0], packages[2], packages[3]]
    engine.deshacer_ultima_accion()
    assert engine.listar_paquetes() == packages
    assert engine.paquetes.size == 4
    engine.rehacer_ultima_accion()
    assert engine.listar_paquetes() == [packages[0], packages[2], packages[3]]
    assert engine.paquetes.size == 3


def test_undo_dispatch_restores_exact_priority_queue_order_including_ties():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    packages = [
        engine.agregar_paquete(Paquete(code, "Centro", 1, 1))
        for code in ("P1", "P2", "P3")
    ]

    assert engine.despachar_paquete("R1") is packages[0]
    assert engine.listar_paquetes() == packages[1:]
    assert route.listar_paquetes() == [packages[0]]
    engine.deshacer_ultima_accion()
    assert engine.listar_paquetes() == packages
    assert route.listar_paquetes() == []
    assert engine.paquetes.size == 3
    engine.rehacer_ultima_accion()
    assert engine.listar_paquetes() == packages[1:]
    assert route.listar_paquetes() == [packages[0]]
    assert engine.paquetes.size == 2


def test_redo_despacho_rechazado_por_capacidad_conserva_estado_e_historial():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 300))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    package = engine.agregar_paquete(Paquete("P1", "Sur", 250, 1))

    engine.despachar_paquete("R1")
    engine.deshacer_ultima_accion()
    vehicle.capacidad_maxima = 200
    redo_action = engine.undo_redo_manager.redo_stack.peek()

    with pytest.raises(ValueError, match="no cabe"):
        engine.rehacer_ultima_accion()

    assert engine.undo_redo_manager.redo_stack.peek() is redo_action
    assert engine.undo_redo_manager.redo_stack.size == 1
    assert engine.listar_paquetes() == [package]
    assert route.listar_paquetes() == []

    vehicle.capacidad_maxima = 300
    engine.rehacer_ultima_accion()
    assert engine.undo_redo_manager.redo_stack.is_empty()
    assert engine.listar_paquetes() == []
    assert route.listar_paquetes() == [package]


def test_redo_despacho_rechazado_si_ruta_inactiva_conserva_accion():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    package = engine.agregar_paquete(Paquete("P1", "Sur", 50, 1))

    engine.despachar_paquete("R1")
    engine.deshacer_ultima_accion()
    engine.desasignar_vehiculo_de_ruta("R1")
    redo_action = engine.undo_redo_manager.redo_stack.peek()

    with pytest.raises(ValueError, match="no tiene vehículo asignado"):
        engine.rehacer_ultima_accion()

    assert engine.undo_redo_manager.redo_stack.peek() is redo_action
    assert engine.undo_redo_manager.redo_stack.size == 1
    assert engine.listar_paquetes() == [package]
    assert route.listar_paquetes() == []

    engine.asignar_vehiculo_a_ruta("R1", "V1")
    engine.rehacer_ultima_accion()
    assert engine.undo_redo_manager.redo_stack.is_empty()
    assert engine.listar_paquetes() == []
    assert route.listar_paquetes() == [package]


def test_undo_redo_de_crear_ruta_asignada_sin_perder_estado_del_vehiculo():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))

    assert vehicle.estado == "En ruta"
    assert route.vehiculo is vehicle

    undone_route = engine.deshacer_ultima_accion()
    assert undone_route["tipo"] == "agregar_ruta"
    assert engine.buscar_ruta("R1") is None
    assert vehicle.estado == "Disponible"

    redone_route = engine.rehacer_ultima_accion()
    assert redone_route["tipo"] == "agregar_ruta"
    assert engine.buscar_ruta("R1") is route
    assert route.vehiculo is vehicle
    assert vehicle.estado == "En ruta"


def test_accion_nueva_despues_de_undo_limpia_redo_y_modifica_modelo():
    engine = LogisticEngine()
    first = engine.agregar_paquete(Paquete("P1", "Centro", 1, 1))
    engine.deshacer_ultima_accion()
    assert engine.buscar_paquete("P1") is None
    assert engine.undo_redo_manager.redo_stack.size == 1

    second = engine.agregar_paquete(Paquete("P2", "Norte", 1, 2))

    assert engine.buscar_paquete("P2") is second
    assert engine.buscar_paquete("P1") is None
    assert engine.undo_redo_manager.redo_stack.is_empty()
    assert engine.undo_redo_manager.undo_stack.size == 1


def test_eliminar_y_restaurar_entidades_conserva_estado_y_tamanos():
    engine = LogisticEngine()
    package = engine.agregar_paquete(Paquete("P1", "Centro", 1, 1))
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 200))
    warehouse = engine.agregar_almacen(Almacen("A1", "Central", "Norte"))

    assert engine.eliminar_almacen("A1") is warehouse
    assert engine.almacenes.size == 0
    engine.deshacer_ultima_accion()
    assert engine.listar_almacenes() == [warehouse]
    assert engine.almacenes.size == 1

    assert engine.eliminar_vehiculo("V1") is vehicle
    assert engine.vehiculos.size == 0
    engine.deshacer_ultima_accion()
    assert engine.listar_vehiculos() == [vehicle]
    assert engine.vehiculos.size == 1

    assert engine.eliminar_paquete("P1") is package
    assert engine.paquetes.size == 0
    engine.deshacer_ultima_accion()
    assert engine.listar_paquetes() == [package]
    assert engine.paquetes.size == 1


def test_historial_flet_habilita_botones_y_sincroniza_todas_las_secciones():
    controller = AppController()
    page = FakePage()
    view = DesktopView(controller)
    view.build(page)
    history = view._history_card

    assert history._undo_button.disabled is True
    assert history._redo_button.disabled is True

    package_card = view._package_card
    package_card._package_code.value = "P1"
    package_card._destination.value = "Centro"
    package_card._weight.value = "1"
    package_card._priority.value = "1"
    package_card._on_add(None)

    assert history._undo_button.disabled is False
    assert history._redo_button.disabled is True
    assert view._package_card._package_list.controls[0].value.startswith("1. P1")
    assert history._undo_list.controls[0].value == "Agregar paquete: P1"

    history._on_undo(None)
    assert controller.obtener_estado()["paquetes"] == []
    assert view._package_card._package_list.controls[0].value == "Sin paquetes pendientes"
    assert history._undo_button.disabled is True
    assert history._redo_button.disabled is False
    assert history._message.value == "Acción deshecha: Agregar paquete: P1"

    history._on_redo(None)
    assert controller.obtener_estado()["paquetes"][0].codigo == "P1"
    assert view._package_card._package_list.controls[0].value.startswith("1. P1")
    assert history._undo_button.disabled is False
    assert history._redo_button.disabled is True
    assert page.update_count >= 4


def test_historial_refresca_paquetes_recursos_y_rutas_en_undo_y_redo():
    controller = AppController()
    page = FakePage()
    view = DesktopView(controller)
    view.build(page)

    package_card = view._package_card
    package_card._package_code.value = "P1"
    package_card._destination.value = "Centro"
    package_card._weight.value = "2"
    package_card._priority.value = "1"
    package_card._on_add(None)

    vehicle_card = view._vehicle_card
    vehicle_card._fields["codigo"].value = "V1"
    vehicle_card._fields["capacidad_maxima"].value = "100"
    vehicle_card._fields["estado"].value = "Disponible"
    vehicle_card._on_add(None)

    warehouse_card = view._warehouse_card
    warehouse_card._fields["codigo"].value = "A1"
    warehouse_card._fields["nombre"].value = "Central"
    warehouse_card._fields["ubicacion"].value = "Norte"
    warehouse_card._on_add(None)

    route_card = view._route_card
    route_card._route_code.value = "R1"
    route_card._origin.value = "Centro"
    route_card._destination.value = "Sur"
    route_card._stops.value = "Centro, Sur"
    route_card._on_add_route(None)

    history = view._history_card
    assert history._undo_button.disabled is False
    assert controller.deshacer()["tipo"] == "agregar_ruta"
    view._refresh_all()
    assert route_card.routes == []

    for _ in range(3):
        history._on_undo(None)
    assert controller.obtener_estado()["paquetes"] == []
    assert controller.obtener_estado()["vehiculos"] == []
    assert controller.obtener_estado()["almacenes"] == []
    assert package_card._package_list.controls[0].value == "Sin paquetes pendientes"
    assert vehicle_card._item_list.controls[0].value == "No hay vehículos registrados."
    assert warehouse_card._item_list.controls[0].value == "No hay almacenes registrados."
    assert route_card.routes == []
    assert history._undo_button.disabled is True

    for _ in range(4):
        history._on_redo(None)
    assert [item.codigo for item in controller.obtener_estado()["paquetes"]] == ["P1"]
    assert [item.codigo for item in controller.obtener_estado()["vehiculos"]] == ["V1"]
    assert [item.codigo for item in controller.obtener_estado()["almacenes"]] == ["A1"]
    assert [item.codigo for item in controller.obtener_estado()["rutas"]] == ["R1"]
    assert package_card._package_list.controls[0].value.startswith("1. P1")
    assert vehicle_card._item_list.controls[0].value.startswith("Vehiculo(codigo=V1")
    assert warehouse_card._item_list.controls[0].value.startswith("Almacen(codigo=A1")
    assert route_card._route_summary.value.startswith("Ruta: R1")
    assert history._redo_button.disabled is True


def test_historial_describe_creacion_de_ruta_y_no_registra_navegacion():
    controller = AppController()
    route = controller.agregar_ruta(
        "R1",
        "Centro",
        "Sur",
        paradas=["Centro", "Sur"],
    )
    before = controller.obtener_estado_historial()["undo_count"]

    controller.avanzar_parada(route.codigo)

    state = controller.obtener_estado_historial()
    assert state["undo_count"] == before
    assert state["undo"][0] == "Crear ruta: R1"

    action = controller.deshacer()
    assert action["tipo"] == "agregar_ruta"
    assert controller.buscar_ruta("R1") is None
    assert controller.rehacer()["tipo"] == "agregar_ruta"
    assert controller.buscar_ruta("R1") is route
