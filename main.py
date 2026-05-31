import sys
from PyQt6.QtWidgets import QApplication

from app.models.database import init_db
from app.view.app_window import AppWindow
from app.controllers.main_controller import MainController
from app.controllers.auth_controller import AuthController
from app.controllers.dashboard_controller import DashboardController

def main():
    init_db()

    app = QApplication(sys.argv)

    window = AppWindow()

    main_controller = MainController(window)
    auth_controller = AuthController(window)
    dashboard_controller = DashboardController(window)

    window.dashboard_controller = dashboard_controller
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()