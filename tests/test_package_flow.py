import pytest

from controllers.app_controller import AppController
from models.logistic_engine import LogisticEngine, Paquete
from views.responsive_components import CircularRouteCard, PackageManagementCard


class FakePage:
    def __init__(self):
        self.update_count = 0

    def update(self):
        self.update_count += 1


@pytest.mark.parametrize(
    ("codigo", "destino", "peso", "prioridad"),
    [
        (" ", "Centro", 1, 1),
        ("P1", " ", 1, 1),
        ("P1", "Centro", 0, 1),
        ("P1", "Centro", float("inf"), 1),
        ("P1", "Centro", 1, 0),
        ("P1", "Centro", 1, 1.5),
        ("P1", "Centro", 1, True),
    ],
)
def test_paquete_rechaza_datos_invalidos(codigo, destino, peso, prioridad):
    with pytest.raises(ValueError):
        Paquete(codigo, destino, peso, prioridad)


def test_agregar_paquete_valida_campos_y_codigo_unico():
    controller = AppController()
    package = controller.agregar_paquete(" P01 ", " Centro ", "2.5", "2")

    assert package.codigo == "P01"
    assert package.destino == "Centro"
    assert package.peso == 2.5
    assert controller.buscar_paquete("p01") is package

    with pytest.raises(ValueError, match="Ya existe"):
        controller.agregar_paquete("p01", "Norte", "1", "1")

    assert controller.obtener_estado()["paquetes"] == [package]


@pytest.mark.parametrize(
    ("peso", "prioridad", "message"),
    [
        ("", "1", "peso"),
        ("no-numérico", "1", "peso"),
        (True, "1", "peso"),
        ("1", "", "prioridad"),
        ("1", "1.5", "entero"),
        ("-1", "1", "peso"),
        ("1", "0", "prioridad"),
    ],
)
def test_controlador_rechaza_entradas_invalidas(peso, prioridad, message):
    controller = AppController()

    with pytest.raises(ValueError, match=message):
        controller.agregar_paquete("P01", "Centro", peso, prioridad)

    assert controller.obtener_estado()["paquetes"] == []


def test_buscar_y_eliminar_paquete_por_codigo_actualiza_colas_e_historial():
    engine = LogisticEngine()
    first = engine.agregar_paquete(Paquete("P01", "Centro", 1, 1))
    middle = engine.agregar_paquete(Paquete("P02", "Norte", 1, 2))
    last = engine.agregar_paquete(Paquete("P03", "Sur", 1, 3))

    assert engine.buscar_paquete(" p02 ") is middle
    assert engine.buscar_paquete("inexistente") is None
    assert engine.eliminar_paquete("P02") is middle
    assert engine.listar_paquetes() == [first, last]
    assert engine.paquetes.size == 2

    engine.deshacer_ultima_accion()
    assert engine.listar_paquetes() == [first, middle, last]
    engine.rehacer_ultima_accion()
    assert engine.listar_paquetes() == [first, last]
    assert engine.eliminar_paquete("P02") is None
    assert engine.paquetes.size == 2


def test_tarjeta_paquetes_conecta_agregar_buscar_eliminar_y_despacho():
    controller = AppController()
    controller.agregar_vehiculo("V1", 100)
    route = controller.agregar_ruta("R1", "Centro", "Sur", "V1")
    page = FakePage()
    card = PackageManagementCard(controller, [])
    card.build(page)

    card._package_code.value = "P03"
    card._destination.value = "Sur"
    card._weight.value = "3"
    card._priority.value = "3"
    card._on_add(None)

    card._package_code.value = "P01"
    card._destination.value = "Centro"
    card._weight.value = "1"
    card._priority.value = "1"
    card._on_add(None)

    assert [package.codigo for package in controller.obtener_estado()["paquetes"]] == [
        "P01",
        "P03",
    ]
    assert (
        card._package_list.controls[0]
        .content.controls[1].controls[0].value.startswith("P01")
    )

    card._search_code.value = "p03"
    card._on_search(None)
    assert card._selected_package.value == "P03"
    assert card._message.value == "Paquete P03 encontrado."

    card._on_delete(None)
    assert [package.codigo for package in controller.obtener_estado()["paquetes"]] == [
        "P01",
    ]
    assert card._message.value == "Paquete P03 eliminado correctamente."

    dispatched = controller.agregar_paquete("P02", "Norte", "2", "2")
    assert card._selected_package.value == "P01"
    card._on_dispatch(None)
    assert controller.buscar_paquete(dispatched.codigo) is not None
    assert card._message.value == (
        "Paquete P01 despachado a la ruta R1 (prioridad 1)."
    )
    assert [package.codigo for package in controller.obtener_estado()["paquetes"]] == [
        "P02",
    ]
    assert route.listar_paquetes()[0].codigo == "P01"
    assert page.update_count == 5


def test_tarjeta_informa_cola_vacia_y_errores_de_validacion():
    controller = AppController()
    page = FakePage()
    card = PackageManagementCard(controller, [])
    card.build(page)

    card._on_dispatch(None)
    assert card._message.value == "Selecciona una ruta activa antes de despachar."

    card._package_code.value = "P01"
    card._destination.value = ""
    card._weight.value = "1"
    card._priority.value = "1"
    card._on_add(None)
    assert card._message.value == "El destino del paquete es obligatorio."
    assert controller.obtener_estado()["paquetes"] == []


def test_tarjeta_exige_ruta_activa_y_refresca_opciones_al_asignar_y_desasignar():
    controller = AppController()
    vehicle = controller.agregar_vehiculo("V1", 100)
    route = controller.agregar_ruta("R1", "Centro", "Sur")
    package = controller.agregar_paquete("P1", "Sur", 1, 1)
    page = FakePage()
    card = PackageManagementCard(
        controller,
        controller.obtener_estado()["paquetes"],
    )
    card.build(page)
    route_card = CircularRouteCard(
        controller,
        controller.obtener_estado()["rutas"],
        card._refresh_packages,
    )
    route_card.build(page)

    assert card._selected_route.options == []
    route_card._vehicle_selector.value = vehicle.codigo
    route_card._on_assign_vehicle(None)
    assert card._selected_route.value == "R1"

    card._on_dispatch(None)
    assert route.listar_paquetes() == [package]
    assert controller.obtener_estado()["paquetes"] == []

    route_card._on_unassign_vehicle(None)
    assert card._selected_route.value is None
    assert card._selected_route.options == []
    assert route.listar_paquetes() == [package]


def test_tarjeta_muestra_rechazo_por_capacidad_y_conserva_paquete_pendiente():
    controller = AppController()
    controller.agregar_vehiculo("V1", 5)
    controller.agregar_ruta("R1", "Centro", "Sur", "V1")
    package = controller.agregar_paquete("P1", "Sur", 6, 1)
    page = FakePage()
    card = PackageManagementCard(
        controller,
        controller.obtener_estado()["paquetes"],
    )
    card.build(page)

    card._on_dispatch(None)

    assert "no cabe" in card._message.value
    assert "capacidad suficiente o una decisión del usuario" in card._message.value
    assert controller.obtener_estado()["paquetes"] == [package]
    assert controller.buscar_ruta("R1").listar_paquetes() == []
    assert page.update_count == 1
