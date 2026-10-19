"""Vista principal del simulador con Flet."""

try:
    import flet as ft
except ImportError:  # pragma: no cover
    ft = None

from views.responsive_components import (
    ActionHistoryCard,
    CircularRouteCard,
    PackageManagementCard,
    VehicleManagementCard,
    WarehouseManagementCard,
)


class DesktopView:
    """Vista principal del simulador para escritorio."""

    def __init__(self, controller):
        self.controller = controller
        self._sections = []
        self._navigation_bar = None
        self._page = None
        self._selected_section = 0
        self._package_card = None
        self._vehicle_card = None
        self._route_card = None
        self._warehouse_card = None
        self._history_card = None

    def build(self, page):
        if ft is None:
            raise RuntimeError("Flet no está disponible en este entorno.")

        estado = self.controller.obtener_estado()
        self._page = page
        self._package_card = PackageManagementCard(
            self.controller,
            estado["paquetes"],
            self._refresh_all,
        )
        self._vehicle_card = VehicleManagementCard(
            self.controller,
            estado["vehiculos"],
            self._refresh_all,
        )
        self._route_card = CircularRouteCard(
            self.controller,
            estado["rutas"],
            self._refresh_all,
        )
        self._warehouse_card = WarehouseManagementCard(
            self.controller,
            estado["almacenes"],
            self._refresh_all,
        )
        self._history_card = ActionHistoryCard(
            self.controller,
            self._refresh_all,
        )
        section_contents = [
            self._package_card.build(page),
            self._vehicle_card.build(page),
            self._route_card.build(page),
            self._warehouse_card.build(page),
            self._history_card.build(page),
        ]
        self._sections = [
            ft.Container(
                content=content,
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
                padding=8,
            )
            for content in section_contents
        ]
        self._navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    label="Paquetes",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.LOCAL_SHIPPING_OUTLINED,
                    label="Vehículos",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.ALT_ROUTE,
                    label="Rutas",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.WAREHOUSE_OUTLINED,
                    label="Almacenes",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    label="Historial",
                ),
            ],
            selected_index=self._selected_section,
            label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED,
            on_change=self._on_navigation_change,
        )

        page.title = "Simulador logístico"
        page.vertical_alignment = "start"
        page.navigation_bar = self._navigation_bar
        page.on_resize = self._on_resize
        page.add(
            ft.Column(
                controls=[
                    ft.ResponsiveRow(
                        controls=self._sections,
                        columns=12,
                        spacing=8,
                        run_spacing=8,
                    )
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )
        self._update_layout()

    def _refresh_all(self):
        if self._page is None:
            return

        self._package_card._refresh_packages()
        self._vehicle_card._refresh_items()
        selected_route = self._route_card.selected_route_code
        self._route_card._refresh_routes(selected_route)
        self._route_card._refresh_vehicles()
        self._warehouse_card._refresh_items()
        self._history_card.refresh()
        self._page.update()

    def _is_mobile_width(self):
        width = self._page.width
        if width is None:
            window = getattr(self._page, "window", None)
            width = getattr(window, "width", None)
        return width is not None and width < 600

    def _update_layout(self):
        if self._page is None:
            return

        mobile_width = self._is_mobile_width()
        self._navigation_bar.visible = mobile_width
        self._navigation_bar.selected_index = self._selected_section
        for index, section in enumerate(self._sections):
            section.visible = not mobile_width or index == self._selected_section
        self._page.update()

    def _on_navigation_change(self, event):
        selected_index = event.control.selected_index
        if selected_index is None:
            return
        self._selected_section = selected_index
        self._update_layout()

    def _on_resize(self, _event):
        self._update_layout()

    def run(self, web=False, host=None, port=0):
        if ft is None:
            raise RuntimeError("Flet no está disponible en este entorno.")
        app_view = ft.AppView.WEB_BROWSER if web else ft.AppView.FLET_APP
        ft.run(self.build, view=app_view, host=host, port=port)
