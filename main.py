"""Punto de entrada de la aplicación del simulador logístico."""

import argparse

from controllers.app_controller import AppController
from views.desktop_view import DesktopView


def main(web=False, host=None, port=0):
    """Inicializa la aplicación con el controlador y la vista."""
    controller = AppController()
    view = DesktopView(controller)
    view.run(web=web, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de centro logístico")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Ejecuta la aplicación en el navegador en lugar de la ventana de escritorio.",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Dirección de enlace para el servidor web de Flet.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Puerto del servidor web (0 selecciona uno disponible).",
    )
    args = parser.parse_args()
    main(web=args.web, host=args.host, port=args.port)
