import pytest
import flet as ft

from controllers.app_controller import AppController
from models.logistic_engine import Paquete, Ruta, Vehiculo
from views.responsive_components import CircularRouteCard


class FakePage:
    def __init__(self):
        self.update_count = 0

    def update(self):
        self.update_count += 1


class DropdownEvent:
    def __init__(self, value):
        self.control = type("Control", (), {"value": value})()


def test_visualizacion_refleja_ruta_vehiculo_estado_y_parada_actual():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 1200)
    route = controller.agregar_ruta(
        "R1",
        "Centro",
        "Sur",
        vehicle,
        paradas=["Centro", "Norte", "Sur"],
    )
    page = FakePage()
    card = CircularRouteCard(controller, [route])

    visual = card.build(page)

    assert card._route_summary.value == "Ruta: R1 | Centro → Sur"
    assert card._vehicle_summary.value == "Vehículo: V1 (estado: En ruta)"
    assert card._position_summary.value == "Estado del recorrido: parada 1 de 3"
    assert len(card._stop_row.controls) == 5
    assert card._loop_summary.value == (
        "Retorno circular: última parada «Sur» ⇄ primera parada «Centro»"
    )
    assert card._stop_row.controls[0].content.controls[2].value == "Posición actual"
    for stop_index in (0, 2, 4):
        stop_card = card._stop_row.controls[stop_index]
        assert stop_card.content.controls[0].color == ft.Colors.GREY_900
        assert stop_card.content.controls[1].color == ft.Colors.GREY_900
        assert stop_card.content.controls[2].color == ft.Colors.GREY_900
        assert stop_card.bgcolor in (ft.Colors.GREEN_100, ft.Colors.BLUE_50)

    card._on_next(None)

    assert controller.obtener_detalle_ruta("R1")["paradas"] == [
        "Centro",
        "Norte",
        "Sur",
    ]
    assert card._position_summary.value == "Estado del recorrido: parada 2 de 3"
    assert card._stop_row.controls[2].content.controls[2].value == "Posición actual"
    assert page.update_count == 1

    card._on_previous(None)
    assert card._position_summary.value == "Estado del recorrido: parada 1 de 3"
    card._on_previous(None)
    assert card._position_summary.value == "Estado del recorrido: parada 3 de 3"


def test_detalle_de_ruta_conserva_y_muestra_paquetes_despachados():
    controller = AppController()
    controller.agregar_vehiculo("V1", 100)
    route = controller.agregar_ruta("R1", "Centro", "Sur", "V1")
    package = controller.agregar_paquete("P1", "Sur", 2, 1)
    controller.despachar_paquete(route.codigo)
    card = CircularRouteCard(controller, [route])
    card.build(FakePage())

    detail = controller.obtener_detalle_ruta("R1")
    assert detail["paquetes"] == [package]
    assert [control.value for control in card._package_summary.controls] == [
        "P1 — Sur | 2 kg | prioridad 1"
    ]


def test_visualizacion_sin_rutas_muestra_estado_y_permite_crear_primera():
    controller = AppController()
    page = FakePage()
    card = CircularRouteCard(controller, [])
    card.build(page)

    assert card._route_summary.value == "Ruta: ninguna seleccionada"
    assert card._position_summary.value == "Estado del recorrido: sin ruta"
    assert card._stop_row.controls[0].value == "No hay rutas registradas."

    card._route_code.value = "R1"
    card._origin.value = "Centro"
    card._destination.value = "Sur"
    card._stops.value = "Centro, Norte, Sur"
    card._on_add_route(None)

    assert card.selected_route_code == "R1"
    assert card._route_summary.value == "Ruta: R1 | Centro → Sur"
    assert card._position_summary.value == "Estado del recorrido: parada 1 de 3"
    assert card._message.value == "Ruta R1 creada correctamente."
    assert card._message.color == ft.Colors.GREEN_300
    assert page.update_count == 1


def test_visualizacion_permite_seleccionar_otra_ruta():
    controller = AppController()
    first_route = controller.agregar_ruta(
        "R1",
        "Centro",
        "Norte",
        paradas=["Centro", "Norte"],
    )
    second_route = controller.agregar_ruta(
        "R2",
        "Centro",
        "Sur",
        paradas=["Centro", "Oeste", "Sur"],
    )
    card = CircularRouteCard(controller, [first_route, second_route])
    card.build(FakePage())

    card._on_route_selected(DropdownEvent("R2"))

    assert card.selected_route_code == "R2"
    assert card._route_summary.value == "Ruta: R2 | Centro → Sur"
    assert card._position_summary.value == "Estado del recorrido: parada 1 de 3"


def test_visualizacion_maneja_rutas_sin_paradas_y_con_una_parada():
    controller = AppController()
    empty_route = controller.engine.agregar_ruta(
        Ruta(
            "R0",
            "Centro",
            "Centro",
            paradas=[],
        )
    )
    single_stop_route = controller.agregar_ruta(
        "R1",
        "Base",
        "Base",
        paradas=["Base"],
    )
    card = CircularRouteCard(controller, [empty_route, single_stop_route])
    page = FakePage()
    card.build(page)

    assert card._position_summary.value == "Estado del recorrido: sin paradas"
    assert card._stop_row.controls[0].value == "La ruta no tiene paradas."

    card._on_route_selected(DropdownEvent("R1"))
    assert card._position_summary.value == "Estado del recorrido: parada 1 de 1"
    assert card._loop_summary.value == "La parada «Base» enlaza consigo misma."
    assert card._stop_row.controls[0].content.controls[2].value == "Posición actual"


def test_asignacion_rechaza_vehiculo_inexistente_o_no_disponible():
    controller = AppController()
    controller.agregar_ruta("R1", "Centro", "Sur", paradas=["Centro", "Sur"])
    unavailable = controller.agregar_vehiculo("V1", 100, "En ruta")
    card = CircularRouteCard(controller, controller.obtener_estado()["rutas"])
    card.build(FakePage())

    with pytest.raises(ValueError, match="No se encontró el vehículo"):
        controller.asignar_vehiculo_a_ruta("R1", "V404")
    with pytest.raises(ValueError, match="no está disponible"):
        controller.asignar_vehiculo_a_ruta("R1", unavailable.codigo)
    assert controller.obtener_detalle_ruta("R1")["vehiculo"] is None
    assert card._vehicle_summary.value == "Vehículo: sin asignar"


def test_creacion_rechaza_vehiculo_no_registrado_y_no_altera_paquetes():
    controller = AppController()
    package = controller.agregar_paquete("P1", "Sur", 2, 1)
    unregistered_vehicle = Vehiculo("V404", 100)

    with pytest.raises(ValueError, match="no está registrado"):
        controller.agregar_ruta(
            "R1",
            "Centro",
            "Sur",
            unregistered_vehicle,
            paradas=["Centro", "Sur"],
        )

    route = controller.agregar_ruta(
        "R1",
        "Centro",
        "Sur",
        paradas=["Centro", "Sur"],
    )
    controller.avanzar_parada(route.codigo)

    assert controller.buscar_ruta("R1") is route
    assert controller.engine.obtener_paquete_siguiente() is package


def test_asignacion_cambio_de_vehiculo_y_eliminacion_protegida():
    controller = AppController()
    first = controller.agregar_vehiculo("V1", 100)
    second = controller.agregar_vehiculo("V2", 200)
    controller.agregar_ruta("R1", "Centro", "Sur", paradas=["Centro", "Sur"])

    route = controller.asignar_vehiculo_a_ruta("R1", "V1")
    assert route.vehiculo is first
    assert first.estado == "En ruta"
    assert second.estado == "Disponible"
    route = controller.asignar_vehiculo_a_ruta("R1", "V2")
    assert route.vehiculo is second
    assert first.estado == "Disponible"
    assert second.estado == "En ruta"

    with pytest.raises(ValueError, match="asignado a una ruta"):
        controller.eliminar_vehiculo("V2")
    assert controller.buscar_vehiculo("V2") is second
    controller.desasignar_vehiculo_de_ruta("R1")
    assert route.vehiculo is None
    assert second.estado == "Disponible"
    assert controller.eliminar_vehiculo("V2") is second


def test_vehiculo_no_puede_asignarse_a_dos_rutas_activas():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 100)
    first_route = controller.agregar_ruta("R1", "Centro", "Norte")
    second_route = controller.agregar_ruta("R2", "Centro", "Sur")

    controller.asignar_vehiculo_a_ruta("R1", "V1")

    with pytest.raises(ValueError, match="ya está asignado a una ruta"):
        controller.asignar_vehiculo_a_ruta("R2", "V1")

    assert first_route.vehiculo is vehicle
    assert second_route.vehiculo is None
    assert vehicle.estado == "En ruta"
    assert controller.engine.listar_rutas() == [first_route, second_route]


def test_crear_ruta_con_vehiculo_ocupado_falla_sin_cambios_parciales():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 100)
    first_route = controller.agregar_ruta("R1", "Centro", "Norte", vehicle)

    with pytest.raises(ValueError, match="ya está asignado a una ruta"):
        controller.agregar_ruta("R2", "Centro", "Sur", vehicle)

    assert controller.engine.listar_rutas() == [first_route]
    assert vehicle.estado == "En ruta"
    assert first_route.vehiculo is vehicle


def test_cambio_de_vehiculo_fallido_conserva_asignaciones_y_estados():
    controller = AppController()
    first_vehicle = controller.agregar_vehiculo("V1", 100)
    occupied_vehicle = controller.agregar_vehiculo("V2", 100)
    first_route = controller.agregar_ruta("R1", "Centro", "Norte")
    second_route = controller.agregar_ruta("R2", "Centro", "Sur")
    controller.asignar_vehiculo_a_ruta("R1", "V1")
    controller.asignar_vehiculo_a_ruta("R2", "V2")

    with pytest.raises(ValueError, match="ya está asignado a una ruta"):
        controller.asignar_vehiculo_a_ruta("R1", "V2")

    assert first_route.vehiculo is first_vehicle
    assert second_route.vehiculo is occupied_vehicle
    assert first_vehicle.estado == "En ruta"
    assert occupied_vehicle.estado == "En ruta"


def test_tarjeta_asigna_vehiculo_registrado_y_refresca_estado_visible():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 1200)
    route = controller.agregar_ruta(
        "R1",
        "Centro",
        "Sur",
        paradas=["Centro", "Sur"],
    )
    page = FakePage()
    card = CircularRouteCard(controller, [route])
    card.build(page)
    card._vehicle_selector.value = vehicle.codigo
    card._on_assign_vehicle(None)

    assert card._vehicle_summary.value == "Vehículo: V1 (estado: En ruta)"
    assert card._message.value == "Vehículo V1 asignado a la ruta R1."
    assert vehicle.estado == "En ruta"
    assert page.update_count == 1

    card._on_unassign_vehicle(None)
    assert card._vehicle_summary.value == "Vehículo: sin asignar"
    assert card._message.value == "Vehículo desasignado de la ruta R1."
    assert vehicle.estado == "Disponible"
    assert page.update_count == 2


def test_tarjeta_muestra_error_si_se_intenta_asignar_vehiculo_no_disponible():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 1200, "En ruta")
    controller.agregar_ruta("R1", "Centro", "Sur", paradas=["Centro", "Sur"])
    page = FakePage()
    card = CircularRouteCard(controller, controller.obtener_estado()["rutas"])
    card.build(page)
    card._vehicle_selector.value = vehicle.codigo

    card._on_assign_vehicle(None)

    assert card._message.value == "El vehículo «V1» no está disponible."
    assert card._vehicle_summary.value == "Vehículo: sin asignar"
    assert page.update_count == 1


def test_formulario_rechaza_datos_invalidos_y_codigos_duplicados():
    controller = AppController()
    page = FakePage()
    card = CircularRouteCard(controller, [])
    card.build(page)

    card._route_code.value = ""
    card._origin.value = "Centro"
    card._destination.value = "Sur"
    card._stops.value = "Centro, Sur"
    card._on_add_route(None)
    assert card._message.value == "El campo código de la ruta es obligatorio."
    assert card._message.color == ft.Colors.RED_300

    card._route_code.value = "R1"
    card._stops.value = "Centro,,Sur"
    card._on_add_route(None)
    assert card._message.value == "El campo nombre de parada es obligatorio."

    card._stops.value = "Centro, Sur"
    card._on_add_route(None)
    assert card._message.value == "Ruta R1 creada correctamente."

    card._route_code.value = "r1"
    card._origin.value = "Centro"
    card._destination.value = "Sur"
    card._stops.value = "Centro, Sur"
    card._on_add_route(None)
    assert card._message.value == "Ya existe una ruta con el código «r1»."
    assert len(controller.obtener_estado()["rutas"]) == 1
    assert page.update_count == 4


def test_cola_circular_llena_rechaza_y_muestra_mensaje_en_formulario():
    controller = AppController()
    for index in range(controller.engine.rutas.capacity):
        controller.agregar_ruta(
            f"R{index}",
            "Centro",
            "Sur",
            paradas=["Centro", "Sur"],
        )

    page = FakePage()
    card = CircularRouteCard(controller, controller.obtener_estado()["rutas"])
    card.build(page)
    card._route_code.value = "R-extra"
    card._origin.value = "Centro"
    card._destination.value = "Sur"
    card._stops.value = "Centro, Sur"
    card._on_add_route(None)

    assert card._message.value == "La cola de rutas está llena (capacidad: 10)."
    assert len(controller.obtener_estado()["rutas"]) == 10
    assert controller.engine.rutas.is_full()
    assert page.update_count == 1
