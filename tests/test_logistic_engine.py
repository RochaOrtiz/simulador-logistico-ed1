import pytest

from models.logistic_engine import Almacen, LogisticEngine, Paquete, Ruta, Vehiculo


def test_agregar_y_despachar_paquetes_por_prioridad():
    """Los paquetes deben salir ordenados por prioridad (menor número = mayor prioridad)."""
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))

    engine.agregar_paquete(Paquete("P1", "Bogotá", 3.5, 3))
    engine.agregar_paquete(Paquete("P2", "Medellín", 1.0, 1))
    engine.agregar_paquete(Paquete("P3", "Cali", 2.0, 2))

    assert engine.obtener_paquete_siguiente().codigo == "P2"
    dispatched = engine.despachar_paquete("R1")
    assert dispatched.codigo == "P2"
    assert route.listar_paquetes() == [dispatched]
    assert engine.obtener_paquete_siguiente().codigo == "P3"


def test_despacho_rechaza_ruta_inexistente_o_inactiva_sin_alterar_cola():
    engine = LogisticEngine()
    package = engine.agregar_paquete(Paquete("P1", "Sur", 2, 1))
    engine.agregar_ruta(Ruta("R1", "Centro", "Sur"))

    with pytest.raises(ValueError, match="No se encontró la ruta"):
        engine.despachar_paquete("R404")
    with pytest.raises(ValueError, match="no tiene vehículo asignado"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == [package]
    assert engine.paquetes.size == 1
    assert engine.buscar_ruta("R1").listar_paquetes() == []


def test_despacho_rechaza_ruta_con_vehiculo_no_registrado_sin_alterar_cola():
    engine = LogisticEngine()
    package = engine.agregar_paquete(Paquete("P1", "Sur", 2, 1))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur"))
    route.vehiculo = Vehiculo("V404", 100, "En ruta")

    with pytest.raises(ValueError, match="vehículo activo válido"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == [package]
    assert engine.paquetes.size == 1
    assert route.listar_paquetes() == []


def test_despacho_asocia_paquete_y_desasignar_no_lo_elimina_de_la_ruta():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    package = engine.agregar_paquete(Paquete("P1", "Sur", 2, 1))

    assert engine.despachar_paquete("R1") is package
    assert engine.listar_paquetes() == []
    assert route.listar_paquetes() == [package]

    engine.desasignar_vehiculo_de_ruta("R1")
    assert route.vehiculo is None
    assert route.listar_paquetes() == [package]
    with pytest.raises(ValueError, match="no tiene vehículo asignado"):
        engine.despachar_paquete("R1")
    assert route.listar_paquetes() == [package]


def test_despacho_acepta_capacidad_exacta_con_carga_previa():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 500))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    first = engine.agregar_paquete(Paquete("P1", "Sur", 300, 1))
    second = engine.agregar_paquete(Paquete("P2", "Sur", 200, 2))

    assert engine.despachar_paquete("R1") is first
    assert route.calcular_peso_total_paquetes() == 300
    assert engine.despachar_paquete("R1") is second
    assert route.calcular_peso_total_paquetes() == 500
    assert route.listar_paquetes() == [first, second]


def test_despacho_rechaza_si_no_cabe_con_carga_previa_sin_cambios():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 500))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    first = engine.agregar_paquete(Paquete("P1", "Sur", 300, 1))
    blocked = engine.agregar_paquete(Paquete("P2", "Sur", 250, 2))

    assert engine.despachar_paquete("R1") is first
    history_before = engine.undo_redo_manager.obtener_estado()
    queue_before = engine.listar_paquetes()
    route_packages_before = route.listar_paquetes()

    with pytest.raises(ValueError, match="no cabe"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == queue_before == [blocked]
    assert route.listar_paquetes() == route_packages_before == [first]
    assert route.calcular_peso_total_paquetes() == 300
    assert engine.undo_redo_manager.obtener_estado() == history_before


def test_despacho_rechaza_paquete_mayor_que_capacidad_total():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 200))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    package = engine.agregar_paquete(Paquete("P1", "Sur", 250, 1))

    with pytest.raises(ValueError, match="no cabe"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == [package]
    assert route.listar_paquetes() == []
    assert route.calcular_peso_total_paquetes() == 0


def test_paquete_prioritario_que_no_cabe_bloquea_paquetes_posteriores_menores():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 200))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    priority_package = engine.agregar_paquete(Paquete("P1", "Sur", 250, 1))
    later_package = engine.agregar_paquete(Paquete("P2", "Sur", 100, 2))
    tied_package = engine.agregar_paquete(Paquete("P3", "Sur", 90, 2))
    queue_before = engine.listar_paquetes()

    with pytest.raises(ValueError, match="no cabe"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == queue_before == [
        priority_package,
        later_package,
        tied_package,
    ]
    assert engine.obtener_paquete_siguiente() is priority_package
    assert route.listar_paquetes() == []


def test_despacho_rechaza_capacidad_de_vehiculo_no_valida_sin_cambios():
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    package = engine.agregar_paquete(Paquete("P1", "Sur", 1, 1))
    vehicle.capacidad_maxima = float("inf")

    with pytest.raises(ValueError, match="capacidad máxima no válida"):
        engine.despachar_paquete("R1")

    assert engine.listar_paquetes() == [package]
    assert route.listar_paquetes() == []


def test_agregar_vehiculo_almacen_y_ruta():
    """Se deben registrar vehículos, almacenes y rutas en sus estructuras correspondientes."""
    engine = LogisticEngine()

    vehiculo = Vehiculo("V1", 1500)
    almacen = Almacen("A1", "Almacén Norte", "Calle 10")
    ruta = Ruta("R1", "Centro", "Norte", vehiculo)

    engine.agregar_vehiculo(vehiculo)
    engine.agregar_almacen(almacen)
    engine.agregar_ruta(ruta)

    assert engine.listar_vehiculos()[0].codigo == "V1"
    assert engine.listar_almacenes()[0].codigo == "A1"
    assert engine.listar_rutas()[0].codigo == "R1"


def test_undo_redo_con_agregar_paquete():
    """Debe poder deshacer y rehacer una operación real sobre el motor."""
    engine = LogisticEngine()
    paquete = Paquete("P1", "Cartagena", 4.0, 2)

    engine.agregar_paquete(paquete)
    assert engine.obtener_paquete_siguiente().codigo == "P1"

    engine.deshacer_ultima_accion()
    assert engine.obtener_paquete_siguiente() is None

    engine.rehacer_ultima_accion()
    assert engine.obtener_paquete_siguiente().codigo == "P1"


def test_undo_redo_con_despachar_paquete():
    """El historial debe restaurar un paquete cuando se deshace un despacho."""
    engine = LogisticEngine()
    vehicle = engine.agregar_vehiculo(Vehiculo("V1", 100))
    route = engine.agregar_ruta(Ruta("R1", "Centro", "Sur", vehicle))
    paquete = Paquete("P1", "Cartagena", 4.0, 2)

    engine.agregar_paquete(paquete)
    engine.despachar_paquete("R1")
    assert engine.obtener_paquete_siguiente() is None
    assert route.listar_paquetes() == [paquete]

    engine.deshacer_ultima_accion()
    assert engine.obtener_paquete_siguiente().codigo == "P1"
    assert route.listar_paquetes() == []

    engine.rehacer_ultima_accion()
    assert engine.obtener_paquete_siguiente() is None
    assert route.listar_paquetes() == [paquete]


def test_ruta_crea_recorrido_circular_con_origen_y_destino():
    """Las rutas existentes incluyen origen y destino como paradas."""
    ruta = Ruta("R1", "Centro", "Norte")

    assert ruta.paradas.recorrer() == ["Centro", "Norte"]
    assert ruta.paradas.head.prev is ruta.paradas.tail
    assert ruta.paradas.tail.next is ruta.paradas.head


def test_ruta_acepta_paradas_personalizadas_y_avanza_en_circulo():
    """Una ruta puede recorrer paradas explícitas y envolver al inicio."""
    ruta = Ruta("R2", "Centro", "Sur", paradas=["Centro", "Norte", "Sur"])

    assert ruta.paradas.recorrer() == ["Centro", "Norte", "Sur"]
    assert ruta.avanzar_parada().data == "Norte"
    assert ruta.avanzar_parada().data == "Sur"
    assert ruta.avanzar_parada().data == "Centro"
    assert ruta.retroceder_parada().data == "Sur"
