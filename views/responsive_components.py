"""Componentes visuales reutilizables para la vista del simulador."""

try:
    import flet as ft
except ImportError:  # pragma: no cover - Flet no está disponible en algunos entornos
    ft = None

from views.theme import PALETTE


def _button(label, secondary=False, **kwargs):
    return ft.Button(
        label,
        style=ft.ButtonStyle(
            bgcolor=(
                PALETTE["surface"] if secondary else PALETTE["primary"]
            ),
            color=(
                PALETTE["text"] if secondary else PALETTE["on_primary"]
            ),
            side=ft.BorderSide(1, PALETTE["border"]) if secondary else None,
            padding=12,
        ),
        width=150,
        **kwargs,
    )


def _panel(content):
    return ft.Container(
        content=content,
        bgcolor=PALETTE["surface"],
        border=ft.Border.all(1, PALETTE["border"]),
        padding=20,
        border_radius=12,
    )


def _set_status_style(message, tone):
    message.style = ft.TextStyle(color=PALETTE[tone])


def _text_field(label, **kwargs):
    return ft.TextField(
        label=label,
        border_color=PALETTE["border"],
        focused_border_color=PALETTE["primary"],
        border_radius=8,
        text_style=ft.TextStyle(color=PALETTE["text"]),
        label_style=ft.TextStyle(color=PALETTE["text_secondary"]),
        **kwargs,
    )


def _dropdown(label, **kwargs):
    return ft.Dropdown(
        label=label,
        border_color=PALETTE["border"],
        focused_border_color=PALETTE["primary"],
        border_radius=8,
        text_style=ft.TextStyle(color=PALETTE["text"]),
        label_style=ft.TextStyle(color=PALETTE["text_secondary"]),
        **kwargs,
    )


def _form_row(fields, columns):
    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=field,
                col=column,
                alignment=ft.Alignment(0, 0) if isinstance(field, ft.Button) else None,
            )
            for field, column in zip(fields, columns)
        ],
        columns=12,
        breakpoints={"xs": 0, "sm": 600, "md": 850, "lg": 1200},
        spacing=12,
        run_spacing=8,
    )
"""-------------------------------------------------------------------------------"""

class ActionHistoryCard:
    """Muestra y ejecuta las operaciones disponibles en el historial."""

    def __init__(self, controller, on_model_change=None, title="Historial"):
        self.controller = controller
        self.on_model_change = on_model_change
        self.title = title
        self._undo_title = None
        self._redo_title = None

    def build(self, page):
        if ft is None:
            return None
        self._page = page
        self._undo_button = _button(
            "Deshacer",
            secondary=True,
            on_click=self._on_undo,
            disabled=True,
        )
        self._redo_button = _button(
            "Rehacer",
            secondary=True,
            on_click=self._on_redo,
            disabled=True,
        )
        self._undo_list = ft.Column(
            controls=[],
            height=220,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        self._redo_list = ft.Column(
            controls=[],
            height=220,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        self._message = ft.Text()
        self._message.style = ft.TextStyle(color=PALETTE["text"])
        self._undo_title = ft.Text("Pila Deshacer", weight="bold")
        self._redo_title = ft.Text("Pila Rehacer", weight="bold")
        self.refresh()
        return ft.Column(
            controls=[
                ft.Text(self.title, size=18, weight="bold"),
                _panel(
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self._undo_button,
                                    self._redo_button,
                                ],
                                wrap=True,
                                spacing=8,
                            ),
                            self._message,
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                self._undo_title,
                                                self._undo_list,
                                            ],
                                            spacing=8,
                                        ),
                                        col={"xs": 12, "md": 6},
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                self._redo_title,
                                                self._redo_list,
                                            ],
                                            spacing=8,
                                        ),
                                        col={"xs": 12, "md": 6},
                                    ),
                                ],
                                columns=12,
                                spacing=12,
                                run_spacing=12,
                            ),
                        ],
                        spacing=12,
                    ),
                )
            ],
            spacing=12,
        )

    def refresh(self):
        state = self.controller.obtener_estado_historial()
        self._undo_button.disabled = state["undo_count"] == 0
        self._redo_button.disabled = state["redo_count"] == 0
        self._undo_title.value = f"Pila Deshacer ({state['undo_count']})"
        self._redo_title.value = f"Pila Rehacer ({state['redo_count']})"
        self._undo_list.controls = [
            ft.Container(
                content=ft.Text(action),
                padding=12,
                border=ft.Border.all(1, PALETTE["border"]),
                border_radius=8,
                bgcolor=PALETTE["surface_subtle"],
            )
            for action in state["undo"]
        ] or [ft.Text("No hay acciones.", color=PALETTE["text_secondary"])]
        self._redo_list.controls = [
            ft.Container(
                content=ft.Text(action),
                padding=12,
                border=ft.Border.all(1, PALETTE["border"]),
                border_radius=8,
                bgcolor=PALETTE["surface_subtle"],
            )
            for action in state["redo"]
        ] or [ft.Text("No hay acciones.", color=PALETTE["text_secondary"])]

    def _complete_history_action(self, action, operation):
        if action is None:
            self._message.value = (
                "No hay acciones para deshacer."
                if operation == "undo"
                else "No hay acciones para rehacer."
            )
            self._message.color = ft.Colors.AMBER_300
            _set_status_style(self._message, "warning")
            self.refresh()
            self._page.update()
            return

        description = self.controller.describir_accion_historial(action)
        self._message.value = (
            f"Acción deshecha: {description}"
            if operation == "undo"
            else f"Acción rehecha: {description}"
        )
        self._message.color = ft.Colors.GREEN_300
        _set_status_style(self._message, "success")
        if self.on_model_change is not None:
            self.on_model_change()
        else:
            self.refresh()
            self._page.update()

    def _on_undo(self, _event):
        try:
            action = self.controller.deshacer()
        except (RuntimeError, ValueError) as error:
            self._message.value = f"No se pudo deshacer: {error}"
            self._message.color = ft.Colors.RED_300
            _set_status_style(self._message, "error")
            self.refresh()
            self._page.update()
            return
        self._complete_history_action(action, "undo")

    def _on_redo(self, _event):
        try:
            action = self.controller.rehacer()
        except (RuntimeError, ValueError) as error:
            self._message.value = f"No se pudo rehacer: {error}"
            self._message.color = ft.Colors.RED_300
            _set_status_style(self._message, "error")
            self.refresh()
            self._page.update()
            return
        self._complete_history_action(action, "redo")

"""---------------------------------------------------------------"""
class PackageManagementCard:
    """Formulario para operar los paquetes a través del controlador."""

    def __init__(self, controller, packages, on_model_change=None):
        self.controller = controller
        self.packages = packages
        self.on_model_change = on_model_change
        self._page = None
        self._package_list = None
        self._selected_package = None
        self._selected_route = None
        self._message = None

    def build(self, page):
        if ft is None:
            return None

        self._page = page
        self._package_code = _text_field("Código")
        self._destination = _text_field("Destino")
        self._weight = _text_field("Peso")
        self._priority = _text_field("Prioridad")
        self._search_code = _text_field("Código para buscar")
        self._selected_package = _dropdown(
            "Paquete seleccionado",
            options=[],
        )
        self._selected_route = _dropdown(
            "Ruta activa para despacho",
            options=[],
        )
        self._package_list = ft.Row(
            controls=[],
            wrap=True,
            spacing=8,
            run_spacing=8,
        )
        self._message = ft.Text()
        self._message.style = ft.TextStyle(color=PALETTE["text"])

        self._refresh_packages()
        return _panel(
            content=ft.Column(
                controls=[
                    ft.Text("Paquetes por prioridad", size=16, weight="bold"),
                    _form_row(
                        [
                            self._package_code,
                            self._destination,
                            self._weight,
                            self._priority,
                        ],
                        [
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                        ],
                    ),
                    _button("Agregar", on_click=self._on_add),
                    _form_row(
                        [
                            self._search_code,
                            _button(
                                "Buscar",
                                secondary=True,
                                on_click=self._on_search,
                            ),
                        ],
                        [
                            {"xs": 12, "md": 7},
                            {"xs": 12, "md": 5},
                        ],
                    ),
                    _form_row(
                        [
                            self._selected_package,
                            _button(
                                "Eliminar",
                                secondary=True,
                                on_click=self._on_delete,
                            ),
                        ],
                        [
                            {"xs": 12, "md": 7},
                            {"xs": 12, "md": 5},
                        ],
                    ),
                    _form_row(
                        [
                            self._selected_route,
                            _button(
                                "Despachar",
                                on_click=self._on_dispatch,
                            ),
                        ],
                        [
                            {"xs": 12, "md": 7},
                            {"xs": 12, "md": 5},
                        ],
                    ),
                    self._message,
                    ft.Text("Cola ordenada: prioridad más alta primero"),
                    self._package_list,
                ],
                spacing=14,
            ),
        )

    def _refresh_packages(self, selected_code=None):
        state = self.controller.obtener_estado()
        self.packages = state["paquetes"]
        active_routes = [
            route for route in state["rutas"]
            if route.vehiculo is not None
            and isinstance(route.vehiculo.estado, str)
            and route.vehiculo.estado.strip().casefold() == "en ruta"
        ]
        route_options = [
            ft.DropdownOption(
                key=route.codigo,
                text=f"{route.codigo} — {route.origen} → {route.destino}",
            )
            for route in active_routes
        ]
        selected_route_code = self._selected_route.value
        active_route_codes = {option.key for option in route_options}
        self._selected_route.options = route_options
        self._selected_route.value = (
            selected_route_code
            if selected_route_code in active_route_codes
            else route_options[0].key if route_options
            else None
        )

        options = [
            ft.DropdownOption(
                key=package.codigo,
                text=(
                    f"{package.codigo} — {package.destino} | "
                    f"{package.peso:g} kg | prioridad {package.prioridad}"
                ),
            )
            for package in self.packages
        ]
        current_code = selected_code or self._selected_package.value
        valid_codes = {option.key for option in options}
        self._selected_package.options = options
        self._selected_package.value = (
            current_code if current_code in valid_codes
            else options[0].key if options
            else None
        )
        self._package_list.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                f"#{index}",
                                weight="bold",
                                color=PALETTE["primary"],
                            ),
                            bgcolor=PALETTE["primary_soft"],
                            padding=8,
                            border_radius=8,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    f"{package.codigo} — {package.destino}",
                                    weight="bold",
                                ),
                                ft.Text(
                                    f"{package.peso:g} kg | "
                                    f"Prioridad {package.prioridad}"
                                ),
                            ],
                            spacing=4,
                            tight=True,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=250,
                padding=12,
                border=ft.Border.all(1, PALETTE["border"]),
                border_radius=10,
                bgcolor=PALETTE["surface"],
            )
            for index, package in enumerate(self.packages, start=1)
        ] or [ft.Text("Sin paquetes pendientes")]

    def _finish_operation(
        self,
        message,
        is_error=False,
        selected_code=None,
        model_changed=False,
    ):
        self._refresh_packages(selected_code)
        self._message.value = message
        self._message.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700
        _set_status_style(
            self._message,
            "error" if is_error else "success",
        )
        if model_changed and self.on_model_change is not None:
            self.on_model_change()
        else:
            self._page.update()

    def _on_add(self, _event):
        try:
            package = self.controller.agregar_paquete(
                self._package_code.value,
                self._destination.value,
                self._weight.value,
                self._priority.value,
            )
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        self._package_code.value = ""
        self._destination.value = ""
        self._weight.value = ""
        self._priority.value = ""
        self._finish_operation(
            f"Paquete {package.codigo} agregado correctamente.",
            selected_code=package.codigo,
            model_changed=True,
        )

    def _on_search(self, _event):
        try:
            package = self.controller.buscar_paquete(self._search_code.value)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        if package is None:
            self._finish_operation(
                f"No se encontró el paquete «{self._search_code.value}».",
                is_error=True,
            )
            return
        self._finish_operation(
            f"Paquete {package.codigo} encontrado.",
            selected_code=package.codigo,
        )

    def _on_delete(self, _event):
        codigo = self._selected_package.value
        if codigo is None:
            self._finish_operation("Selecciona un paquete para eliminar.", is_error=True)
            return

        package = self.controller.eliminar_paquete(codigo)
        if package is None:
            self._finish_operation(
                f"No se encontró el paquete «{codigo}».",
                is_error=True,
            )
            return
        self._finish_operation(
            f"Paquete {package.codigo} eliminado correctamente.",
            model_changed=True,
        )

    def _on_dispatch(self, _event):
        if self._selected_route.value is None:
            self._finish_operation(
                "Selecciona una ruta activa antes de despachar.",
                is_error=True,
            )
            return
        try:
            package = self.controller.despachar_paquete(
                self._selected_route.value
            )
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        if package is None:
            self._finish_operation("No hay paquetes pendientes para despachar.", is_error=True)
            return
        self._finish_operation(
            f"Paquete {package.codigo} despachado a la ruta "
            f"{self._selected_route.value} (prioridad {package.prioridad}).",
            model_changed=True,
        )

"""---------------------------------------------------------------"""
class DataListCard:
    """Contenedor simple para listar elementos del modelo."""

    def __init__(self, title):
        self.title = title

    def build(self, items):
        if ft is None:
            return None
        entries = [
            ft.Container(
                content=ft.Text(str(item), color=PALETTE["text"]),
                padding=12,
                border=ft.Border.all(1, PALETTE["border"]),
                border_radius=8,
                bgcolor=PALETTE["surface"],
            )
            for item in items
        ] or [ft.Text("Sin elementos", color=PALETTE["text_secondary"])]
        return _panel(
            content=ft.Column(
                controls=[
                    ft.Text(self.title, size=16, weight="bold"),
                    ft.Column(
                        controls=entries,
                        height=280,
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=12,
            ),
        )

"""---------------------------------------------------------------"""
class _LinkedEntityManagementCard:
    """Interfaz común para administrar entidades almacenadas en listas enlazadas."""

    def __init__(
        self,
        controller,
        items,
        title,
        fields,
        add_method,
        search_method,
        delete_method,
        on_model_change=None,
    ):
        self.controller = controller
        self.items = items
        self.title = title
        self.fields = fields
        self.add_method = add_method
        self.search_method = search_method
        self.delete_method = delete_method
        self.on_model_change = on_model_change
        self._page = None

    def build(self, page):
        if ft is None:
            return None

        self._page = page
        self._fields = {
            name: _text_field(label, value=initial)
            for name, label, initial in self.fields
        }
        self._search_code = _text_field("Código para buscar")
        self._selected_item = _dropdown("Elemento seleccionado", options=[])
        self._item_list = ft.Column(
            controls=[],
            height=140,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        self._message = ft.Text()
        self._message.style = ft.TextStyle(color=PALETTE["text"])
        self._refresh_items()

        return _panel(
            content=ft.Column(
                controls=[
                    ft.Text(self.title, size=16, weight="bold"),
                    _form_row(
                        list(self._fields.values()),
                        [
                            {"xs": 12, "sm": 6}
                            for _ in self._fields
                        ],
                    ),
                    _button("Registrar", on_click=self._on_add),
                    _form_row(
                        [
                            self._search_code,
                            _button(
                                "Buscar",
                                secondary=True,
                                on_click=self._on_search,
                            ),
                        ],
                        [
                            {"xs": 12, "md": 7},
                            {"xs": 12, "md": 5},
                        ],
                    ),
                    _form_row(
                        [
                            self._selected_item,
                            _button(
                                "Eliminar",
                                secondary=True,
                                on_click=self._on_delete,
                            ),
                        ],
                        [
                            {"xs": 12, "sm": 8},
                            {"xs": 12, "sm": 4},
                        ],
                    ),
                    self._message,
                    self._item_list,
                ],
                spacing=14,
            ),
        )

    def _refresh_items(self, selected_code=None):
        self.items = self.controller.obtener_estado()[self.state_key]
        options = [
            ft.DropdownOption(
                key=item.codigo,
                text=self._item_label(item),
            )
            for item in self.items
        ]
        current_code = selected_code or self._selected_item.value
        valid_codes = {option.key for option in options}
        self._selected_item.options = options
        self._selected_item.value = (
            current_code if current_code in valid_codes
            else options[0].key if options
            else None
        )
        self._item_list.controls = [
            ft.Container(
                content=ft.Text(
                    self._item_display(item),
                    color=PALETTE["text"],
                ),
                padding=12,
                border=ft.Border.all(1, self._item_border_color(item)),
                border_radius=8,
                bgcolor=PALETTE["surface"],
            )
            for item in self.items
        ] or [
            ft.Text(
                f"No hay {self.empty_label}.",
                color=PALETTE["text_secondary"],
            )
        ]

    def _item_label(self, item):
        return str(item)

    def _item_display(self, item):
        return self._item_label(item)

    def _item_border_color(self, _item):
        return PALETTE["border"]

    def _finish_operation(
        self,
        message,
        is_error=False,
        selected_code=None,
        model_changed=False,
    ):
        self._refresh_items(selected_code)
        self._message.value = message
        self._message.color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700
        _set_status_style(
            self._message,
            "error" if is_error else "success",
        )
        if model_changed and self.on_model_change is not None:
            self.on_model_change()
        else:
            self._page.update()

    def _on_add(self, _event):
        values = [field.value for field in self._fields.values()]
        try:
            item = getattr(self.controller, self.add_method)(*values)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        for name, field in self._fields.items():
            field.value = self.field_defaults.get(name, "")
        self._finish_operation(
            f"{self.item_label} {item.codigo} registrado correctamente.",
            selected_code=item.codigo,
            model_changed=True,
        )

    def _on_search(self, _event):
        codigo = self._search_code.value
        try:
            item = getattr(self.controller, self.search_method)(codigo)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        if item is None:
            self._finish_operation(
                f"No se encontró {self.item_label.lower()} con código «{codigo}».",
                is_error=True,
            )
            return
        self._finish_operation(
            f"{self.item_label} {item.codigo} encontrado.",
            selected_code=item.codigo,
        )

    def _on_delete(self, _event):
        codigo = self._selected_item.value
        if codigo is None:
            self._finish_operation(
                f"Selecciona {self.item_label.lower()} para eliminar.",
                is_error=True,
            )
            return
        try:
            item = getattr(self.controller, self.delete_method)(codigo)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        if item is None:
            self._finish_operation(
                f"No se encontró {self.item_label.lower()} con código «{codigo}».",
                is_error=True,
            )
            return
        self._finish_operation(
            f"{self.item_label} {item.codigo} eliminado correctamente.",
            model_changed=True,
        )

"""---------------------------------------------------------------"""
class VehicleManagementCard(_LinkedEntityManagementCard):
    """Formulario de alta, búsqueda y eliminación de vehículos."""

    state_key = "vehiculos"
    empty_label = "vehículos registrados"
    item_label = "Vehículo"
    field_defaults = {"estado": "Disponible"}

    def __init__(self, controller, vehicles, on_model_change=None):
        super().__init__(
            controller,
            vehicles,
            "Vehículos",
            [
                ("codigo", "Código", ""),
                ("capacidad_maxima", "Capacidad máxima", ""),
                ("estado", "Estado", "Disponible"),
            ],
            "agregar_vehiculo",
            "buscar_vehiculo",
            "eliminar_vehiculo",
            on_model_change,
        )

    def _item_display(self, item):
        return (
            f"Vehiculo(codigo={item.codigo}, "
            f"capacidad_maxima={item.capacidad_maxima}, "
            f"estado={item.estado})\n"
            f"Capacidad máxima: {item.capacidad_maxima:g} kg\n"
            f"Estado: {item.estado}"
        )

    def _item_border_color(self, item):
        if str(item.estado).strip().casefold() == "disponible":
            return PALETTE["success"]
        return PALETTE["warning"]

"""---------------------------------------------------------------"""
class WarehouseManagementCard(_LinkedEntityManagementCard):
    """Formulario de alta, búsqueda y eliminación de almacenes."""

    state_key = "almacenes"
    empty_label = "almacenes registrados"
    item_label = "Almacén"
    field_defaults = {}

    def __init__(self, controller, warehouses, on_model_change=None):
        super().__init__(
            controller,
            warehouses,
            "Almacenes",
            [
                ("codigo", "Código", ""),
                ("nombre", "Nombre", ""),
                ("ubicacion", "Ubicación", ""),
            ],
            "agregar_almacen",
            "buscar_almacen",
            "eliminar_almacen",
            on_model_change,
        )
        self._current_summary = None
        self._previous_button = None
        self._next_button = None

    def _item_display(self, item):
        return (
            f"Código: {item.codigo}\n"
            f"Nombre: {item.nombre}\n"
            f"Ubicación: {item.ubicacion}"
        )

    def build(self, page):
        if ft is None:
            return super().build(page)

        self._current_summary = ft.Text()
        self._previous_button = _button(
            "Anterior",
            secondary=True,
            on_click=self._on_previous,
        )
        self._next_button = _button(
            "Siguiente",
            secondary=True,
            on_click=self._on_next,
        )
        card = super().build(page)
        card.content.controls.insert(-2, self._current_summary)
        card.content.controls.insert(
            -2,
            ft.Row(
                controls=[self._previous_button, self._next_button],
                wrap=True,
            ),
        )
        self._selected_item.on_select = self._on_selection_changed
        self._refresh_items()
        return card

    def _refresh_items(self, selected_code=None):
        super()._refresh_items(selected_code)
        if self._current_summary is None:
            return

        if selected_code is not None:
            self.controller.seleccionar_almacen(self._selected_item.value)

        state = self.controller.obtener_estado_navegacion_almacenes()
        almacen = state["almacen"]
        self._selected_item.value = almacen.codigo if almacen is not None else None
        self._current_summary.value = (
            f"Almacén actual: {almacen.codigo} — {almacen.nombre} | "
            f"{almacen.ubicacion}"
            if almacen is not None
            else "No hay almacenes registrados."
        )
        self._previous_button.disabled = not state["tiene_anterior"]
        self._next_button.disabled = not state["tiene_siguiente"]

    def _on_selection_changed(self, event):
        selected_code = event.control.value
        if selected_code is None:
            return
        self._refresh_items(selected_code)
        self._page.update()

    def _on_previous(self, _event):
        self.controller.navegar_almacen_anterior()
        self._refresh_items()
        self._page.update()

    def _on_next(self, _event):
        self.controller.navegar_almacen_siguiente()
        self._refresh_items()
        self._page.update()

"""---------------------------------------------------------------"""
class CircularRouteCard:
    """Permite administrar rutas y visualizar su recorrido circular."""

    def __init__(self, controller, routes, on_model_change=None):
        self.controller = controller
        self.on_model_change = on_model_change
        self.routes = routes
        self.selected_route_code = routes[0].codigo if routes else None
        self._page = None
        self._stop_row = None
        self._route_summary = None
        self._vehicle_summary = None
        self._position_summary = None
        self._package_summary = None
        self._loop_summary = None
        self._message = None

    def build(self, page):
        if ft is None:
            return None

        self._page = page
        self._route_code = _text_field("Código de ruta")
        self._origin = _text_field("Origen")
        self._destination = _text_field("Destino")
        self._stops = _text_field(
            "Paradas (separadas por comas)",
            hint_text="Ejemplo: Centro, Norte, Sur",
        )
        self._route_selector = _dropdown(
            "Ruta",
            options=[],
            on_select=self._on_route_selected,
        )
        self._search_code = _text_field("Buscar ruta por código")
        self._vehicle_selector = _dropdown(
            "Vehículo registrado",
            options=[],
        )
        self._message = ft.Text()
        self._message.style = ft.TextStyle(color=PALETTE["text"])
        self._route_summary = ft.Text()
        self._vehicle_summary = ft.Text()
        self._position_summary = ft.Text()
        self._package_summary = ft.Column(controls=[], spacing=4)
        self._stop_row = ft.Row(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._loop_summary = ft.Text()
        self._refresh_routes(self.selected_route_code)
        self._refresh_vehicles()
        self._refresh_route()

        return _panel(
            content=ft.Column(
                controls=[
                    ft.Text("Rutas y recorrido circular", size=16, weight="bold"),
                    _form_row(
                        [
                            self._route_code,
                            self._origin,
                            self._destination,
                            self._stops,
                        ],
                        [
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                            {"xs": 12, "sm": 6},
                        ],
                    ),
                    _button("Crear ruta", on_click=self._on_add_route),
                    _form_row(
                        [
                            self._search_code,
                            _button(
                                "Buscar",
                                secondary=True,
                                on_click=self._on_search_route,
                            ),
                        ],
                        [
                            {"xs": 12, "sm": 8},
                            {"xs": 12, "sm": 4},
                        ],
                    ),
                    self._route_selector,
                    _form_row(
                        [self._vehicle_selector],
                        [{"xs": 12}],
                    ),
                    _form_row(
                        [
                            _button(
                                "Asignar",
                                on_click=self._on_assign_vehicle,
                            ),
                            _button(
                                "Desasignar",
                                secondary=True,
                                on_click=self._on_unassign_vehicle,
                            ),
                        ],
                        [
                            {"xs": 12, "md": 6},
                            {"xs": 12, "md": 6},
                        ],
                    ),
                    ft.Row(
                        controls=[
                            _button(
                                "Anterior",
                                icon=ft.Icons.ARROW_BACK,
                                secondary=True,
                                on_click=self._on_previous,
                            ),
                            _button(
                                "Siguiente",
                                icon=ft.Icons.ARROW_FORWARD,
                                secondary=True,
                                on_click=self._on_next,
                            ),
                        ],
                        wrap=True,
                    ),
                    self._message,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self._route_summary,
                                self._vehicle_summary,
                                self._position_summary,
                            ],
                            spacing=6,
                        ),
                        bgcolor=PALETTE["surface_subtle"],
                        border=ft.Border.all(1, PALETTE["border"]),
                        border_radius=8,
                        padding=12,
                    ),
                    ft.Container(
                        content=self._stop_row,
                        bgcolor=PALETTE["surface_subtle"],
                        border=ft.Border.all(1, PALETTE["border"]),
                        border_radius=8,
                        padding=12,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Paquetes asociados", weight="bold"),
                                self._package_summary,
                            ],
                            spacing=8,
                        ),
                        bgcolor=PALETTE["surface_subtle"],
                        border=ft.Border.all(1, PALETTE["border"]),
                        border_radius=8,
                        padding=12,
                    ),
                    ft.Container(
                        content=self._loop_summary,
                        bgcolor=PALETTE["primary_soft"],
                        border_radius=8,
                        padding=10,
                    ),
                ],
                spacing=14,
            ),
        )

    def _refresh_routes(self, selected_code=None):
        self.routes = self.controller.obtener_estado()["rutas"]
        options = [
            ft.DropdownOption(
                key=route.codigo,
                text=f"{route.codigo}: {route.origen} → {route.destino}",
            )
            for route in self.routes
        ]
        route_codes = {option.key for option in options}
        self.selected_route_code = (
            selected_code
            if selected_code in route_codes
            else options[0].key if options
            else None
        )
        self._route_selector.options = options
        self._route_selector.value = self.selected_route_code
        self._refresh_route()

    def _refresh_vehicles(self, selected_code=None):
        vehicles = self.controller.obtener_estado()["vehiculos"]
        self._vehicle_selector.options = [
            ft.DropdownOption(
                key=vehicle.codigo,
                text=(
                    f"{vehicle.codigo} — {vehicle.capacidad_maxima:g} kg "
                    f"({vehicle.estado})"
                ),
            )
            for vehicle in vehicles
        ]
        available_codes = {option.key for option in self._vehicle_selector.options}
        self._vehicle_selector.value = (
            selected_code if selected_code in available_codes else None
        )

    def _finish_operation(
        self,
        message,
        is_error=False,
        selected_code=None,
        model_changed=False,
    ):
        self._refresh_routes(selected_code or self.selected_route_code)
        self._refresh_vehicles()
        self._refresh_route()
        self._message.value = message
        self._message.color = ft.Colors.RED_300 if is_error else ft.Colors.GREEN_300
        _set_status_style(
            self._message,
            "error" if is_error else "success",
        )
        if model_changed and self.on_model_change is not None:
            self.on_model_change()
        else:
            self._page.update()

    def _on_add_route(self, _event):
        stops = self._stops.value.split(",") if self._stops.value else []
        try:
            route = self.controller.agregar_ruta(
                self._route_code.value,
                self._origin.value,
                self._destination.value,
                paradas=stops,
            )
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return

        self._route_code.value = ""
        self._origin.value = ""
        self._destination.value = ""
        self._stops.value = ""
        self._finish_operation(
            f"Ruta {route.codigo} creada correctamente.",
            selected_code=route.codigo,
            model_changed=True,
        )

    def _on_search_route(self, _event):
        codigo = self._search_code.value
        try:
            route = self.controller.buscar_ruta(codigo)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        if route is None:
            self._finish_operation(
                f"No se encontró la ruta «{codigo}».",
                is_error=True,
            )
            return
        self._finish_operation(
            f"Ruta {route.codigo} encontrada.",
            selected_code=route.codigo,
        )

    def _on_assign_vehicle(self, _event):
        if self.selected_route_code is None:
            self._finish_operation("Selecciona una ruta antes de asignar vehículo.", True)
            return
        if self._vehicle_selector.value is None:
            self._finish_operation("Selecciona un vehículo registrado.", True)
            return
        try:
            route = self.controller.asignar_vehiculo_a_ruta(
                self.selected_route_code,
                self._vehicle_selector.value,
            )
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        self._finish_operation(
            f"Vehículo {route.vehiculo.codigo} asignado a la ruta {route.codigo}.",
            selected_code=route.codigo,
            model_changed=True,
        )

    def _on_unassign_vehicle(self, _event):
        if self.selected_route_code is None:
            self._finish_operation("Selecciona una ruta antes de desasignar.", True)
            return
        try:
            route = self.controller.desasignar_vehiculo_de_ruta(
                self.selected_route_code
            )
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        self._finish_operation(
            f"Vehículo desasignado de la ruta {route.codigo}.",
            selected_code=route.codigo,
            model_changed=True,
        )

    def _on_route_selected(self, event):
        self.selected_route_code = event.control.value
        self._refresh_route()
        self._page.update()

    def _on_previous(self, _event):
        if self.selected_route_code is None:
            self._finish_operation("No hay rutas para recorrer.", is_error=True)
            return
        try:
            self.controller.retroceder_parada(self.selected_route_code)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        self._refresh_route()
        self._page.update()

    def _on_next(self, _event):
        if self.selected_route_code is None:
            self._finish_operation("No hay rutas para recorrer.", is_error=True)
            return
        try:
            self.controller.avanzar_parada(self.selected_route_code)
        except ValueError as error:
            self._finish_operation(str(error), is_error=True)
            return
        self._refresh_route()
        self._page.update()

    def _refresh_route(self):
        if self.selected_route_code is None:
            self._route_summary.value = "Ruta: ninguna seleccionada"
            self._vehicle_summary.value = "Vehículo: sin asignar"
            self._position_summary.value = "Estado del recorrido: sin ruta"
            self._stop_row.controls = [ft.Text("No hay rutas registradas.")]
            self._package_summary.controls = [ft.Text("Sin paquetes asociados")]
            self._loop_summary.value = ""
            return

        detail = self.controller.obtener_detalle_ruta(self.selected_route_code)
        stops = detail["paradas"]
        current_index = detail["indice_actual"]
        vehicle = detail["vehiculo"]
        self._vehicle_selector.value = (
            vehicle.codigo if vehicle is not None else None
        )

        self._route_summary.value = (
            f"Ruta: {detail['codigo']} | {detail['origen']} → {detail['destino']}"
        )
        self._vehicle_summary.value = (
            f"Vehículo: {vehicle.codigo} (estado: {vehicle.estado})"
            if vehicle is not None
            else "Vehículo: sin asignar"
        )
        self._package_summary.controls = [
            ft.Text(
                f"{package.codigo} — {package.destino} | "
                f"{package.peso:g} kg | prioridad {package.prioridad}",
                color=PALETTE["text"],
            )
            for package in detail["paquetes"]
        ] or [
            ft.Text("Sin paquetes asociados", color=PALETTE["text_secondary"])
        ]
        self._position_summary.value = (
            f"Estado del recorrido: parada {current_index + 1} de {len(stops)}"
            if current_index is not None
            else "Estado del recorrido: sin paradas"
        )

        visual_controls = []
        for index, stop in enumerate(stops):
            is_current = index == current_index
            visual_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"Parada {index + 1}",
                                weight="bold",
                                color=ft.Colors.GREY_900,
                            ),
                            ft.Text(str(stop), color=ft.Colors.GREY_900),
                            ft.Text(
                                "Posición actual" if is_current else "",
                                color=ft.Colors.GREY_900,
                            ),
                        ],
                        spacing=4,
                    ),
                    bgcolor=ft.Colors.GREEN_100 if is_current else ft.Colors.BLUE_50,
                    border=ft.Border.all(
                        2 if is_current else 1,
                        ft.Colors.GREEN_700 if is_current else PALETTE["border"],
                    ),
                    padding=10,
                    border_radius=8,
                    width=150,
                )
            )
            if index < len(stops) - 1:
                visual_controls.append(ft.Text("⇄", size=20))
        self._stop_row.controls = visual_controls or [ft.Text("La ruta no tiene paradas.")]

        if len(stops) > 1:
            self._loop_summary.value = (
                f"Retorno circular: última parada «{stops[-1]}» "
                f"⇄ primera parada «{stops[0]}»"
            )
        elif stops:
            self._loop_summary.value = f"La parada «{stops[0]}» enlaza consigo misma."
        else:
            self._loop_summary.value = ""
